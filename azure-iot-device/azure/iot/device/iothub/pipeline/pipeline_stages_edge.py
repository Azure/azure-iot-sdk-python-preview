# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from azure.iot.device.common.pipeline import PipelineStage, operation_flow, pipeline_thread
from . import pipeline_ops_iothub, pipeline_ops_edge
from . import constant

logger = logging.getLogger(__name__)


# TODO: combine with the one in pipeline_stages_iothub.py
class UseAuthProviderStage(PipelineStage):
    """
    PipelineStage which extracts relevant AuthenticationProvider values for a new
    SetIoTHubConnectionArgsOperation.

    All other operations are passed down.
    """

    @pipeline_thread.runs_on_pipeline_thread
    def _run_op(self, op):
        if isinstance(op, pipeline_ops_iothub.SetAuthProviderOperation):
            auth_provider = op.auth_provider
            operation_flow.delegate_to_different_op(
                stage=self,
                original_op=op,
                new_op=pipeline_ops_edge.SetEdgeConnectionArgsOperation(
                    device_id=auth_provider.device_id,
                    module_id=getattr(auth_provider, "module_id", None),
                    # hostname=auth_provider.hostname,
                    gateway_hostname=getattr(auth_provider, "gateway_hostname", None),
                    # ca_cert=getattr(auth_provider, "ca_cert", None),
                    # sas_token=auth_provider.get_current_sas_token(),
                ),
            )
        elif isinstance(op, pipeline_ops_iothub.SetX509AuthProviderOperation):
            auth_provider = op.auth_provider
            operation_flow.delegate_to_different_op(
                stage=self,
                original_op=op,
                new_op=pipeline_ops_edge.SetEdgeConnectionArgsOperation(
                    device_id=auth_provider.device_id,
                    module_id=getattr(auth_provider, "module_id", None),
                    # hostname=auth_provider.hostname,
                    gateway_hostname=getattr(auth_provider, "gateway_hostname", None),
                    # ca_cert=getattr(auth_provider, "ca_cert", None),
                    # client_cert=auth_provider.get_x509_certificate(),
                ),
            )
        else:
            operation_flow.pass_op_to_next_stage(self, op)
