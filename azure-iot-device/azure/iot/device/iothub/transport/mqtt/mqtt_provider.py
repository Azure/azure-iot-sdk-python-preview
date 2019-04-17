# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import paho.mqtt.client as mqtt
import logging
import ssl
import traceback

logger = logging.getLogger(__name__)

LOG_UNKOWN_SUBACK = "SUBACK received with unknown MID: {}"
LOG_UKNOWN_PUBACK = "PUBACK received with unknown MID: {}"
LOG_UNKNOW_UNSUBACK = "UNSUBACK received with unknown MID: {}"


class MQTTProvider(object):
    """
    A wrapper over the actual implementation of mqtt message broker which will eventually connect to an mqtt broker
    to publish/subscribe messages.
    """

    def __init__(self, client_id, hostname, username, ca_cert=None):
        """
        Constructor to instantiate a mqtt provider.
        :param client_id: The id of the client connecting to the broker.
        :param hostname: hostname or IP address of the remote broker.
        :param ca_cert: Certificate which can be used to validate a server-side TLS connection.
        """
        self._client_id = client_id
        self._hostname = hostname
        self._username = username
        self._mqtt_client = None
        self._ca_cert = ca_cert

        self.on_mqtt_connected = None  # TODO: Replace this callback w/ a param to .connect()
        self.on_mqtt_disconnected = None
        self.on_mqtt_message_received = None

        # Maps mid->callback for operations where a control packet has been sent
        # but the reponse has not yet been received
        self._pending_operation_callbacks = {}

        # Maps mid->mid for responses received that are in the _pending_operation_callbacks dict.
        # Necessary because sometimes an operation will complete with a response before the
        # Paho call returns.
        # TODO: make this map mid to something more useful (result code?)
        self._unknown_operation_responses = {}

        self._create_mqtt_client()

    def _create_mqtt_client(self):
        """
        Create the MQTT client object and assign all necessary callbacks.
        """
        logger.info("creating mqtt client")

        self._mqtt_client = mqtt.Client(self._client_id, False, protocol=mqtt.MQTTv311)

        def on_connect(client, userdata, flags, result_code):
            logger.info("connected with result code: %s", str(result_code))
            # TODO: how to do failed connection?
            try:
                self.on_mqtt_connected()
            except:  # noqa: E722 do not use bare 'except'
                logger.error("Unexpected error calling on_mqtt_connected")
                logger.error(traceback.format_exc())

        def on_disconnect(client, userdata, result_code):
            logger.info("disconnected with result code: %s", str(result_code))
            try:
                self.on_mqtt_disconnected()
            except:  # noqa: E722 do not use bare 'except'
                logger.error("Unexpected error calling on_mqtt_disconnected")
                logger.error(traceback.format_exc())

        def on_subscribe(client, userdata, mid, granted_qos):
            logger.info("suback received for %s", str(mid))
            # TODO: how to do failure?
            self._resolve_pending_callback(mid)

        def on_unsubscribe(client, userdata, mid):
            logger.info("UNSUBACK received for %s", str(mid))
            # TODO: how to do failure?
            self._resolve_pending_callback(mid)

        def on_publish(client, userdata, mid):
            logger.info("payload published for %s", str(mid))
            # TODO: how to do failed publish
            self._resolve_pending_callback(mid)

        def on_message(client, userdata, mqtt_message):
            logger.info("message received on %s", mqtt_message.topic)
            try:
                self.on_mqtt_message_received(mqtt_message._topic, mqtt_message.payload)
            except:  # noqa: E722 do not use bare 'except'
                logger.error("Unexpected error calling on_mqtt_message_received")
                logger.error(traceback.format_exc())

        self._mqtt_client.on_connect = on_connect
        self._mqtt_client.on_disconnect = on_disconnect
        self._mqtt_client.on_subscribe = on_subscribe
        self._mqtt_client.on_unsubscribe = on_unsubscribe
        self._mqtt_client.on_publish = on_publish
        self._mqtt_client.on_message = on_message

        logger.info("Created MQTT provider, assigned callbacks")

    def connect(self, password):
        """
        This method connects the upper transport layer to the mqtt broker.
        This method should be called as an entry point before sending any telemetry.
        """
        logger.info("connecting to mqtt broker")

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        if self._ca_cert:
            ssl_context.load_verify_locations(cadata=self._ca_cert)
        else:
            ssl_context.load_default_certs()
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True
        self._mqtt_client.tls_set_context(ssl_context)
        self._mqtt_client.tls_insecure_set(False)
        self._mqtt_client.username_pw_set(username=self._username, password=password)

        self._mqtt_client.connect(host=self._hostname, port=8883)
        self._mqtt_client.loop_start()

    def reconnect(self, password):
        """
        This method reconnects the mqtt broker, possibly because of a password (sas) change
        Connect should have previously been called.
        """
        logger.info("reconnecting transport")
        self._mqtt_client.username_pw_set(username=self._username, password=password)
        self._mqtt_client.reconnect()

    def disconnect(self):
        """
        This method disconnects the mqtt provider. This should be called from the upper transport
        when it wants to disconnect from the mqtt provider.
        """
        logger.info("disconnecting transport")
        self._mqtt_client.disconnect()
        self._mqtt_client.loop_stop()  # Is this necessary? We just added it

    def publish(self, topic, message_payload, callback=None):
        """
        This method enables the transport to send a message to the message broker.
        By default the the quality of service level to use is set to 1.
        :param topic: topic: The topic that the message should be published on.
        :param message_payload: The actual message to send.
        :param callback: A callback triggered upon completion.
        :return message ID for the publish request.
        """
        logger.info("sending")
        message_info = self._mqtt_client.publish(topic=topic, payload=message_payload, qos=1)
        self._set_operation_callback(message_info.mid, callback)

    def subscribe(self, topic, qos=0, callback=None):
        """
        This method subscribes the client to one topic.
        :param topic: a single string specifying the subscription topic to subscribe to
        :param qos: the desired quality of service level for the subscription. Defaults to 0.
        :param callback: A callback triggered upon completion.
        :return: message ID for the subscribe request
        Raises a ValueError if qos is not 0, 1 or 2, or if topic is None or has zero string length,
        """
        logger.info("subscribing to %s with qos %s", topic, str(qos))
        (result, mid) = self._mqtt_client.subscribe(topic, qos)
        self._set_operation_callback(mid, callback)

    def unsubscribe(self, topic, callback=None):
        """
        Unsubscribe the client from one topic.
        :param topic: a single string which is the subscription topic to unsubscribe from.
        :param callback: A callback triggered upon completion.
        Raises a ValueError if topic is None or has zero string length, or is not a string.
        """
        logger.info("unsubscribing from %s", topic)
        (result, mid) = self._mqtt_client.unsubscribe(topic)
        self._set_operation_callback(mid, callback)

    def _set_operation_callback(self, mid, callback):
        if mid in self._unknown_operation_responses:
            # If response already came back, trigger the callback
            logger.info("Response for MID: {} was received early - triggering callback".format(mid))
            del self._unknown_operation_responses[mid]
            if callback:
                callback()
        else:
            # Otherwise, set the callback to use later
            logger.info("Waiting for response on MID: {}".format(mid))
            self._pending_operation_callbacks[mid] = callback

    def _resolve_pending_callback(self, mid):
        if mid in self._pending_operation_callbacks:
            # If mid is known, trigger it's associated callback
            logger.info(
                "Response received for recognized MID: {} - triggering callback".format(mid)
            )
            callback = self._pending_operation_callbacks[mid]
            del self._pending_operation_callbacks[mid]
            if callback:
                callback()
        else:
            # Otherwise, store the mid as an unknown response
            logger.warning("Response received for unknown MID: {}".format(mid))
            self._unknown_operation_responses[mid] = mid  # TODO: set something more useful here
