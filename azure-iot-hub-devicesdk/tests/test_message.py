# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.iot.hub.devicesdk.message import Message
import six.moves.urllib as urllib
from datetime import date


def test_construct_message_with_string():
    s = "After all this time? Always"
    msg = Message(s)
    assert msg.data == s


def test_construct_message_with_ids():
    s = "After all this time? Always"
    message_id = "Postage12323"
    msg = Message(s, message_id)
    assert msg.message_id == message_id


def test_construct_message_with_contenttype_encoding():
    s = "After all this time? Always"
    type = "application/json"
    encoding = "utf-16"
    msg = Message(s, None, encoding, type)
    assert msg.content_encoding == encoding
    assert msg.content_type == type


def test_int():
    s = 987
    msg = Message(s)
    assert msg.data == s


def test_someobject():
    s = "After all this time? Always"
    inner_mes = Message(s)
    msg = Message(inner_mes)
    assert msg.data == inner_mes


def test_encode_properties():
    message_to_send = Message("Alohomora")
    message_to_send.message_id = "ID-1234"
    message_to_send.correlation_id = "CORR-5980"
    message_to_send.user_id = "Hermione Granger"
    message_to_send.to = "P.O. BOX:Griffindor Common Room @ Hogwarts"

    message_to_send.custom_properties = dict()
    message_to_send.custom_properties["DementorAlert"] = "yes"
    message_to_send.custom_properties["QuidditchInRain"] = "no"

    topic = "devices/" + "MyPensieve"
    topic += "/messages/events/"

    system_properties = dict()
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

    print("\n")
    print(topic)


def test_decode_properties():
    topic = "devices/MyPensieve/messages/events/%24.mid=ID-1234&%24.cid=CORR-5980&%24.uid=Hermione+Granger&%24.to=P.O.+BOX%3AGriffindor+Common+Room+%40+Hogwarts&DementorAlert=yes&QuidditchInRain=no"

    message_received = Message("Alohomora")

    topic_parts = topic.split("/")

    if len(topic_parts) > 6:
        # module
        message_received.input_name = topic_parts[5]
        _extract_properties(topic_parts[6], message_received)
    else:
        # device
        _extract_properties(topic_parts[4], message_received)

    print(message_received)


def _extract_properties(properties, message_received):
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
        else:
            message_received.custom_properties[key] = value
