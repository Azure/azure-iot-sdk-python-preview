# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.iot.hub.devicesdk.transport.mqtt.mqtt_provider import MQTTProvider
from azure.iot.hub.devicesdk.auth.x509_authentication_provider import X509Credentials
import paho.mqtt.client as mqtt
import ssl
import pytest
from mock import MagicMock, patch

fake_hostname = "beauxbatons.academy-net"
fake_device_id = "MyFirebolt"
fake_password = "Fortuna Major"
fake_username = fake_hostname + "/" + fake_device_id
new_fake_password = "new fake password"
fake_cert_file = "cert_file"
fake_key_file = "key_file"
fake_passphrase = "passphrase"
fake_x509 = X509Credentials(fake_cert_file, fake_key_file, fake_passphrase)


@patch.object(ssl, "SSLContext")
@patch.object(mqtt, "Client")
def test_connect_triggers_client_connect(MockMqttClient, MockSsl):
    mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
    mqtt_provider.connect(fake_password)

    MockMqttClient.assert_called_once_with(fake_device_id, False, protocol=4)
    mock_mqtt_client = MockMqttClient.return_value

    MockSsl.assert_called_once_with(ssl.PROTOCOL_TLSv1_2)

    assert mock_mqtt_client.tls_set_context.call_count == 1
    context = mock_mqtt_client.tls_set_context.call_args[0][0]
    assert context.check_hostname is True
    assert context.verify_mode == ssl.CERT_REQUIRED
    context.load_default_certs.assert_called_once_with()
    mock_mqtt_client.tls_insecure_set.assert_called_once_with(False)
    mock_mqtt_client.username_pw_set.assert_called_once_with(
        username=fake_username, password=fake_password
    )
    mock_mqtt_client.connect.assert_called_once_with(host=fake_hostname, port=8883)
    mock_mqtt_client.username_pw_set.assert_called_once_with(
        username=fake_username, password=fake_password
    )
    mock_mqtt_client.loop_start.assert_called_once_with()

    assert mock_mqtt_client.on_connect is not None
    assert mock_mqtt_client.on_disconnect is not None
    assert mock_mqtt_client.on_publish is not None
    assert mock_mqtt_client.on_subscribe is not None


@patch.object(ssl, "SSLContext")
@patch.object(mqtt, "Client")
def test_connect_triggers_client_connect_with_x509(MockMqttClient, MockSsl):
    mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
    mqtt_provider.connect(None, fake_x509)

    MockMqttClient.assert_called_once_with(fake_device_id, False, protocol=4)
    mock_mqtt_client = MockMqttClient.return_value

    MockSsl.assert_called_once_with(ssl.PROTOCOL_TLSv1_2)

    assert mock_mqtt_client.tls_set_context.call_count == 1
    context = mock_mqtt_client.tls_set_context.call_args[0][0]
    assert context.check_hostname is True
    assert context.verify_mode == ssl.CERT_REQUIRED
    context.load_default_certs.assert_called_once_with()
    context.load_cert_chain.assert_called_once_with(fake_cert_file, fake_key_file, fake_passphrase)
    mock_mqtt_client.tls_insecure_set.assert_called_once_with(False)
    mock_mqtt_client.connect.assert_called_once_with(host=fake_hostname, port=8883)
    mock_mqtt_client.username_pw_set.assert_called_once_with(username=fake_username, password=None)
    mock_mqtt_client.loop_start.assert_called_once_with()

    assert mock_mqtt_client.on_connect is not None
    assert mock_mqtt_client.on_disconnect is not None
    assert mock_mqtt_client.on_publish is not None
    assert mock_mqtt_client.on_subscribe is not None


@patch.object(mqtt, "Client")
@pytest.mark.parametrize(
    "client_callback_name, client_callback_args, provider_callback_name, provider_callback_args",
    [
        ("on_connect", [None, None, None, 0], "on_mqtt_connected", []),
        ("on_disconnect", [None, None, 0], "on_mqtt_disconnected", []),
        ("on_publish", [None, None, 9], "on_mqtt_published", [9]),
        ("on_subscribe", [None, None, 0], "on_mqtt_subscribed", []),
    ],
)
def test_mqtt_client_callback_triggers_provider_callback(
    MockMqttClient,
    client_callback_name,
    client_callback_args,
    provider_callback_name,
    provider_callback_args,
):
    mock_mqtt_client = MockMqttClient.return_value

    mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
    stub_provider_callback = MagicMock()
    setattr(mqtt_provider, provider_callback_name, stub_provider_callback)

    getattr(mock_mqtt_client, client_callback_name)(*client_callback_args)

    stub_provider_callback.assert_called_once_with(*provider_callback_args)


@patch.object(mqtt, "Client")
def test_disconnect_calls_loopstop_on_mqttclient(MockMqttClient):
    mock_mqtt_client = MockMqttClient.return_value

    mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
    mqtt_provider.disconnect()

    mock_mqtt_client.loop_stop.assert_called_once_with()
    mock_mqtt_client.disconnect.assert_called_once_with()


@patch.object(mqtt, "Client")
def test_publish_calls_publish_on_mqtt_client(MockMqttClient):
    mock_mqtt_client = MockMqttClient.return_value

    topic = "topic/"
    event = "Tarantallegra"

    mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
    mqtt_provider.publish(topic, event)

    mock_mqtt_client.publish.assert_called_once_with(topic=topic, payload=event, qos=1)


@patch.object(mqtt, "Client")
def test_reconnect_calls_username_pw_set_and_reconnect_on_mqtt_client(MockMqttClient):
    mock_mqtt_client = MockMqttClient.return_value

    mqtt_provider = MQTTProvider(fake_device_id, fake_hostname, fake_username)
    mqtt_provider.reconnect(new_fake_password)

    mock_mqtt_client.username_pw_set.assert_called_once_with(
        username=fake_username, password=new_fake_password
    )
    mock_mqtt_client.reconnect.assert_called_once_with()
