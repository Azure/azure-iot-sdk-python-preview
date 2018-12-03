# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .authentication_provider import AuthenticationProvider
import logging

logger = logging.getLogger(__name__)


class X509Credentials:
    """
    A class with references to the certificate, key, and optional passphrase used to authenticate
    a TLS connection using x509 certificates
    """

    def __init__(self, cert_file, key_file, passphrase=None):
        self.cert_file = cert_file
        self.key_file = key_file
        self.passphrase = passphrase


class X509AuthenticationProvider:
    """
    An X509 Authentication Provider. This provider uses the certificate and key
    provided to authenticate a device with an Azure IoT Hub instance.

    X509 Authentication is only supported for device identities connecting directly to an Azure IoT hub.
    """

    def __init__(self, device_id, hostname, cert_file, key_file, passphrase=None):
        """
        Constructor for the X509AuthenticationProvider class.

        :param device_id: The device unique identifier as it exists in the Azure IoT Hub device registry
        :param hostname: The hostname of the Azure IoT hub.
        :param cert_file: The path to the pem file containing the certificate (or certificate chain) used to authenticate the device
        :param key_file: The path to the pem file containing the key associated with the certificate
        :param passhphrase: (optional) The passphrase used to encode the key file
        """

        logger.info("Using X509 authentication for {%s, %s}", hostname, device_id)
        self.hostname = hostname
        self.device_id = device_id
        self.module_id = None  # Modules do not support X509 Authentication (for now)
        self.x509 = X509Credentials(cert_file, key_file, passphrase)

    def disconnect(self):
        """
        Closes any timers or resources used by the authentication provider.
        This is called when the transport is disconnected.
        """
        return
