# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.iot.device.common.pipeline import PipelineOperation


# TODO: revise doc
# TODO: how many of these args do we really need?
class SetEdgeConnectionArgsOperation(PipelineOperation):
    """
    A PipelineOperation object which contains connection arguments which were retrieved from an authorization provider,
    likely by a pipeline stage which handles the SetAuthProviderOperation operation.

    This operation is in the group of IoTHub operations because the arguments which it accepts are very specific to
    IoTHub connections and would not apply to other types of client connections (such as a DPS client).
    """

    def __init__(
        self,
        device_id,
        # hostname,
        module_id,
        gateway_hostname,
        # ca_cert=None,
        # client_cert=None,
        # sas_token=None,
        callback=None,
    ):
        """
        Initializer for SetIoTHubConnectionArgsOperation objects.

        :param str device_id: The device id for the device that we are connecting.
        :param str hostname: The hostname of the iothub service we are connecting to.
        :param str module_id: (optional) If we are connecting as a module, this contains the module id
          for the module we are connecting.
        :param str gateway_hostname: (optional) If we are going through a gateway host, this is the
          hostname for the gateway
        :param str ca_cert: (Optional) The CA certificate to use if the server that we're going to
          connect to uses server-side TLS
        :param X509 client_cert: (Optional) The x509 object containing a client certificate and key used to connect
          to the service
        :param str sas_token: The token string which will be used to authenticate with the service
        :param Function callback: The function that gets called when this operation is complete or has failed.
         The callback function must accept A PipelineOperation object which indicates the specific operation which
         has completed or failed.
        """
        super(SetEdgeConnectionArgsOperation, self).__init__(callback=callback)
        self.device_id = device_id
        self.module_id = module_id
        # self.hostname = hostname
        self.gateway_hostname = gateway_hostname
        # self.ca_cert = ca_cert
        # self.client_cert = client_cert
        # self.sas_token = sas_token


class InvokeMethodOperation(PipelineOperation):
    def __init__(self, method_name, device_id, module_id=None, payload=None):
        pass
