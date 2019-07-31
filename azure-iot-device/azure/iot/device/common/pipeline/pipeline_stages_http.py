# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from . import PipelineStage, pipeline_thread, pipeline_ops_http, operation_flow
from azure.iot.device.common.http_transport import HTTPTransport

logger = logging.getLogger(__name__)


# TODO: doc
class HTTPTransportStage(PipelineStage):
    """
    """

    @pipeline_thread.runs_on_pipeline_thread
    def _run_op(self, op):
        if isinstance(op, pipeline_ops_http.SetHTTPConnectionArgsOperation):
            logger.info("{}({}): got connection args".format(self.name, op.name))
            self.hostname = op.hostname
            # self.ca_cert = op.ca_cert

            self.transport = HTTPTransport(hostname=self.hostname)
            self.pipeline_root.transport = self.transport  # WHY??
            operation_flow.complete_op(self, op)
