# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure_provisioning_e2e.iothubservice20180630.iot_hub_gateway_service_ap_is20180630 import (
    IotHubGatewayServiceAPIs20180630,
)

# from .iot_hub_gateway_service_ap_is20180630 import IotHubGatewayServiceAPIs20180630
from msrest.exceptions import HttpOperationError
from azure_provisioning_e2e.iothubservice20180630 import connection_string

# import connection_string
import uuid
import time
import random

max_failure_count = 5

initial_backoff = 10


def run_with_retry(fun, args, kwargs):
    failures_left = max_failure_count
    retry = True
    backoff = initial_backoff + random.randint(1, 10)

    while retry:
        try:
            return fun(*args, **kwargs)
        except HttpOperationError as e:
            resp = e.response.json()
            retry = False
            if "Message" in resp:
                if resp["Message"].startswith("ErrorCode:ThrottlingBacklogTimeout"):
                    retry = True
            if retry and failures_left:
                failures_left = failures_left - 1
                print("{} failures left before giving up".format(failures_left))
                print("sleeping for {} seconds".format(backoff))
                time.sleep(backoff)
                backoff = backoff * 2
            else:
                raise e


class Helper:
    def __init__(self, service_connection_string):
        self.cn = connection_string.connection_string_to_sas_token(service_connection_string)
        self.service = IotHubGatewayServiceAPIs20180630("https://" + self.cn["host"]).service

    def headers(self):
        return {
            "Authorization": self.cn["sas"],
            "Request-Id": str(uuid.uuid4()),
            "User-Agent": "azure-iot-device-provisioning-e2e",
        }

    def get_device(self, device_id):
        device = run_with_retry(
            self.service.get_device, (device_id,), {"custom_headers": self.headers()}
        )
        return device

    def get_module(self, device_id, module_id):
        module = run_with_retry(
            self.service.get_module, (device_id, module_id), {"custom_headers": self.headers()}
        )
        return module

    def get_device_connection_string(self, device_id):
        device = run_with_retry(
            self.service.get_device, (device_id,), {"custom_headers": self.headers()}
        )

        primary_key = device.authentication.symmetric_key.primary_key
        return (
            "HostName="
            + self.cn["host"]
            + ";DeviceId="
            + device_id
            + ";SharedAccessKey="
            + primary_key
        )

    def get_module_connection_string(self, device_id, module_id):
        module = run_with_retry(
            self.service.get_module, (device_id, module_id), {"custom_headers": self.headers()}
        )

        primary_key = module.authentication.symmetric_key.primary_key
        return (
            "HostName="
            + self.cn["host"]
            + ";DeviceId="
            + device_id
            + ";ModuleId="
            + module_id
            + ";SharedAccessKey="
            + primary_key
        )

    # def apply_configuration(self, device_id, modules_content):
    #     content = ConfigurationContent(modules_content=modules_content)
    #
    #     run_with_retry(
    #         self.service.apply_configuration_on_edge_device,
    #         (device_id, content),
    #         {"custom_headers": self.headers()},
    #     )
    #
    # def create_device(self, device_id, is_edge=False):
    #     print("creating device {}".format(device_id))
    #     try:
    #         device = run_with_retry(
    #             self.service.get_device,
    #             (device_id,),
    #             {"custom_headers": self.headers()},
    #         )
    #         print("using existing device")
    #     except HttpOperationError:
    #         device = Device(device_id)
    #
    #     if is_edge:
    #         device.capabilities = DeviceCapabilities(True)
    #
    #     run_with_retry(
    #         self.service.create_or_update_device,
    #         (device_id, device),
    #         {"custom_headers": self.headers()},
    #     )
    #
    # def create_device_module(self, device_id, module_id):
    #     print("creating module {}/{}".format(device_id, module_id))
    #     try:
    #         module = run_with_retry(
    #             self.service.get_module,
    #             (device_id, module_id),
    #             {"custom_headers": self.headers()},
    #         )
    #         print("using existing device module")
    #     except HttpOperationError:
    #         module = Module(module_id, None, device_id)
    #
    #     run_with_retry(
    #         self.service.create_or_update_module,
    #         (device_id, module_id, module),
    #         {"custom_headers": self.headers()},
    #     )

    def try_delete_device(self, device_id):
        try:
            run_with_retry(
                self.service.delete_device,
                (device_id,),
                {"if_match": "*", "custom_headers": self.headers()},
            )
            return True
        except HttpOperationError:
            return False

    def try_delete_module(self, device_id, module_id):
        try:
            run_with_retry(
                self.service.delete_module,
                (device_id, module_id),
                {"if_match": "*", "custom_headers": self.headers()},
            )
            return True
        except HttpOperationError:
            return False
