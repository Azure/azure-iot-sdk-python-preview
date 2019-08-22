# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import os
import logging
import pytest
from scripts.create_x509_chain_pipeline import (
    call_intermediate_cert_creation_from_pipeline,
    call_device_cert_creation_from_pipeline,
    delete_directories_certs_created_from_pipeline,
)


intermediate_common_name = "e2edpshomenum"
intermediate_password = "revelio"
device_common_name = "e2edpslocomotor"
device_password = "mortis"


@pytest.fixture(scope="session", autouse=True)
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
