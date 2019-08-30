# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ..common.auth import ConnectionStringAuthentication
from ..service.iot_hub_gateway_service_ap_is20190701_preview import IotHubGatewayServiceAPIs20190701Preview as pl_client
from ..service.models.device import Device
from ..service.models.module import Module
from ..service.models.symmetric_key import SymmetricKey
from ..service.models.x509_thumbprint import X509Thumbprint
from ..service.models.authentication_mechanism import AuthenticationMechanism
# from ..service.iot_hub_gateway_service_ap_is20190701_preview import IotHubGatewayServiceAPIs20190701PreviewConfiguration as pl_config
# from ..service.models.device_capabilities import DeviceCapabilities

class IoTHubRegistryManager(object):
    def __init__(self, connection_string):
        self.auth = ConnectionStringAuthentication(connection_string)
        self.pl = pl_client(self.auth, "https://" + self.auth["HostName"])

    def create_device_with_sas(self, device_id, primary_key, secondary_key, status):
        symmetric_key = SymmetricKey(primary_key=primary_key, secondary_key=secondary_key)

        params = { \
        'device_id': device_id, \
        'status': status, \
        'authentication': AuthenticationMechanism(type='sas', symmetric_key=symmetric_key)
        }
        device = Device(**params)

        return self.pl.service.create_or_update_device(device_id, device)

    def create_device_with_x509(self, device_id, primary_thumbprint, secondary_thumbprint, status):
        x509_thumbprint = X509Thumbprint(primary_thumbprint=primary_thumbprint, secondary_thumbprint=secondary_thumbprint)

        params = { \
        'device_id': device_id, \
        'status': status, \
        'authentication': AuthenticationMechanism(type='selfSigned', x509_thumbprint=x509_thumbprint)
        }
        device = Device(**params)

        return self.pl.service.create_or_update_device(device_id, device)

    def create_device_with_certificate_authority(self, device_id, status):
        params = { \
        'device_id': device_id, \
        'status': status, \
        'authentication': AuthenticationMechanism(type='certificateAuthority')
        }
        device = Device(**params)

        return self.pl.service.create_or_update_device(device_id, device)

    def update_device_with_sas(self, device_id, etag, primary_key, secondary_key, status):
        symmetric_key = SymmetricKey(primary_key=primary_key, secondary_key=secondary_key)

        params = { \
        'device_id': device_id, \
        'status': status, \
        'etag': etag, \
        'authentication': AuthenticationMechanism(type='sas', symmetric_key=symmetric_key)
        }
        device = Device(**params)

        return self.pl.service.create_or_update_device(device_id, device, "*")

    def update_device_with_x509(self, device_id, etag, primary_thumbprint, secondary_thumbprint, status):
        x509_thumbprint = X509Thumbprint(primary_thumbprint=primary_thumbprint, secondary_thumbprint=secondary_thumbprint)

        params = { \
        'device_id': device_id, \
        'status': status, \
        'etag': etag, \
        'authentication': AuthenticationMechanism(type='selfSigned', x509_thumbprint=x509_thumbprint)
        }
        device = Device(**params)

        return self.pl.service.create_or_update_device(device_id, device)

    def update_device_with_certificate_authority(self, device_id, etag, status):
        params = { \
        'device_id': device_id, \
        'status': status, \
        'etag': etag, \
        'authentication': AuthenticationMechanism(type='certificateAuthority')
        }
        device = Device(**params)

        return self.pl.service.create_or_update_device(device_id, device)

    def get_device(self, device_id):
        return self.pl.service.get_device(device_id)

    def get_configuration(self, device_id):
        pass

    def delete_device(self, device_id, if_match=None):
        if if_match is None:
            if_match = '*'

        self.pl.service.delete_device(device_id, if_match)

    def get_service_statistics(self):
        return self.pl.service.get_service_statistics()

    def get_device_registry_statistics(self):
        return self.pl.service.get_device_registry_statistics()

    def create_module_with_sas(self, device_id, module_id, managed_by, primary_key, secondary_key, status):
        symmetric_key = SymmetricKey(primary_key=primary_key, secondary_key=secondary_key)

        params = { \
        'device_id': device_id, \
        'module_id': module_id, \
        'managed_by': managed_by, \
        'status': status, \
        'authentication': AuthenticationMechanism(type='sas', symmetric_key=symmetric_key)
        }
        module = Module(**params)

        return self.pl.service.create_or_update_module(device_id, module_id, module)

    def create_module_with_x509(self, device_id, module_id, managed_by, primary_thumbprint, secondary_thumbprint, status):
        x509_thumbprint = X509Thumbprint(primary_thumbprint=primary_thumbprint, secondary_thumbprint=secondary_thumbprint)

        params = { \
        'device_id': device_id, \
        'module_id': module_id, \
        'managed_by': managed_by, \
        'status': status, \
        'authentication': AuthenticationMechanism(type='selfSigned', x509_thumbprint=x509_thumbprint)
        }
        module = Module(**params)

        return self.pl.service.create_or_update_device(device_id, module_id, module)

    def create_module_with_certificate_authority(self, device_id, module_id, managed_by, status):
        params = { \
        'device_id': device_id, \
        'module_id': module_id, \
        'managed_by': managed_by, \
        'status': status, \
        'authentication': AuthenticationMechanism(type='certificateAuthority')
        }
        module = Module(**params)

        return self.pl.service.create_or_update_device(device_id, module_id, module)

    def update_module_with_sas(self, device_id, module_id, managed_by, etag, primary_key, secondary_key, status):
        symmetric_key = SymmetricKey(primary_key=primary_key, secondary_key=secondary_key)

        params = { \
        'device_id': device_id, \
        'module_id': module_id, \
        'managed_by': managed_by, \
        'status': status, \
        'etag': etag, \
        'authentication': AuthenticationMechanism(type='sas', symmetric_key=symmetric_key)
        }
        module = Module(**params)

        return self.pl.service.create_or_update_device(device_id, module_id, module, "*")

    def update_module_with_x509(self, device_id, module_id, managed_by, etag, primary_thumbprint, secondary_thumbprint, status):
        x509_thumbprint = X509Thumbprint(primary_thumbprint=primary_thumbprint, secondary_thumbprint=secondary_thumbprint)

        params = { \
        'device_id': device_id, \
        'module_id': module_id, \
        'managed_by': managed_by, \
        'status': status, \
        'etag': etag, \
        'authentication': AuthenticationMechanism(type='selfSigned', x509_thumbprint=x509_thumbprint)
        }
        module = Module(**params)

        return self.pl.service.create_or_update_device(device_id, module_id, module)

    def update_module_with_certificate_authority(self, device_id, module_id, managed_by, etag, status):
        params = { \
        'device_id': device_id, \
        'module_id': module_id, \
        'managed_by': managed_by, \
        'status': status, \
        'etag': etag, \
        'authentication': AuthenticationMechanism(type='certificateAuthority')
        }
        module = Module(**params)

        return self.pl.service.create_or_update_device(device_id, module_id, module)

    def get_module(self, device_id, module_id):
        return self.pl.service.get_module(device_id, module_id)

    def delete_module(self, device_id, if_match=None):
        if if_match is None:
            if_match = '*'

        self.pl.service.delete_module(device_id, if_match)

