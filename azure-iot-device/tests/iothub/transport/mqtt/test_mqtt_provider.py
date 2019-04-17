# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.iot.device.iothub.transport.mqtt.mqtt_provider import MQTTProvider
import paho.mqtt.client as mqtt
import ssl
import pytest
import pytest_mock

fake_hostname = "beauxbatons.academy-net"
fake_device_id = "MyFirebolt"
fake_password = "Fortuna Major"
fake_username = fake_hostname + "/" + fake_device_id
new_fake_password = "new fake password"
fake_topic = "fake_topic"
fake_qos = 1
fake_mid = 52
fake_rc = 0


@pytest.fixture
def mock_mqtt_client(mocker):
    mock = mocker.patch.object(mqtt, "Client")
    # Return the mock resulting object, rather than the mock constructor
    return mock.return_value


@pytest.fixture
def provider(mock_mqtt_client):
    return MQTTProvider(fake_device_id, fake_hostname, fake_username)


@pytest.fixture
def message_info(mocker):
    mi = mqtt.MQTTMessageInfo(fake_mid)
    mi.rc = fake_rc
    return mi


@pytest.mark.describe("MQTT Provider - Instantiation")
class TestInstantiation(object):

    # TODO: test custom ca_cert
    @pytest.mark.it("Creates an instance of the Paho MQTT Client")
    def test_instantiates_mqtt_client(self, mocker):
        mock_mqtt_client_constructor = mocker.patch.object(mqtt, "Client")

        MQTTProvider(fake_device_id, fake_hostname, fake_username)

        assert mock_mqtt_client_constructor.call_count == 1
        assert mock_mqtt_client_constructor.call_args == mocker.call(
            fake_device_id, False, protocol=mqtt.MQTTv311
        )

    # TODO: verify these are set to the specific callback, not just not None
    @pytest.mark.it("Sets Paho MQTT Client callbacks")
    def test_sets_paho_callbacks(self, mocker):
        mock_mqtt_client = mocker.patch.object(mqtt, "Client").return_value

        MQTTProvider(fake_device_id, fake_hostname, fake_username)

        assert mock_mqtt_client.on_connect is not None
        assert mock_mqtt_client.on_disconnect is not None
        assert mock_mqtt_client.on_subscribe is not None
        assert mock_mqtt_client.on_unsubscribe is not None
        assert mock_mqtt_client.on_publish is not None
        assert mock_mqtt_client.on_message is not None

    @pytest.mark.it("Initializes event handler callbacks to 'None'")
    def test_handler_callbacks_set_to_none(self, mocker):
        mocker.patch.object(mqtt, "Client")

        provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)

        assert provider.on_mqtt_connected is None
        assert provider.on_mqtt_disconnected is None
        assert provider.on_mqtt_message_received is None

    @pytest.mark.it("Initializes internal operation tracking structures")
    def test_operation_infrastructure_set_up(self, mocker):
        provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)

        assert provider._pending_operation_callbacks == {}
        assert provider._unknown_operation_responses == {}


@pytest.mark.describe("MQTT Provider - Connect")
class TestConnect(object):
    @pytest.mark.it("Configures TLS context")
    def test_configures_tls_context(self, mocker, mock_mqtt_client, provider):
        mock_ssl_context_constructor = mocker.patch.object(ssl, "SSLContext")
        mock_ssl_context = mock_ssl_context_constructor.return_value

        provider.connect(fake_password)

        # Verify correctness of TLS/SSL Context
        assert mock_ssl_context_constructor.call_count == 1
        assert mock_ssl_context_constructor.call_args == mocker.call(ssl.PROTOCOL_TLSv1_2)
        assert mock_ssl_context.check_hostname is True
        assert mock_ssl_context.verify_mode == ssl.CERT_REQUIRED
        assert mock_ssl_context.load_default_certs.call_count == 1

        # Verify correctness of MQTT Client TLS config
        assert mock_mqtt_client.tls_set_context.call_count == 1
        assert mock_mqtt_client.tls_set_context.call_args == mocker.call(mock_ssl_context)
        assert mock_mqtt_client.tls_insecure_set.call_count == 1
        assert mock_mqtt_client.tls_insecure_set.call_args == mocker.call(False)

    @pytest.mark.it("Sets username and password")
    def test_sets_username_and_password(self, mocker, mock_mqtt_client, provider):
        provider.connect(fake_password)

        assert mock_mqtt_client.username_pw_set.call_count == 1
        assert mock_mqtt_client.username_pw_set.call_args == mocker.call(
            username=fake_username, password=fake_password
        )

    @pytest.mark.it("Connects via Paho")
    def test_calls_paho_connect(self, mocker, mock_mqtt_client, provider):
        provider.connect(fake_password)

        assert mock_mqtt_client.connect.call_count == 1
        assert mock_mqtt_client.connect.call_args == mocker.call(host=fake_hostname, port=8883)

    @pytest.mark.it("Starts MQTT Network Loop")
    def test_calls_loop_start(self, mocker, mock_mqtt_client, provider):
        provider.connect(fake_password)

        assert mock_mqtt_client.loop_start.call_count == 1
        assert mock_mqtt_client.loop_start.call_args == mocker.call()


@pytest.mark.describe("MQTT Provider - Reconnect")
class TestReconnect(object):
    @pytest.mark.it("Sets username and password")
    def test_sets_username_and_password(self, mocker, mock_mqtt_client, provider):
        provider.reconnect(fake_password)

        assert mock_mqtt_client.username_pw_set.call_count == 1
        assert mock_mqtt_client.username_pw_set.call_args == mocker.call(
            username=fake_username, password=fake_password
        )

    @pytest.mark.it("Reconnects with Paho")
    def test_calls_paho_reconnect(self, mocker, mock_mqtt_client, provider):
        provider.reconnect(fake_password)

        assert mock_mqtt_client.reconnect.call_count == 1
        assert mock_mqtt_client.reconnect.call_args == mocker.call()


@pytest.mark.describe("MQTT Provider - Disconnect")
class TestDisconnect(object):
    @pytest.mark.it("Disconnects with Paho")
    def test_calls_paho_disconnect(self, mocker, mock_mqtt_client, provider):
        provider.disconnect()

        assert mock_mqtt_client.disconnect.call_count == 1
        assert mock_mqtt_client.disconnect.call_args == mocker.call()

    @pytest.mark.it("Stops MQTT Network Loop")
    def test_calls_loop_stop(self, mocker, mock_mqtt_client, provider):
        provider.disconnect()

        assert mock_mqtt_client.loop_stop.call_count == 1
        assert mock_mqtt_client.loop_stop.call_args == mocker.call()


@pytest.mark.describe("MQTT Provider - Subscribe")
class TestPublish(object):
    msg_payload = "Tarantallegra"

    @pytest.mark.it("Publishes with Paho")
    def test_calls_paho_publish(self, mocker, mock_mqtt_client, provider):
        provider.publish(fake_topic, self.msg_payload)

        assert mock_mqtt_client.publish.call_count == 1
        assert mock_mqtt_client.publish.call_args == mocker.call(
            topic=fake_topic, payload=self.msg_payload, qos=1
        )

    @pytest.mark.it("Triggers callback upon publish completion [regular flow]")
    @pytest.mark.parametrize("callback", [pytest_mock.mock().MagicMock()])
    def test_triggers_callback_upon_paho_on_publish_event(
        self, mocker, mock_mqtt_client, provider, message_info, callback
    ):
        # callback = mocker.MagicMock()
        mock_mqtt_client.publish.return_value = message_info

        # Initiate publish
        provider.publish(fake_topic, self.msg_payload, callback=callback)

        # Check callback is stored as pending, but not called
        assert callback.call_count == 0
        assert provider._pending_operation_callbacks == {message_info.mid: callback}
        assert provider._unknown_operation_responses == {}

        # Manually trigger Paho on_publish event handler
        mock_mqtt_client.on_publish(mock_mqtt_client, None, message_info.mid)

        # Check callback has now been called, and stored values cleared
        assert callback.call_count == 1
        assert provider._pending_operation_callbacks == {}
        assert provider._unknown_operation_responses == {}

    @pytest.mark.it(
        "Triggers callback upon publish completion [paho on_publish event triggered early]"
    )
    def test_triggers_callback_when_paho_on_publish_event_called_early(
        self, mocker, mock_mqtt_client, provider, message_info
    ):
        def publish_triggers_early_on_publish(topic, payload, qos):

            # Trigger on_publish before returning message_info
            mock_mqtt_client.on_publish(mock_mqtt_client, None, message_info.mid)

            # Check mid has been stored as an unknown response, callback not yet called
            assert callback.call_count == 0
            assert provider._pending_operation_callbacks == {}
            assert provider._unknown_operation_responses == {message_info.mid: message_info.mid}

            return message_info

        callback = mocker.MagicMock()
        mock_mqtt_client.publish.side_effect = publish_triggers_early_on_publish

        # Initiate publish
        provider.publish(fake_topic, self.msg_payload, callback=callback)

        # Check callback has now been called, and stored values cleared
        assert callback.call_count == 1
        assert provider._pending_operation_callbacks == {}
        assert provider._unknown_operation_responses == {}

    # @pytest.mark.it("Skips callback that is set to 'None' upon publish completion")
    # def test_none_callback_upon_paho_on_publish_event(self, mocker, mock_mqtt_client, provider, message_info):
    #     mock_mqtt_client.publish.return_value = message_info

    #     provider.publish(fake_topic, self.msg_payload, callback=None)
    #     mock_mqtt_client.on_publish(mock_mqtt_client, None, message_info.mid)

    #     # No assert required, just running successfully passes this test


# @patch.object(mqtt, "Client")
# @pytest.mark.parametrize(
#     "client_callback_name, client_callback_args, provider_callback_name, provider_callback_args",
#     [
#         pytest.param(
#             "on_connect",
#             [None, None, None, 0],
#             "on_mqtt_connected",
#             [],
#             id="on_connect => on_mqtt_connected",
#         ),
#         pytest.param(
#             "on_disconnect",
#             [None, None, 0],
#             "on_mqtt_disconnected",
#             [],
#             id="on_disconnect => on_mqtt_disconnected",
#         ),
#         pytest.param(
#             "on_publish",
#             [None, None, 9],
#             "on_mqtt_published",
#             [9],
#             id="on_publish => on_mqtt_published",
#         ),
#         pytest.param(
#             "on_subscribe",
#             [None, None, 1234, 1],
#             "on_mqtt_subscribed",
#             [1234],
#             id="on_subscribe => on_mqtt_subscribed",
#         ),
#         pytest.param(
#             "on_unsubscribe",
#             [None, None, 1235],
#             "on_mqtt_unsubscribed",
#             [1235],
#             id="on_unsubscribe => on_mqtt_unsubscribed",
#         ),
#     ],
# )
# def test_mqtt_client_callback_triggers_provider_callback(
#     MockMqttClient,
#     client_callback_name,
#     client_callback_args,
#     provider_callback_name,
#     provider_callback_args,
# ):
#     mock_mqtt_client = MockMqttClient.return_value

#     mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
#     stub_provider_callback = MagicMock()
#     setattr(mqtt_provider, provider_callback_name, stub_provider_callback)

#     getattr(mock_mqtt_client, client_callback_name)(*client_callback_args)

#     stub_provider_callback.assert_called_once_with(*provider_callback_args)


# @patch.object(mqtt, "Client")
# def test_disconnect_calls_loopstop_on_mqttclient(MockMqttClient):
#     mock_mqtt_client = MockMqttClient.return_value

#     mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
#     mqtt_provider.disconnect()

#     mock_mqtt_client.disconnect.assert_called_once_with()


# @patch.object(mqtt, "Client")
# def test_publish_calls_publish_on_mqtt_client(MockMqttClient):
#     mock_mqtt_client = MockMqttClient.return_value
#     mock_mqtt_client.publish = MagicMock(return_value=mqtt.MQTTMessageInfo(fake_mid))

#     topic = "topic/"
#     event = "Tarantallegra"

#     mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
#     pub_mid = mqtt_provider.publish(topic, event)

#     assert pub_mid == fake_mid
#     mock_mqtt_client.publish.assert_called_once_with(topic=topic, payload=event, qos=1)


# @patch.object(mqtt, "Client")
# def test_reconnect_calls_username_pw_set_and_reconnect_on_mqtt_client(MockMqttClient):
#     mock_mqtt_client = MockMqttClient.return_value

#     mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
#     mqtt_provider.reconnect(new_fake_password)

#     mock_mqtt_client.username_pw_set.assert_called_once_with(
#         username=fake_username, password=new_fake_password
#     )
#     mock_mqtt_client.reconnect.assert_called_once_with()


# @patch.object(mqtt, "Client")
# def test_subscribe_calls_subscribe_on_mqtt_client(MockMqttClient):
#     mock_mqtt_client = MockMqttClient.return_value
#     mock_mqtt_client.subscribe = MagicMock(return_value=(fake_rc, fake_mid))

#     mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
#     sub_mid = mqtt_provider.subscribe(fake_topic, fake_qos)

#     assert sub_mid == fake_mid
#     mock_mqtt_client.subscribe.assert_called_once_with(fake_topic, fake_qos)


# @patch.object(mqtt, "Client")
# def test_unsubscribe_calls_unsubscribe_on_mqtt_client(MockMqttClient):
#     mock_mqtt_client = MockMqttClient.return_value
#     mock_mqtt_client.unsubscribe = MagicMock(return_value=(fake_rc, fake_mid))

#     mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
#     unsub_mid = mqtt_provider.unsubscribe(fake_topic)

#     assert unsub_mid == fake_mid
#     mock_mqtt_client.unsubscribe.assert_called_once_with(fake_topic)
