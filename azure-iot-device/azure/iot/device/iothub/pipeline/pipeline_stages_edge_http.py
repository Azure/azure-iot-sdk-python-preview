# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from azure.iot.device.common.pipeline import (
    PipelineStage,
    operation_flow,
    pipeline_thread,
    pipeline_ops_http,
)
from . import pipeline_ops_edge


logger = logging.getLogger(__name__)


class EdgeHTTPConverterStage(PipelineStage):
    def __init__(self):
        super(EdgeHTTPConverterStage, self).__init__()

    @pipeline_thread.runs_on_pipeline_thread
    def _run_op(self, op):

        if isinstance(op, pipeline_ops_edge.SetEdgeConnectionArgsOperation):

            operation_flow.delegate_to_different_op(
                stage=self,
                original_op=op,
                new_op=pipeline_ops_http.SetHTTPConnectionArgsOperation(
                    hostname=op.gateway_hostname
                ),
            )

        elif isinstance(op, pipeline_ops_edge.InvokeMethodOperation):
            pass
