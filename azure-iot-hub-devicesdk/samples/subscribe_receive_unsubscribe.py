# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import logging
from azure.iot.hub.devicesdk import DeviceClient
from azure.iot.hub.devicesdk.auth.authentication_provider_factory import from_connection_string

logging.basicConfig(level=logging.ERROR)

# The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
# The "Authentication Provider" is the object in charge of creating authentication "tokens" for the device client.
auth_provider = from_connection_string(conn_str)
# For now, the SDK only supports MQTT as a protocol. the client object is used to interact with your Azure IoT hub.
# It needs an Authentication Provider to secure the communication with the hub, using either tokens or x509 certificates
device_client = DeviceClient.from_authentication_provider(auth_provider, "mqtt")


# The connection state callback allows us to detect when the client is connected and disconnected:
def connection_state_callback(status):
    print("connection status: " + status)


def on_unsubscribe_completed_handler(feature):
    print(feature + " has been disabled")


def c2d_message_handler(c2d_message):
    print("the data in the message received was ")
    print(c2d_message.data)
    print("custom properties are")
    print(c2d_message.custom_properties)


# Register the connection state callback with the client...
device_client.on_connection_state = connection_state_callback
# Register the unsubscribe completed handler with the client...
device_client.on_unsubscribe_completed = on_unsubscribe_completed_handler

# ... and connect the client.
device_client.connect()

# enable the device to receive c2d messages
device_client.enable_feature("c2d", c2d_message_handler)


while True:
    selection = input("Press D or d: Disable C2D\n" + "Press Q or q: Quit and Exit completely\n")
    if selection == "D" or selection == "d":
        print("Disabling reception of C2D messages")
        # unsubscribe
        device_client.disable_feature("c2d")
        print("Try C2D messages now and see if it works")
        print("It still works , but ideally should not")
    if selection == "Q" or selection == "q":
        print("Quitting")
        break

# finally, disconnect
device_client.disconnect()
