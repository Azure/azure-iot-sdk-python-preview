# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pytest
from azure.iot.hub.devicesdk.auth.x509_authentication_provider import (
    X509Credentials,
    X509AuthenticationProvider,
)


def test_x509_auth_provider_constructor_populates_properties_correctly_without_passphrase():
    test_device_id = "device_id"
    test_hostname = "host.name"
    test_cert_file_path = "/cert/path"
    test_key_file_path = "/key/path"

    auth_provider = X509AuthenticationProvider(
        test_device_id, test_hostname, test_cert_file_path, test_key_file_path
    )
    assert isinstance(auth_provider, X509AuthenticationProvider)
    assert auth_provider.device_id == test_device_id
    assert auth_provider.hostname == test_hostname
    assert isinstance(auth_provider.x509, X509Credentials)
    assert auth_provider.x509.cert_file == test_cert_file_path
    assert auth_provider.x509.key_file == test_key_file_path
    assert auth_provider.x509.passphrase is None


def test_x509_auth_provider_constructor_populates_properties_correctly_with_passphrase():
    test_device_id = "device_id"
    test_hostname = "host.name"
    test_cert_file_path = "/cert/path"
    test_key_file_path = "/key/path"
    test_passphrase = "passphrase"

    auth_provider = X509AuthenticationProvider(
        test_device_id, test_hostname, test_cert_file_path, test_key_file_path, test_passphrase
    )
    assert isinstance(auth_provider, X509AuthenticationProvider)
    assert auth_provider.device_id == test_device_id
    assert auth_provider.hostname == test_hostname
    assert isinstance(auth_provider.x509, X509Credentials)
    assert auth_provider.x509.cert_file == test_cert_file_path
    assert auth_provider.x509.key_file == test_key_file_path
    assert auth_provider.x509.passphrase == test_passphrase
