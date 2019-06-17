# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import six.moves.urllib as urllib
from azure.iot.device.common.pipeline import (
    pipeline_ops_base,
    pipeline_ops_mqtt,
    pipeline_events_mqtt,
    operation_flow,
)
from azure.iot.device.common.pipeline.pipeline_stages_base import PipelineStage
from azure.iot.device.provisioning.pipeline import constant, mqtt_topic
from azure.iot.device.provisioning.pipeline import (
    pipeline_events_provisioning,
    pipeline_ops_provisioning,
)

logger = logging.getLogger(__name__)


class ProvisioningMQTTConverter(PipelineStage):
    """
    PipelineStage which converts other Provisioning pipeline operations into Mqtt operations. This stage also
    converts pipelinemqtt pipeline events into Provisioning pipeline events.
    """

    def __init__(self):
        super(ProvisioningMQTTConverter, self).__init__()
        self.action_to_topic = {}

    def _run_op(self, op):

        if isinstance(
            op, pipeline_ops_provisioning.SetSecurityClientArgs
        ):  # TODO Generic Args , then only 1 case ?
            # get security client args from above, save some, use some to build topic names,
            # always pass it down because MQTT Provider stage will also want to receive these args.

            client_id = op.registration_id
            client_version = urllib.parse.quote_plus(constant.USER_AGENT)
            username = "{id_scope}/registrations/{registration_id}/api-version={api_version}&ClientVersion={client_version}".format(
                id_scope=op.id_scope,
                registration_id=op.registration_id,
                api_version=constant.API_VERSION,
                client_version=client_version,
            )

            hostname = op.provisioning_host

            operation_flow.delegate_to_different_op(
                stage=self,
                original_op=op,
                new_op=pipeline_ops_mqtt.SetConnectionArgs(
                    client_id=client_id, hostname=hostname, username=username
                ),
            )

        elif isinstance(op, pipeline_ops_provisioning.SendRegistrationRequest):
            # Convert Sending the request into Mqtt Publish operations
            topic = mqtt_topic.get_topic_for_register(op.request_id)
            operation_flow.delegate_to_different_op(
                stage=self,
                original_op=op,
                new_op=pipeline_ops_mqtt.Publish(topic=topic, payload=op.request_payload),
            )

        elif isinstance(op, pipeline_ops_provisioning.SendQueryRequest):
            # Convert Sending the request into Mqtt Publish operations
            topic = mqtt_topic.get_topic_for_query(op.request_id, op.operation_id)
            operation_flow.delegate_to_different_op(
                stage=self,
                original_op=op,
                new_op=pipeline_ops_mqtt.Publish(topic=topic, payload=op.request_payload),
            )

        elif isinstance(op, pipeline_ops_base.EnableFeature):
            # Enabling for register gets translated into an Mqtt subscribe operation
            topic = mqtt_topic.get_topic_for_subscribe()
            operation_flow.delegate_to_different_op(
                stage=self, original_op=op, new_op=pipeline_ops_mqtt.Subscribe(topic=topic)
            )

        elif isinstance(op, pipeline_ops_base.DisableFeature):
            # Disabling a register response gets turned into an Mqtt unsubscribe operation
            topic = mqtt_topic.get_topic_for_subscribe()
            operation_flow.delegate_to_different_op(
                stage=self, original_op=op, new_op=pipeline_ops_mqtt.Unsubscribe(topic=topic)
            )

        else:
            # All other operations get passed down
            operation_flow.pass_op_to_next_stage(self, op)

    def _handle_pipeline_event(self, event):
        """
        Pipeline Event handler function to convert incoming Mqtt messages into the appropriate DPS
        events, based on the topic of the message
        """
        if isinstance(event, pipeline_events_mqtt.IncomingMessage):
            topic = event.topic

            if mqtt_topic.is_dps_response_topic(topic):
                logger.info(
                    "Received payload:{payload} on topic:{topic}".format(
                        payload=event.payload, topic=topic
                    )
                )
                key_values = mqtt_topic.extract_properties_from_topic(topic)
                status_code = mqtt_topic.extract_status_code_from_topic(topic)
                request_id = key_values["rid"][0]
                if event.payload is not None:
                    response = event.payload.decode("utf-8")
                # Extract pertinent information from mqtt topic
                # like status code request_id and send it upwards.
                self.handle_pipeline_event(
                    pipeline_events_provisioning.RegistrationResponseEvent(
                        request_id, status_code, key_values, response
                    )
                )
            else:
                logger.warning("Unknown topic: {} passing up to next handler".format(topic))
                PipelineStage._handle_pipeline_event(self, event)

        else:
            # all other messages get passed up
            PipelineStage._handle_pipeline_event(self, event)
