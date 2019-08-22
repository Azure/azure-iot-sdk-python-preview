# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure_provisioning_e2e.service_helper import Helper
from azure.iot.device import ProvisioningDeviceClient
from provisioningserviceclient import ProvisioningServiceClient, IndividualEnrollment
from provisioningserviceclient.protocol.models import AttestationMechanism, ReprovisionPolicy
import pytest
import logging
import os

logging.basicConfig(level=logging.DEBUG)

PROVISIONING_HOST = os.getenv("PROVISIONING_DEVICE_ENDPOINT")
ID_SCOPE = os.getenv("PROVISIONING_DEVICE_IDSCOPE")
service_client = ProvisioningServiceClient.create_from_connection_string(
    os.getenv("PROVISIONING_SERVICE_CONNECTION_STRING")
)
device_registry_helper = Helper(os.getenv("IOTHUB_CONNECTION_STRING"))


@pytest.mark.it(
    "A device gets provisioned to the linked IoTHub with the device_id equal to the registration_id of the individual enrollment that has been created with a symmetric key authentication"
)
def test_device_register_with_no_device_id_for_a_symmetric_key_individual_enrollment():
    try:
        individual_enrollment_record = create_individual_enrollment(
            "e2e-dps-underthewhompingwillow"
        )

        registration_id = individual_enrollment_record.registration_id
        symmetric_key = individual_enrollment_record.attestation.symmetric_key.primary_key

        result_from_register(registration_id, symmetric_key)

        assert_device_provisioned(device_id=registration_id)
    finally:
        service_client.delete_individual_enrollment_by_param(registration_id)


@pytest.mark.it(
    "A device gets provisioned to the linked IoTHub with the user supplied device_id different from the registration_id of the individual enrollment that has been created with a symmetric key authentication"
)
def test_device_register_with_device_id_for_a_symmetric_key_individual_enrollment():

    device_id = "e2edpstommarvoloriddle"
    try:
        individual_enrollment_record = create_individual_enrollment(
            registration_id="e2e-dps-prioriincantatem", device_id=device_id
        )

        registration_id = individual_enrollment_record.registration_id
        symmetric_key = individual_enrollment_record.attestation.symmetric_key.primary_key

        result_from_register(registration_id, symmetric_key)

        assert_device_provisioned(device_id=device_id)
    finally:
        service_client.delete_individual_enrollment_by_param(registration_id)


def create_individual_enrollment(registration_id, device_id=None):
    """
    Create an individual enrollment record using the service client
    :param registration_id: The registration id of the enrollment
    :param device_id:  Optional device id
    :return: And individual enrollment record
    """
    reprovision_policy = ReprovisionPolicy(migrate_device_data=True)
    attestation_mechanism = AttestationMechanism(type="symmetricKey")

    individual_provisioning_model = IndividualEnrollment.create(
        attestation=attestation_mechanism,
        registration_id=registration_id,
        device_id=device_id,
        reprovision_policy=reprovision_policy,
    )

    return service_client.create_or_update(individual_provisioning_model)


def assert_device_provisioned(device_id):
    """
    Assert that the device has been provisioned correctly to iothub.
    :param device_id: The device id
    """
    device = device_registry_helper.get_device(device_id)

    assert device is not None
    assert device.authentication.type == "sas"
    assert device.device_id == device_id


# TODO Eventually should return result after the APi changes
def result_from_register(registration_id, symmetric_key):
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=PROVISIONING_HOST,
        registration_id=registration_id,
        id_scope=ID_SCOPE,
        symmetric_key=symmetric_key,
    )

    provisioning_device_client.register()
