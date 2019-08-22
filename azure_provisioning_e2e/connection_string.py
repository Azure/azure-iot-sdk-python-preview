# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import urllib
import hmac
import hashlib
import time
import base64
from azure.iot.device.common.connection_string import ConnectionString
from azure.iot.device.common.sastoken import SasToken


def generate_auth_token(uri, sas_name, sas_value):
    """
    Given a URI, a sas_name, and a sas_value, return a shared access signature.
    """
    sas = base64.b64decode(sas_value)
    expiry = str(int(time.time() + 10000))
    string_to_sign = (uri + "\n" + expiry).encode("utf-8")
    signed_hmac_sha256 = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
    signature = urllib.parse.quote(base64.b64encode(signed_hmac_sha256.digest()))
    return "SharedAccessSignature sr={}&sig={}&se={}&skn={}".format(
        uri, signature, expiry, sas_name
    )


def connection_string_to_dictionary(str):
    """
    parse a connection string and return a dictionary of values
    """
    cn = {}
    for pair in str.split(";"):
        (key, value) = pair.rstrip("=").split("=")
        cn[key] = value
    return cn


# def connection_string_to_sas_token(str):
#     """
#     parse an IoTHub service connection string and return the host and a shared access
#     signature that can be used to connect to the given hub
#     """
#     cn = connection_string_to_dictionary(str)
#     sas = generate_auth_token(
#         cn["HostName"], cn["SharedAccessKeyName"], cn["SharedAccessKey"] + "="
#     )
#     return {"host": cn["HostName"], "sas": sas}


def connection_string_to_sas_token(str):
    """
    parse an IoTHub service connection string and return the host and a shared access
    signature that can be used to connect to the given hub
    """
    conn_str = ConnectionString(str)
    sas_token = SasToken(
        uri=conn_str.get("HostName"),
        key=conn_str.get("SharedAccessKey"),
        key_name=conn_str.get("SharedAccessKeyName"),
    )
    # sas = generate_auth_token(
    #     conn_str.get["HostName"], conn_str.get["SharedAccessKeyName"], conn_str.get["SharedAccessKey"] + "="
    # )
    return {"host": conn_str("HostName"), "sas": str(sas_token)}
