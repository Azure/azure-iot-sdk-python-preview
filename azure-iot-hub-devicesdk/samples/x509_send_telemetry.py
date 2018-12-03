# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import time
from azure.iot.hub.devicesdk.device_client import DeviceClient
from azure.iot.hub.devicesdk.auth.authentication_provider_factory import from_x509


# X509 certificate and key paths, and optional passphrase
# The certificate and key files can be created using OpenSSL for example.
# For convenience (not production), the repository contains a script that
# helps generate these files:
# scripts/gen_self_signed_cert_not_for_production.py
cert_file = "../../scripts/certificate.pem"
key_file = "../../scripts/key.pem"
passphrase = "passphrase"

# The "Authentication Provider" will hold references to the device identity and certificate information and provide them to the transport when necessary
x509_auth_provider = from_x509(
    os.getenv("IOTHUB_DEVICE_ID"), os.getenv("IOTHUB_HOSTNAME"), cert_file, key_file, passphrase
)

# For now, the SDK only supports MQTT as a protocol. the client object is used to interact with your Azure IoT hub.
# It needs an Authentication Provider to secure the communication with the hub, using either tokens or x509 certificates
device_client = DeviceClient.from_authentication_provider(x509_auth_provider, "mqtt")


# The connection state callback allows us to detect when the client is connected and disconnected:
def connection_state_callback(status):
    print("connection status: " + status)


# Register the connection state callback with the client...
device_client.on_connection_state = connection_state_callback

# ... and connect the client.
device_client.connect()

# send 5 messages with a 1 second pause between each message
for i in range(0, 5):
    print("sending message #" + str(i))
    device_client.send_event("test_payload message " + str(i))
    time.sleep(1)

# finally, disconnect
device_client.disconnect()
