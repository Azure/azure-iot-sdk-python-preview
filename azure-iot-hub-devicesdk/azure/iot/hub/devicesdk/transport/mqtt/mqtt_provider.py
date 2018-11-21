# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import paho.mqtt.client as mqtt
import logging
import ssl

logger = logging.getLogger(__name__)


class MQTTProvider(object):
    """
    A wrapper over the actual implementation of mqtt message broker which will eventually connect to an mqtt broker
    to publish/subscribe messages.
    """

    def __init__(self, client_id, hostname, username, password, ca_cert=None):
        """
        Constructor to instantiate a mqtt provider.
        :param client_id: The id of the client connecting to the broker.
        :param hostname: hostname or IP address of the remote broker.
        :param password:  The password to authenticate with.
        :param ca_cert: Certificate which can be used to validate a server-side TLS connection.
        """
        self._client_id = client_id
        self._hostname = hostname
        self._username = username
        self._password = password
        self._mqtt_client = None
        self._ca_cert = ca_cert

        self.on_mqtt_connected = None
        self.on_mqtt_disconnected = None
        self.on_mqtt_published = None
        self.on_mqtt_subscribed = None

        self._create_mqtt_client()

    def _create_mqtt_client(self):
        """
        Create the MQTT client object and assign all necessary callbacks.
        """
        logger.info("creating mqtt client")

        self._mqtt_client = mqtt.Client(self._client_id, False, protocol=mqtt.MQTTv311)

        def on_connect_callback(client, userdata, flags, result_code):
            logger.info("connected with result code: %s", str(result_code))
            # TODO: how to do failed connection?
            self.on_mqtt_connected("connected")

        def on_disconnect_callback(client, userdata, result_code):
            logger.info("disconnected with result code: %s", str(result_code))
            self.on_mqtt_disconnected("disconnected")

        def on_publish_callback(client, userdata, mid):
            logger.info("payload published for %s", str(mid))
            # TODO: how to do failed publish
            self.on_mqtt_published()

        def on_subscribe_callback(client, userdata, mid):
            logger.info("suback received")
            # TODO: how to do failure?
            self.on_mqtt_subscribed()

        self._mqtt_client.on_connect = on_connect_callback
        self._mqtt_client.on_disconnect = on_disconnect_callback
        self._mqtt_client.on_publish = on_publish_callback
        self._mqtt_client.on_subscribe = on_subscribe_callback

        logger.info("Created MQTT provider, assigned callbacks")

    def connect(self):
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
        self._mqtt_client.username_pw_set(username=self._username, password=self._password)

        self._mqtt_client.connect(host=self._hostname, port=8883)
        self._mqtt_client.loop_start()

    def disconnect(self):
        """
        This method disconnects the mqtt provider. This should be called from the upper transport
        when it wants to disconnect from the mqtt provider.
        """
        logger.info("disconnecting transport")
        self._mqtt_client.loop_stop()
        self._mqtt_client.disconnect()

    def publish(self, topic, message_payload):
        """
        This method enables the transport to send a message to the message broker
        :param topic: topic: The topic that the message should be published on.
        :param message_payload: The actual message to send.
        """
        logger.info("sending")
        self._mqtt_client.publish(topic=topic, payload=message_payload, qos=1)
