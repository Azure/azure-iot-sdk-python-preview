# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from azure.iot.device.common.pipeline import (
    pipeline_stages_base,
    pipeline_ops_base,
    pipeline_stages_http,
)
from . import pipeline_stages_edge, pipeline_stages_edge_http, pipeline_ops_iothub
from azure.iot.device.iothub.auth import X509AuthenticationProvider

logger = logging.getLogger(__name__)


class EdgePipeline(object):
    """Pipeline to communicate with Edge.
    Uses HTTP.
    """

    def __init__(self, auth_provider):

        self._pipeline = (
            pipeline_stages_base.PipelineRootStage()
            .append_stage(
                pipeline_stages_edge.UseAuthProviderStage()
            )  # TODO: combine with iothub equivalent
            # .append_stage(pipeline_stages_base.EnsureConnectionStage())
            .append_stage(pipeline_stages_edge_http.EdgeHTTPConverterStage())
            .append_stage(pipeline_stages_http.HTTPTransportStage())
        )

        def remove_this_code(call):
            if call.error:
                raise call.error

        # For now use the iothub ops to prevent duplication
        # TODO: make this op more generic - nothing iothub specific about auth provider
        # TODO: these also should be the same op (pending auth provider revision)
        if isinstance(auth_provider, X509AuthenticationProvider):
            op = pipeline_ops_iothub.SetX509AuthProviderOperation(
                auth_provider=auth_provider, callback=remove_this_code
            )
        else:
            op = pipeline_ops_iothub.SetAuthProviderOperation(
                auth_provider=auth_provider, callback=remove_this_code
            )

        self._pipeline.run_op(op)
