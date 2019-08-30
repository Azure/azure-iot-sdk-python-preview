# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ..azure.iot.digitaltwins.digital_twin_service_client import DigitalTwinServiceClient
from  ..azure.iot.digitaltwins.digital_twin_service_client import DigitalTwin

# deviceId = '<DEVICE_ID_GOES_HERE>';
device_id = "z001"

# interfaceInstanceName = '<INTERFACE_INSTANCE_NAME_GOES_HERE>'; // for the environmental sensor, try "environmentalSensor"
interface_instance_name = "environmentalSensor"

conn_str = os.getenv("IOTHUB_CONNECTION_STRING")

# modelId = '<MODEL_ID_GOES_HERE>'
model_id = "urn:azureiot:Client:SDKInformation:1"

digitalTwinServiceClient = DigitalTwinServiceClient(conn_str)

digital_twin: DigitalTwin = digitalTwinServiceClient.get_digital_twin(device_id)
print("DigitalTwin: ")
print(digital_twin)

digital_twin_interface_instance: DigitalTwin = digitalTwinServiceClient.get_digital_twin_interface_instance(device_id, interface_instance_name)
print("DigitalTwinInterfaceInstance: ")
print(digital_twin_interface_instance)

digital_twin_model = digitalTwinServiceClient.get_model(model_id)
print("Model: ")
print(digital_twin_model)


# patch = "{'additional_properties': {}, 'interfaces': {'environmentalSensor': <pl.service.models.interface_py3.Interface object at 0x00000215065F0108>}, 'version': 6}"
# patch = { \
#   "interfaces": { \
#     "environmentalSensor" \
#       "properties": { \
#         "brightness": \
#           "desired": { \
#             "value": 42 \
#           } \
#         } \
#       } \
#     } \
#   } \
# }
# digital_twin_updated = digitalTwinServiceClient.updateDigitalTwin(digital_twin_id, patch, e_tag)
# print("Model: ")
# print(digital_twin_model)

