# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from datetime import date
import six.moves.urllib as urllib
from transitions import Machine
from .mqtt_state_provider import MQTTStateProvider
from azure.iot.device.iothub.transport.abstract_transport import AbstractTransport
from azure.iot.device.iothub.transport import constant
from azure.iot.device.iothub.models import Message

logger = logging.getLogger(__name__)

TOPIC_POS_DEVICE = 4
TOPIC_POS_MODULE = 6
TOPIC_POS_INPUT_NAME = 5


class MQTTTransport(AbstractTransport):
    def __init__(self, auth_provider):
        """
        Constructor for instantiating a transport
        :param auth_provider: The authentication provider
        """
        AbstractTransport.__init__(self, auth_provider)
        self.topic = self._get_telemetry_topic_for_publish()
        self._mqtt_state_provider = None

        self._connect_callback = None
        self._disconnect_callback = None

        self._c2d_topic = None
        self._input_topic = None

        self._create_mqtt_state_provider()

    def _create_mqtt_state_provider(self):
        """
        Create the provider object which is used by this instance to communicate with the service.
        No network communication can take place without a provider object.
        """
        client_id = self._auth_provider.device_id

        if self._auth_provider.module_id:
            client_id += "/" + self._auth_provider.module_id

        username = self._auth_provider.hostname + "/" + client_id + "/" + "?api-version=2018-06-30"

        hostname = None
        if hasattr(self._auth_provider, "gateway_hostname"):
            hostname = self._auth_provider.gateway_hostname
        if not hostname or len(hostname) == 0:
            hostname = self._auth_provider.hostname

        if hasattr(self._auth_provider, "ca_cert"):
            ca_cert = self._auth_provider.ca_cert
        else:
            ca_cert = None

        self._mqtt_state_provider = MQTTStateProvider(
            client_id, hostname, username, ca_cert=ca_cert
        )

        # TODO: remove provider.on_mqtt_connected - should pass as a param to provider.connect()
        self._mqtt_state_provider.on_mqtt_connected = self._on_provider_connect_complete
        self._mqtt_state_provider.on_mqtt_disconnected = self._on_provider_disconnect_complete
        self._mqtt_state_provider.on_mqtt_message_received = (
            self._on_provider_message_received_callback
        )

    def _get_topic_base(self):
        """
        return the string that is at the beginning of all topics for this
        device/module
        """

        if self._auth_provider.module_id:
            return (
                "devices/"
                + self._auth_provider.device_id
                + "/modules/"
                + self._auth_provider.module_id
            )
        else:
            return "devices/" + self._auth_provider.device_id

    def _get_telemetry_topic_for_publish(self):
        """
        return the topic string used to publish telemetry
        """
        return self._get_topic_base() + "/messages/events/"

    def _get_c2d_topic_for_subscribe(self):
        """
        :return: The topic for cloud to device messages.It is of the format
        "devices/<deviceid>/messages/devicebound/#"
        """
        return self._get_topic_base() + "/messages/devicebound/#"

    def _get_input_topic_for_subscribe(self):
        """
        :return: The topic for input messages. It is of the format
        "devices/<deviceId>/modules/<moduleId>/messages/inputs/#"
        """
        return self._get_topic_base() + "/inputs/#"

    def connect(self, callback=None):
        """
        Connect to the service.

        :param callback: callback which is called when the connection to the service is complete.
        """
        logger.info("connect called")
        self._connect_callback = callback
        self._trig_connect()

    def disconnect(self, callback=None):
        """
        Disconnect from the service.

        :param callback: callback which is called when the connection to the service has been disconnected
        """
        logger.info("disconnect called")
        self._disconnect_callback = callback
        self._trig_disconnect()

    def send_event(self, message, callback=None):
        """
        Send a telemetry message to the service.

        :param callback: callback which is called when the message publish has been acknowledged by the service.
        """
        encoded_topic = _encode_properties(message, self._get_telemetry_topic_for_publish())
        self._mqtt_state_provider.publish(encoded_topic, message, callback)

    def send_output_event(self, message, callback=None):
        """
        Send an output message to the service.

        :param callback: callback which is called when the message publish has been acknowledged by the service.
        """
        encoded_topic = _encode_properties(message, self._get_telemetry_topic_for_publish())
        self._mqtt_state_provider.publish(encoded_topic, message, callback)

    def send_method_response(self, method, payload, status, callback=None):
        raise NotImplementedError

    def _on_shared_access_string_updated(self):
        """
        Callback which is called by the authentication provider when the shared access string has been updated.
        """
        self._trig_on_shared_access_string_updated()

    def enable_feature(self, feature_name, callback=None):
        """
        Enable the given feature by subscribing to the appropriate topics.

        :param feature_name: one of the feature name constants from constant.py
        :param callback: callback which is called when the feature is enabled
        """
        logger.info("enable_feature %s called", feature_name)
        if feature_name == constant.INPUT_MSG:
            self._enable_input_messages(callback)
        elif feature_name == constant.C2D_MSG:
            self._enable_c2d_messages(callback)
        elif feature_name == constant.METHODS:
            self._enable_methods(callback)
        else:
            logger.error("Feature name {} is unknown".format(feature_name))
            raise ValueError("Invalid feature name")

    def disable_feature(self, feature_name, callback=None):
        """
        Disable the given feature by subscribing to the appropriate topics.
        :param callback: callback which is called when the feature is disabled

        :param feature_name: one of the feature name constants from constant.py
        """
        logger.info("disable_feature %s called", feature_name)
        if feature_name == constant.INPUT_MSG:
            self._disable_input_messages(callback)
        elif feature_name == constant.C2D_MSG:
            self._disable_c2d_messages(callback)
        elif feature_name == constant.METHODS:
            self._disable_methods(callback)
        else:
            logger.error("Feature name {} is unknown".format(feature_name))
            raise ValueError("Invalid feature name")

    def _enable_input_messages(self, callback=None):
        """
        Helper function to enable input messages

        :param callback: callback which is called when the feature is enabled
        """
        self._mqtt_state_provider.subscribe(
            topic=self._get_input_topic_for_subscribe(), qos=1, callback=callback
        )
        self.feature_enabled[constant.INPUT_MSG] = True

    def _disable_input_messages(self, callback=None):
        """
        Helper function to disable input messages

        :param callback: callback which is called when the feature is disabled
        """
        self._mqtt_sate_provider.unsubscribe(
            topic=self._get_input_topic_for_subscribe(), callback=callback
        )
        self.feature_enabled[constant.INPUT_MSG] = False

    def _enable_c2d_messages(self, callback=None):
        """
        Helper function to enable c2de messages

        :param callback: callback which is called when the feature is enabled
        """
        self._mqtt_state_provider.subscribe(
            topic=self._get_c2d_topic_for_subscribe(), qos=1, callback=callback
        )
        self.feature_enabled[constant.C2D_MSG] = True

    def _disable_c2d_messages(self, callback=None):
        """
        Helper function to disabled c2d messages

        :param callback: callback which is called when the feature is disabled
        """
        self._mqtt_state_provider.unsubscribe(
            topic=self._get_c2d_topic_for_subscribe(), callback=callback
        )
        self.feature_enabled[constant.C2D_MSG] = False

    def _enable_methods(self, callback=None, qos=1):
        """
        Helper function to enable methods

        :param callback: callback which is called when the feature is enabled.
        :param qos: Quality of Serivce level
        """
        self._mqtt_state_provider.subscribe(self._get_method_topic_for_subscribe(), qos, callback)
        self.feature_enabled[constant.METHODS] = True

    def _disable_methods(self, callback=None):
        """
        Helper function to disable methods

        :param callback: callback which is called when the feature is disabled
        """
        self._mqtt_state_provider.unsubscribe(self._get_method_topic_for_subscribe(), callback)
        self.feature_enabled[constant.METHODS] = False


def _is_c2d_topic(split_topic_str):
    """
    Topics for c2d message are of the following format:
    devices/<deviceId>/messages/devicebound
    :param split_topic_str: The already split received topic string
    """
    if "messages/devicebound" in split_topic_str and len(split_topic_str) > 4:
        return True
    return False


def _is_input_topic(split_topic_str):
    """
    Topics for inputs are of the following format:
    devices/<deviceId>/modules/<moduleId>/messages/inputs/<inputName>
    :param split_topic_str: The already split received topic string
    """
    if "inputs" in split_topic_str and len(split_topic_str) > 6:
        return True
    return False


def _extract_properties(properties, message_received):
    """
    Extract key=value pairs from custom properties and set the properties on the received message.
    :param properties: The properties string which is ampersand(&) delimited key=value pair.
    :param message_received: The message received with the payload in bytes
    """
    key_value_pairs = properties.split("&")

    for entry in key_value_pairs:
        pair = entry.split("=")
        key = urllib.parse.unquote_plus(pair[0])
        value = urllib.parse.unquote_plus(pair[1])

        if key == "$.mid":
            message_received.message_id = value
        elif key == "$.cid":
            message_received.correlation_id = value
        elif key == "$.uid":
            message_received.user_id = value
        elif key == "$.to":
            message_received.to = value
        elif key == "$.ct":
            message_received.content_type = value
        elif key == "$.ce":
            message_received.content_encoding = value
        else:
            message_received.custom_properties[key] = value


def _encode_properties(message_to_send, topic):
    """
    uri-encode the system properties of a message as key-value pairs on the topic with defined keys.
    Additionally if the message has user defined properties, the property keys and values shall be
    uri-encoded and appended at the end of the above topic with the following convention:
    '<key>=<value>&<key2>=<value2>&<key3>=<value3>(...)'
    :param message_to_send: The message to send
    :param topic: The topic which has not been encoded yet. For a device it looks like
    "devices/<deviceId>/messages/events/" and for a module it looks like
    "devices/<deviceId>/modules/<moduleId>/messages/events/
    :return: The topic which has been uri-encoded
    """
    system_properties = {}
    if message_to_send.output_name:
        system_properties["$.on"] = message_to_send.output_name
    if message_to_send.message_id:
        system_properties["$.mid"] = message_to_send.message_id

    if message_to_send.correlation_id:
        system_properties["$.cid"] = message_to_send.correlation_id

    if message_to_send.user_id:
        system_properties["$.uid"] = message_to_send.user_id

    if message_to_send.to:
        system_properties["$.to"] = message_to_send.to

    if message_to_send.content_type:
        system_properties["$.ct"] = message_to_send.content_type

    if message_to_send.content_encoding:
        system_properties["$.ce"] = message_to_send.content_encoding

    if message_to_send.expiry_time_utc:
        system_properties["$.exp"] = (
            message_to_send.expiry_time_utc.isoformat()
            if isinstance(message_to_send.expiry_time_utc, date)
            else message_to_send.expiry_time_utc
        )

    system_properties_encoded = urllib.parse.urlencode(system_properties)
    topic += system_properties_encoded

    if message_to_send.custom_properties and len(message_to_send.custom_properties) > 0:
        topic += "&"
        user_properties_encoded = urllib.parse.urlencode(message_to_send.custom_properties)
        topic += user_properties_encoded

    return topic
