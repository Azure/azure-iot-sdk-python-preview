# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import ssl
from six.moves import http_client, urllib


def _encode_params_in_url(url, params):
    if params:
        encoded_params = urllib.parse.urlencode(params)
        new_url = url + "?" + encoded_params
        return new_url
    else:
        return url


class HTTPTransport(object):
    """
    Class providing an generic HTTP request interface
    """

    def __init__(self, hostname, ca_cert=None):
        self._ca_cert = ca_cert
        ssl_context = self._create_ssl_context()
        self._connection = http_client.HTTPSConnection(hostname, context=ssl_context)

    def _create_ssl_context(self):
        """
        Creates an SSL context for use with the HTTP Client
        """
        ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
        ssl_context.load_verify_locations(cadata=self._ca_cert)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True
        return ssl_context

    def connect(self):
        self._connection.connect()

    def post(self, url, params=None, data=None):
        """
        Make an HTTP POST request

        :param str url: Relative URL representing request destination
        :param params:
        :param data:

        :returns: The HTTP response body.
        """
        encoded_url = _encode_params_in_url(url, params)
        self._connection.request(method="POST", url=encoded_url, params=params, body=data)
        response = self._connection.getresponse()
        if not response.status == 200:
            pass
        data = response.read()
        return data
