# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from ..azure.iot.serviceclient import iothub_registry_manager

# deviceId = '<DEVICE_ID_GOES_HERE>';
device_id = "z001"
new_device_id = "zNewDevice001"
new_module_id = "zNewModule001"
device_id_del = "z-del"
device_del_etag = "AAAAAAAAAAE="

conn_str = os.getenv("IOTHUB_CONNECTION_STRING")

serviceClient = iothub_registry_manager.IoTHubRegistryManager(conn_str)

device = serviceClient.get_device(device_id)
print(device)

# new_device = serviceClient.create_device_with_sas(new_device_id, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy', 'enabled')
# print(new_device)
#
# device_updated = serviceClient.update_device_with_sas(new_device.device_id, new_device.etag, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'disabled')
# print(device_updated)

# new_device = serviceClient.create_device_with_x509(new_device_id, "", "", "enabled")
# print(new_device)

# new_device = serviceClient.create_device_with_certificate_authority(new_device_id, "enabled")
# print(new_device)

# new_module = serviceClient.create_module_with_sas(new_device_id, new_module_id, 'IoTEdgeName', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy', 'enabled')
# print(new_module)



# device_statistics = serviceClient.get_device_registry_statistics()
# print(device_statistics)

# service_statistics = serviceClient.get_service_statistics()
# print(service_statistics)

# try:
#     serviceClient.delete_device(device_id_del)
# except HttpOperationError as e:
#     print(e.args)
#     print(e.error)
