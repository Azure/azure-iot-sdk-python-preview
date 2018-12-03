# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .sk_authentication_provider import SymmetricKeyAuthenticationProvider
from .sas_authentication_provider import SharedAccessSignatureAuthenticationProvider
from .iotedge_authentication_provider import IotEdgeAuthenticationProvider
from .x509_authentication_provider import X509AuthenticationProvider


def from_connection_string(connection_string):
    """
    Provides an AuthenticationProvider object that can be created simply with a connection string
    :param connection_string: The connecting string
    :return: a Symmetric Key AuthenticationProvider
    """
    return SymmetricKeyAuthenticationProvider.parse(connection_string)


def from_shared_access_signature(sas_token_str):
    """
    Provides an `AuthenticationProvider` object that can be created simply with a shared access signature
    :param sas_token_str: The shared access signature
    :return: Shared Access Signature AuthenticationProvider
    """
    return SharedAccessSignatureAuthenticationProvider.parse(sas_token_str)


def from_environment():
    """
    Provides an `AuthenticationProvider` object that can be used inside of an Azure IoT Edge module.

    This method does not need any parameters because all of the information necessary to connect
    to Azure IoT Edge comes from the operating system of the module container and also from the
    IoTEdge service.

    :return: iotedge AuthenticationProvider
    """
    return IotEdgeAuthenticationProvider()


def from_x509(device_id, hostname, cert_file, key_file, passphrase=None):
    """
    Provides an `AuthenticationProvider` object that can be used to authenticate a device with an x509 Certificate/Key pair.

    :param cert_string: The PEM string of the certificate
    :param key_string: The PEM string of the key associated with the certificate
    :param passphrase: The passphrase used to encrypt the key file

    :return: X509 AuthenticationProvider
    """
    return X509AuthenticationProvider(device_id, hostname, cert_file, key_file, passphrase)
