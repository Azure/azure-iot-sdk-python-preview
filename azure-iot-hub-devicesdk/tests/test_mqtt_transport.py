# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest
import logging
import six.moves.urllib as urllib
from azure.iot.hub.devicesdk.message import Message
from azure.iot.hub.devicesdk.transport.mqtt.mqtt_transport import MQTTTransport, MQTTProvider
from azure.iot.hub.devicesdk.auth.authentication_provider_factory import (
    from_connection_string,
    from_x509,
)
import azure.iot.hub.devicesdk.auth.sk_authentication_provider as sk_auth
import azure.iot.hub.devicesdk.auth.x509_authentication_provider as x509_auth
from mock import MagicMock, patch
from datetime import date


logging.basicConfig(level=logging.INFO)

connection_string_format = "HostName={};DeviceId={};SharedAccessKey={}"
connection_string_format_mod = "HostName={};DeviceId={};ModuleId={};SharedAccessKey={}"
fake_shared_access_key = "Zm9vYmFy"
fake_hostname = "beauxbatons.academy-net"
fake_device_id = "MyPensieve"
fake_module_id = "MemoryCharms"
fake_event = "Wingardian Leviosa"
fake_event_2 = fake_event + " again!"

before_sys_key = "%24."
after_sys_key = "="
topic_separator = "&"
message_id_key = "mid"
fake_message_id = "spell-1234"
custom_property_value = "yes"
custom_property_name = "dementor_alert"
fake_topic = "devices/" + fake_device_id + "/messages/events/"

encoded_fake_topic = (
    fake_topic
    + before_sys_key
    + message_id_key
    + after_sys_key
    + fake_message_id
    + topic_separator
    + custom_property_name
    + after_sys_key
    + custom_property_value
)


def create_fake_message():
    msg = Message(fake_event)
    msg.message_id = fake_message_id
    msg.custom_properties[custom_property_name] = custom_property_value
    return msg


fake_cert_path = "/cert/path"
fake_key_path = "/key/path"


class BadAuthProvider:
    def __init__(self):
        self.device_id = fake_device_id
        self.hostname = fake_hostname
        self.module_id = None


@pytest.fixture(scope="function")
def sk_authentication_provider():
    connection_string = connection_string_format.format(
        fake_hostname, fake_device_id, fake_shared_access_key
    )
    auth_provider = from_connection_string(connection_string)
    return auth_provider


@pytest.fixture(scope="function")
def x509_authentication_provider():
    auth_provider = from_x509(fake_device_id, fake_hostname, fake_cert_path, fake_key_path)
    return auth_provider


@pytest.fixture(scope="function")
def transport(sk_authentication_provider):
    with patch("azure.iot.hub.devicesdk.transport.mqtt.mqtt_transport.MQTTProvider"):
        transport = MQTTTransport(sk_authentication_provider)
    transport.on_transport_connected = MagicMock()
    transport.on_transport_disconnected = MagicMock()
    transport.on_event_sent = MagicMock()
    yield transport
    transport.disconnect()


@pytest.fixture(scope="function")
def transport_module():
    connection_string_mod = connection_string_format_mod.format(
        fake_hostname, fake_device_id, fake_module_id, fake_shared_access_key
    )
    authentication_provider = from_connection_string(connection_string_mod)

    with patch("azure.iot.hub.devicesdk.transport.mqtt.mqtt_transport.MQTTProvider"):
        transport = MQTTTransport(authentication_provider)
    transport.on_transport_connected = MagicMock()
    transport.on_transport_disconnected = MagicMock()
    transport.on_event_sent = MagicMock()
    yield transport
    transport.disconnect()


@patch.object(sk_auth, "SymmetricKeyAuthenticationProvider")
def test_instantiation_creates_proper_transport_sk(sk_authentication_provider):
    transport = MQTTTransport(sk_authentication_provider)
    assert transport._auth_provider == sk_authentication_provider
    assert transport._mqtt_provider is not None
    assert isinstance(transport._mqtt_provider, MQTTProvider)


def test_instantiation_creates_proper_transport_x509(x509_authentication_provider):
    transport = MQTTTransport(x509_authentication_provider)
    assert transport._auth_provider == x509_authentication_provider
    assert transport._mqtt_provider is not None
    assert isinstance(transport._mqtt_provider, MQTTProvider)


def test_instantiation_raises_TypeError_on_invalid_auth_provider():
    bad_auth_provider = BadAuthProvider()
    with pytest.raises(TypeError):
        transport = MQTTTransport(bad_auth_provider)
        transport.connect()


class TestConnect:
    def test_connect_calls_connect_on_provider(self, transport):
        mock_mqtt_provider = transport._mqtt_provider
        transport.connect()
        mock_mqtt_provider.connect.assert_called_once_with(
            transport._auth_provider.get_current_sas_token(), None
        )
        mock_mqtt_provider.on_mqtt_connected()

    def test_connected_state_handler_called_wth_new_state_once_provider_gets_connected(
        self, transport
    ):
        mock_mqtt_provider = transport._mqtt_provider

        transport.connect()
        mock_mqtt_provider.on_mqtt_connected()

        transport.on_transport_connected.assert_called_once_with("connected")

    def test_connect_ignored_if_waiting_for_connect_complete(self, transport):
        mock_mqtt_provider = transport._mqtt_provider

        transport.connect()
        transport.connect()
        mock_mqtt_provider.on_mqtt_connected()

        mock_mqtt_provider.connect.assert_called_once_with(
            transport._auth_provider.get_current_sas_token(), None
        )
        transport.on_transport_connected.assert_called_once_with("connected")

    def test_connect_ignored_if_waiting_for_send_complete(self, transport):
        mock_mqtt_provider = transport._mqtt_provider

        transport.connect()
        mock_mqtt_provider.on_mqtt_connected()

        mock_mqtt_provider.reset_mock()
        transport.on_transport_connected.reset_mock()

        transport.send_event(create_fake_message())
        transport.connect()

        mock_mqtt_provider.connect.assert_not_called()
        transport.on_transport_connected.assert_not_called()

        mock_mqtt_provider.on_mqtt_published(0)

        mock_mqtt_provider.connect.assert_not_called()
        transport.on_transport_connected.assert_not_called()


class TestSendEvent:
    def test_send_message_with_no_properties(self, transport):
        fake_msg = Message("Petrificus Totalus")

        mock_mqtt_provider = transport._mqtt_provider

        transport.connect()
        mock_mqtt_provider.on_mqtt_connected()
        transport.send_event(fake_msg)

        mock_mqtt_provider.connect.assert_called_once_with(
            transport._auth_provider.get_current_sas_token()
        )
        mock_mqtt_provider.publish.assert_called_once_with(fake_topic, fake_msg.data)

    def test_send_message_with_output_name(self, transport_module):
        fake_msg = Message("Petrificus Totalus")
        fake_msg.custom_properties[custom_property_name] = custom_property_value
        fake_msg.output_name = "fake_output_name"

        fake_output_topic = (
            "devices/"
            + fake_device_id
            + "/modules/"
            + fake_module_id
            + "/messages/events/"
            + before_sys_key
            + "on"
            + after_sys_key
            + "fake_output_name"
            + topic_separator
            + custom_property_name
            + after_sys_key
            + custom_property_value
        )

        mock_mqtt_provider = transport_module._mqtt_provider

        transport_module.connect()
        mock_mqtt_provider.on_mqtt_connected()
        transport_module.send_event(fake_msg)

        mock_mqtt_provider.connect.assert_called_once_with(
            transport_module._auth_provider.get_current_sas_token()
        )
        mock_mqtt_provider.publish.assert_called_once_with(fake_output_topic, fake_msg.data)

    def test_sendevent_calls_publish_on_provider(self, transport):
        fake_msg = create_fake_message()

        mock_mqtt_provider = transport._mqtt_provider

        transport.connect()
        mock_mqtt_provider.on_mqtt_connected()
        transport.send_event(fake_msg)

        mock_mqtt_provider.connect.assert_called_once_with(
            transport._auth_provider.get_current_sas_token(), None
        )
        mock_mqtt_provider.publish.assert_called_once_with(encoded_fake_topic, fake_msg.data)

    def test_send_event_queues_and_connects_before_sending(self, transport):
        fake_msg = create_fake_message()
        mock_mqtt_provider = transport._mqtt_provider

        # send an event
        transport.send_event(fake_msg)

        # verify that we called connect
        mock_mqtt_provider.connect.assert_called_once_with(
            transport._auth_provider.get_current_sas_token(), None
        )

        # verify that we're not connected yet and verify that we havent't published yet
        transport.on_transport_connected.assert_not_called()
        mock_mqtt_provider.publish.assert_not_called()

        # finish the connection
        mock_mqtt_provider.on_mqtt_connected()

        # verify that our connected callback was called and verify that we published the event
        transport.on_transport_connected.assert_called_once_with("connected")
        mock_mqtt_provider.publish.assert_called_once_with(encoded_fake_topic, fake_msg.data)

    def test_send_event_queues_if_waiting_for_connect_complete(self, transport):
        fake_msg = create_fake_message()

        mock_mqtt_provider = transport._mqtt_provider

        # start connecting and verify that we've called into the provider
        transport.connect()
        mock_mqtt_provider.connect.assert_called_once_with(
            transport._auth_provider.get_current_sas_token(), None
        )

        # send an event
        transport.send_event(fake_msg)

        # verify that we're not connected yet and verify that we havent't published yet
        transport.on_transport_connected.assert_not_called()
        mock_mqtt_provider.publish.assert_not_called()

        # finish the connection
        mock_mqtt_provider.on_mqtt_connected()

        # verify that our connected callback was called and verify that we published the event
        transport.on_transport_connected.assert_called_once_with("connected")
        mock_mqtt_provider.publish.assert_called_once_with(encoded_fake_topic, fake_msg.data)

    def test_send_event_sends_overlapped_events(self, transport):
        fake_msg_1 = create_fake_message()
        fake_msg_2 = Message(fake_event_2)

        mock_mqtt_provider = transport._mqtt_provider

        # connect
        transport.connect()
        mock_mqtt_provider.on_mqtt_connected()

        # send an event
        callback_1 = MagicMock()
        transport.send_event(fake_msg_1, callback_1)
        mock_mqtt_provider.publish.assert_called_once_with(encoded_fake_topic, fake_msg_1.data)

        # while we're waiting for that send to complete, send another event
        callback_2 = MagicMock()
        transport.send_event(fake_msg_2, callback_2)

        # verify that we've called publish twice and verify that neither send_event
        # has completed (because we didn't do anything here to complete it).
        assert mock_mqtt_provider.publish.call_count == 2
        callback_1.assert_not_called()
        callback_2.assert_not_called()

    def test_puback_calls_client_callback(self, transport):
        fake_msg = create_fake_message()

        mock_mqtt_provider = transport._mqtt_provider

        # connect
        transport.connect()
        mock_mqtt_provider.on_mqtt_connected()

        # send an event
        transport.send_event(fake_msg)

        # fake the puback:
        mock_mqtt_provider.on_mqtt_published(0)

        # assert
        transport.on_event_sent.assert_called_once_with()

    def test_connect_send_disconnect(self, transport):
        fake_msg = create_fake_message()

        mock_mqtt_provider = transport._mqtt_provider

        # connect
        transport.connect()
        mock_mqtt_provider.on_mqtt_connected()

        # send an event
        transport.send_event(fake_msg)
        mock_mqtt_provider.on_mqtt_published(0)

        # disconnect
        transport.disconnect()
        mock_mqtt_provider.disconnect.assert_called_once_with()


class TestDisconnect:
    def test_disconnect_calls_disconnect_on_provider(self, transport):
        mock_mqtt_provider = transport._mqtt_provider

        transport.connect()
        mock_mqtt_provider.on_mqtt_connected()
        transport.disconnect()

        mock_mqtt_provider.disconnect.assert_called_once_with()

    def test_disconnect_ignored_if_already_disconnected(self, transport):
        mock_mqtt_provider = transport._mqtt_provider

        transport.disconnect(None)

        mock_mqtt_provider.disconnect.assert_not_called()

    def test_disconnect_calls_client_disconnect_callback(self, transport):
        mock_mqtt_provider = transport._mqtt_provider

        transport.connect()
        mock_mqtt_provider.on_mqtt_connected()

        transport.disconnect()
        mock_mqtt_provider.on_mqtt_disconnected()

        transport.on_transport_disconnected.assert_called_once_with("disconnected")
