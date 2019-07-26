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


#
#
# def dictionary_to_connection_string(cn):
#     """
#     given a dictionary of name/value a pairs, make a connection string
#     """
#     return ";".join({"{}={}".format(key, value) for (key, value) in cn.items()})
#
#
# def obfuscate_connection_string(str):
#     """
#     obfuscate a connection_string for outputting to a log
#     """
#     cn = connection_string_to_dictionary(str)
#     for key in cn.keys():
#         cn[key] = "<REDACTED>"
#     return dictionary_to_connection_string(cn)


def connection_string_to_sas_token(str):
    """
    parse an IoTHub service connection string and return the host and a shared access
    signature that can be used to connect to the given hub
    """
    cn = connection_string_to_dictionary(str)
    sas = generate_auth_token(
        cn["HostName"], cn["SharedAccessKeyName"], cn["SharedAccessKey"] + "="
    )
    return {"host": cn["HostName"], "sas": sas}
