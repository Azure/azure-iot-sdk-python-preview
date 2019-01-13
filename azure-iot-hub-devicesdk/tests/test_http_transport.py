# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest
import re
import responses
import logging
from datetime import datetime
from threading import Event
from azure.iot.hub.devicesdk.message import Message
from azure.iot.hub.devicesdk.transport.http.http_transport import HTTPTransport
from azure.iot.hub.devicesdk.auth.authentication_provider_factory import from_connection_string
from mock import MagicMock, patch

connection_string_format = "HostName={};DeviceId={};SharedAccessKey={}"
fake_shared_access_key = "Zm9vYmFy"
fake_hostname = "beauxbatons.academy-net"
fake_device_id = "MyPensieve"


@pytest.fixture(scope="function")
def authentication_provider():
    connection_string = connection_string_format.format(
        fake_hostname, fake_device_id, fake_shared_access_key
    )
    auth_provider = from_connection_string(connection_string)
    return auth_provider


@pytest.fixture(scope="function")
def transport(authentication_provider):
    transport = HTTPTransport(authentication_provider)
    transport.on_transport_connected = MagicMock()
    transport.on_transport_disconnected = MagicMock()
    transport.on_event_sent = MagicMock()
    yield transport
    transport.disconnect()


class TestConnect:
    def test_connect_calls_on_transport_connected(self, transport):
        transport.connect()
        transport.on_transport_connected.assert_called_once_with("connected")

    # TODO: looks like for now we support both passing a callback to the transport function AND calling the on_transport_connected handler. I think we only need one of those?
    def test_connect_calls_callback_if_provided(self, transport):
        callback_event = Event()

        def callback():
            callback_event.set()

        transport.connect(callback)
        callback_event.wait()
        transport.on_transport_connected.assert_called_once_with("connected")


class TestDisconnect:
    def test_disconnect_calls_on_transport_disconnected(self, transport):
        transport.disconnect()
        transport.on_transport_disconnected.assert_called_once_with("disconnected")

    def test_disconnect_calls_callback_if_provided(self, transport):
        callback_event = Event()

        def callback():
            callback_event.set()

        transport.disconnect(callback)
        callback_event.wait()
        transport.on_transport_disconnected.assert_called_once_with("disconnected")


class TestSendEvent:
    @responses.activate
    def test_send_event_encodes_message_properties(self, transport):
        responses.add(
            responses.POST,
            "https://" + fake_hostname + "/devices/" + fake_device_id + "/messages/events/",
            status=204,
        )
        test_date = datetime.now()
        test_msg = Message("test_payload")
        test_msg.message_id = "test_mid"
        test_msg.correlation_id = "test_cid"
        test_msg.user_id = "test_uid"
        test_msg.to = "test_to"
        test_msg.expiry_time_utc = test_date
        test_msg.ack = "full"
        test_msg.content_type = "application/json; charset=utf-8"
        test_msg.content_encoding = "utf-8"
        callback_event = Event()

        def callback():
            callback_event.set()

        transport.send_event(test_msg, callback)
        callback_event.wait()
        assert responses.calls[0].request.headers["IoTHub-MessageId"] == test_msg.message_id
        assert responses.calls[0].request.headers["IoTHub-CorrelationId"] == test_msg.correlation_id
        assert responses.calls[0].request.headers["IoTHub-UserId"] == test_msg.user_id
        assert responses.calls[0].request.headers["IoTHub-To"] == test_msg.to
        assert responses.calls[0].request.headers["IoTHub-Expiry"] == test_date.isoformat()
        assert responses.calls[0].request.headers["IoTHub-Ack"] == test_msg.ack
        assert responses.calls[0].request.headers["IoTHub-contenttype"] == test_msg.content_type
        assert (
            responses.calls[0].request.headers["IoTHub-contentencoding"]
            == test_msg.content_encoding
        )
        assert responses.calls[0].request.body == "test_payload"

    @responses.activate
    def test_send_event_sets_authorization_header(self, transport):
        responses.add(
            responses.POST,
            "https://" + fake_hostname + "/devices/" + fake_device_id + "/messages/events/",
            status=204,
        )
        test_msg = Message("test_payload")
        callback_event = Event()

        def callback():
            callback_event.set()

        transport.send_event(test_msg, callback)
        callback_event.wait()
        assert re.match(
            "^SharedAccessSignature.*", responses.calls[0].request.headers["Authorization"]
        )
