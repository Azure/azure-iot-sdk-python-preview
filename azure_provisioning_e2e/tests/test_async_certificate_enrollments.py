# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure_provisioning_e2e.iothubservice20180630.service_helper import Helper
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device.common import X509
from provisioningserviceclient import (
    ProvisioningServiceClient,
    IndividualEnrollment,
    EnrollmentGroup,
)
from provisioningserviceclient.protocol.models import AttestationMechanism, ReprovisionPolicy
import pytest
import logging
import os
from scripts.create_x509_chain_pipeline import (
    call_intermediate_cert_creation_from_pipeline,
    call_device_cert_creation_from_pipeline,
    delete_directories_certs_created_from_pipeline,
)


pytestmark = pytest.mark.asyncio
logging.basicConfig(level=logging.DEBUG)


intermediate_common_name = "e2edpshomenum"
intermediate_password = "revelio"
device_common_name = "e2edpslocomotor"
device_password = "mortis"

service_client = ProvisioningServiceClient.create_from_connection_string(
    os.getenv("PROVISIONING_SERVICE_CONNECTION_STRING")
)
device_registry_helper = Helper(os.getenv("IOTHUB_CONNECTION_STRING"))
PROVISIONING_HOST = os.getenv("PROVISIONING_DEVICE_ENDPOINT")
ID_SCOPE = os.getenv("PROVISIONING_DEVICE_IDSCOPE")


@pytest.fixture(scope="module")
def before_all_tests(request):
    logging.info("set up certificates before cert related tests")
    call_intermediate_cert_creation_from_pipeline(
        common_name=intermediate_common_name,
        ca_password=os.getenv("PROVISIONING_ROOT_PASSWORD"),
        intermediate_password=intermediate_password,
    )
    call_device_cert_creation_from_pipeline(
        common_name=device_common_name,
        intermediate_password=intermediate_password,
        device_password=device_password,
        device_count=8,
    )

    def after_module():
        logging.info("tear down certificates after cert related tests")
        delete_directories_certs_created_from_pipeline()

    request.addfinalizer(after_module)


@pytest.mark.it(
    "A device gets provisioned to the linked IoTHub with the user supplied device_id different from the registration_id of the individual enrollment that has been created with a selfsigned X509 authentication"
)
async def test_device_register_with_device_id_for_a_x509_individual_enrollment(before_all_tests):
    device_id = "e2edpsthunderbolt"
    device_index = 1

    try:
        individual_enrollment_record = create_individual_enrollment_with_x509_client_certs(
            device_index=device_index, device_id=device_id
        )
        registration_id = individual_enrollment_record.registration_id

        device_cert_file = "demoCA/newcerts/device_cert" + str(device_index) + ".pem"
        device_key_file = "demoCA/private/device_key" + str(device_index) + ".pem"
        await result_from_register(registration_id, device_cert_file, device_key_file)

        assert_device_provisioned(device_id)
    finally:
        service_client.delete_individual_enrollment_by_param(registration_id)


@pytest.mark.it(
    "A device gets provisioned to the linked IoTHub with device_id equal to the registration_id of the individual enrollment that has been created with a selfsigned X509 authentication"
)
async def test_device_register_with_no_device_id_for_a_x509_individual_enrollment(before_all_tests):

    device_index = 2

    try:
        individual_enrollment_record = create_individual_enrollment_with_x509_client_certs(
            device_index=device_index
        )
        registration_id = individual_enrollment_record.registration_id

        device_cert_file = "demoCA/newcerts/device_cert" + str(device_index) + ".pem"
        device_key_file = "demoCA/private/device_key" + str(device_index) + ".pem"
        await result_from_register(registration_id, device_cert_file, device_key_file)

        assert_device_provisioned(registration_id)
    finally:
        service_client.delete_individual_enrollment_by_param(registration_id)


@pytest.mark.it(
    "A group of devices get provisioned to the linked IoTHub with device_ids equal to the individual registration_ids inside a group enrollment that has been created with intermediate X509 authentication"
)
async def test_group_of_devices_register_with_no_device_id_for_a_x509_intermediate_authentication_group_enrollment(
    before_all_tests
):
    group_id = "e2e-intermediate-durmstrang"
    common_device_id = device_common_name
    device_count_in_group = 3
    reprovision_policy = ReprovisionPolicy(migrate_device_data=True)

    try:
        intermediate_cert_filename = "demoCA/newcerts/intermediate_cert.pem"
        with open(intermediate_cert_filename, "r") as intermediate_pem:
            intermediate_cert_content = intermediate_pem.read()

        attestation_mechanism = AttestationMechanism.create_with_x509_signing_certs(
            intermediate_cert_content
        )
        enrollment_group_provisioning_model = EnrollmentGroup.create(
            group_id, attestation=attestation_mechanism, reprovision_policy=reprovision_policy
        )

        service_client.create_or_update(enrollment_group_provisioning_model)

        count = 0
        common_device_key_input_file = "demoCA/private/device_key"
        common_device_cert_input_file = "demoCA/newcerts/device_cert"
        common_device_inter_cert_chain_file = "demoCA/newcerts/out_inter_device_chain_cert"
        for index in range(3, 3 + device_count_in_group):
            count = count + 1
            device_id = common_device_id + str(index)
            device_key_input_file = common_device_key_input_file + str(index) + ".pem"
            device_cert_input_file = common_device_cert_input_file + str(index) + ".pem"
            device_inter_cert_chain_file = common_device_inter_cert_chain_file + str(index) + ".pem"
            filenames = [device_cert_input_file, intermediate_cert_filename]
            with open(device_inter_cert_chain_file, "w") as outfile:
                for fname in filenames:
                    with open(fname) as infile:
                        outfile.write(infile.read())

            await result_from_register(
                registration_id=device_id,
                device_cert_file=device_inter_cert_chain_file,
                device_key_file=device_key_input_file,
            )

            assert_device_provisioned(device_id)

        # Make sure space is okay. The following line must be outside for loop.
        assert count == device_count_in_group

    finally:
        service_client.delete_enrollment_group_by_param(group_id)


@pytest.mark.skip(
    reason="The enrollment is never properly created on the pipeline and it is always created without any CA reference and eventually the registration fails"
)
@pytest.mark.it(
    "A group of devices get provisioned to the linked IoTHub with device_ids equal to the individual registration_ids inside a group enrollment that has been created with an already uploaded ca cert X509 authentication"
)
async def test_group_of_devices_register_with_no_device_id_for_a_x509_ca_authentication_group_enrollment(
    before_all_tests
):
    group_id = "e2e-ca-ilvermorny"
    common_device_id = device_common_name
    device_count_in_group = 3
    reprovision_policy = ReprovisionPolicy(migrate_device_data=True)

    try:
        DPS_GROUP_CA_CERT = os.getenv("PROVISIONING_ROOT_CERT")
        attestation_mechanism = AttestationMechanism.create_with_x509_ca_refs(
            ref1=DPS_GROUP_CA_CERT
        )
        enrollment_group_provisioning_model = EnrollmentGroup.create(
            group_id, attestation=attestation_mechanism, reprovision_policy=reprovision_policy
        )

        service_client.create_or_update(enrollment_group_provisioning_model)

        count = 0
        intermediate_cert_filename = "demoCA/newcerts/intermediate_cert.pem"
        common_device_key_input_file = "demoCA/private/device_key"
        common_device_cert_input_file = "demoCA/newcerts/device_cert"
        common_device_inter_cert_chain_file = "demoCA/newcerts/out_inter_device_chain_cert"
        for index in range(6, 6 + device_count_in_group):
            count = count + 1
            device_id = common_device_id + str(index)
            device_key_input_file = common_device_key_input_file + str(index) + ".pem"
            device_cert_input_file = common_device_cert_input_file + str(index) + ".pem"
            device_inter_cert_chain_file = common_device_inter_cert_chain_file + str(index) + ".pem"
            filenames = [device_cert_input_file, intermediate_cert_filename]
            with open(device_inter_cert_chain_file, "w") as outfile:
                for fname in filenames:
                    with open(fname) as infile:
                        logging.debug("Filename is {}".format(fname))
                        content = infile.read()
                        logging.debug(content)
                        outfile.write(content)

            await result_from_register(
                registration_id=device_id,
                device_cert_file=device_inter_cert_chain_file,
                device_key_file=device_key_input_file,
            )

            assert_device_provisioned(device_id)

        # Make sure space is okay. The following line must be outside for loop.
        assert count == device_count_in_group
    finally:
        service_client.delete_enrollment_group_by_param(group_id)


def assert_device_provisioned(device_id):
    """
    Assert that the device has been provisioned correctly to iothub.
    :param device_id: The device id
    """
    device = device_registry_helper.get_device(device_id)

    assert device is not None
    assert device.authentication.type == "selfSigned"
    assert device.device_id == device_id


def create_individual_enrollment_with_x509_client_certs(device_index, device_id=None):
    registration_id = device_common_name + str(device_index)
    reprovision_policy = ReprovisionPolicy(migrate_device_data=True)

    device_cert_input_file = "demoCA/newcerts/device_cert" + str(device_index) + ".pem"
    with open(device_cert_input_file, "r") as in_device_cert:
        device_cert_content = in_device_cert.read()

    attestation_mechanism = AttestationMechanism.create_with_x509_client_certs(device_cert_content)

    individual_provisioning_model = IndividualEnrollment.create(
        attestation=attestation_mechanism,
        registration_id=registration_id,
        reprovision_policy=reprovision_policy,
        device_id=device_id,
    )

    return service_client.create_or_update(individual_provisioning_model)


async def result_from_register(registration_id, device_cert_file, device_key_file):
    x509 = X509(cert_file=device_cert_file, key_file=device_key_file, pass_phrase=device_password)

    provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
        provisioning_host=PROVISIONING_HOST,
        registration_id=registration_id,
        id_scope=ID_SCOPE,
        x509=x509,
    )

    await provisioning_device_client.register()