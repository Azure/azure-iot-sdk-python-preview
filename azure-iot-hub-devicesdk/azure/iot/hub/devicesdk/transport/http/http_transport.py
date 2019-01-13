# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import requests
from datetime import date
from azure.iot.hub.devicesdk.transport.abstract_transport import AbstractTransport
from azure.iot.hub.devicesdk.message import Message

"""
The below import is for generating the state machine graph.
"""
# from transitions.extensions import LockedGraphMachine as Machine

logger = logging.getLogger(__name__)


class HTTPTransport(AbstractTransport):
    def __init__(self, auth_provider):
        """
        Constructor for instantiating a transport
        :param auth_provider: The authentication provider
        """
        AbstractTransport.__init__(self, auth_provider)
        self.on_transport_connected = None
        self.on_transport_disconnected = None

    def _headers_from_message(self, message):
        headers = dict()

        if message.message_id:
            headers["IoTHub-MessageId"] = str(message.message_id)

        if message.correlation_id:
            headers["IoTHub-CorrelationId"] = str(message.correlation_id)

        if message.user_id:
            headers["IoTHub-UserId"] = str(message.user_id)

        if message.to:
            headers["IoTHub-To"] = message.to

        if message.expiry_time_utc:
            headers["IoTHub-Expiry"] = (
                message.expiry_time_utc.isoformat()
                if isinstance(message.expiry_time_utc, date)
                else message.expiry_time_utc
            )

        if message.ack:
            headers["IoTHub-Ack"] = message.ack

        if message.content_type:
            headers["iothub-contenttype"] = message.content_type

        if message.content_encoding:
            headers["iothub-contentencoding"] = message.content_encoding

        return headers

    def connect(self, callback=None):
        logger.info("HTTPTransport: connect")
        if self.on_transport_connected:
            self.on_transport_connected("connected")
        if callback:
            callback()

    def disconnect(self, callback=None):
        logger.info("HTTPTransport: disconnect")
        if self.on_transport_disconnected:
            self.on_transport_disconnected("disconnected")
        if callback:
            callback()

    def send_event(self, message, callback=None):
        path = "/devices/" + self._auth_provider.device_id
        if self._auth_provider.module_id is not None:
            path += "/modules/" + self._auth_provider.module_id
        path += "/messages/events/"

        hostname = None
        if hasattr(self._auth_provider, "gateway_hostname"):
            hostname = self._auth_provider.gateway_hostname
        if not hostname or len(hostname) == 0:
            hostname = self._auth_provider.hostname

        request_url = "https://" + hostname + path
        request_params = {"api-version": "2018-06-30"}

        logger.info("HTTPTransport: send_event: %s", path)

        message_to_send = message

        if not isinstance(message, Message):
            message_to_send = Message(message)

        headers = self._headers_from_message(message_to_send)

        # TODO: user agent
        # TODO: verify with the x509_auth branch
        client_cert = None
        if hasattr(self._auth_provider, "cert"):
            client_cert = (self._auth_provider.cert, self._auth_provider.key)
        else:
            headers["Authorization"] = self._auth_provider.get_current_sas_token()

        try:
            if hasattr(self._auth_provider, "ca_cert") and self._auth_provider.ca_cert is not None:
                ca_cert = self._auth_provider.ca_cert
                resp = requests.post(
                    request_url,
                    params=request_params,
                    data=message_to_send.data,
                    headers=headers,
                    verify=ca_cert,
                )
            else:
                if client_cert:
                    resp = requests.post(
                        request_url,
                        params=request_params,
                        data=message_to_send.data,
                        headers=headers,
                        cert=client_cert,
                    )
                else:
                    resp = requests.post(
                        request_url,
                        params=request_params,
                        data=message_to_send.data,
                        headers=headers,
                    )
            resp.raise_for_status()
            logger.info("HTTP request was successful. status code: " + str(resp.status_code))
            callback()
        except requests.exceptions.SSLError as ex:
            raise ex
        except requests.exceptions.ConnectionError as ex:
            raise ex
        except requests.exceptions.HTTPError as ex:
            logger.error("HTTP request failed with status code: " + str(resp.status_code))
            # Probably need custom exception handling here to transport transport-specific exception into transport-agnostic exception?
            # Do transports throw or callback with errors?
            raise ex

    def send_output_event(self, output, message, callback=None):
        raise NotImplementedError("HTTP Transport does not support input/output feature")
