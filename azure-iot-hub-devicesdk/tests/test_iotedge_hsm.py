# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.iot.hub.devicesdk.auth.iotedge_hsm import IotEdgeHsm
import pytest
import requests
import os
import json
import base64

from six import add_move, MovedModule
from six.moves import mock
from mock import patch

add_move(MovedModule("mock", "mock", "unittest.mock"))

fake_module_id = "__FAKE_MODULE__ID__"
fake_api_version = "__FAKE_API_VERSION__"
fake_module_generation_id = "__FAKE_MODULE_GENERATION_ID__"
fake_http_workload_uri = "http://__FAKE_WORKLOAD_URI__/"
fake_certificate = "__FAKE_CERTIFICATE__"
fake_message = "__FAKE_MESSAGE__"
fake_digest = "__FAKE_DIGEST__"

required_environment_variables = {
    "IOTEDGE_MODULEID": fake_module_id,
    "IOTEDGE_APIVERSION": fake_api_version,
    "IOTEDGE_MODULEGENERATIONID": fake_module_generation_id,
    "IOTEDGE_WORKLOADURI": fake_http_workload_uri,
}


@patch.dict(os.environ, required_environment_variables)
def test_initializer_doesnt_throw_when_all_environment_variables_are_present():
    IotEdgeHsm()


def test_initializer_throws_with_missing_environment_variables():
    for key in required_environment_variables:
        env = required_environment_variables.copy()
        del env[key]
        with patch.dict(os.environ, env):
            with pytest.raises(KeyError, match=key):
                IotEdgeHsm()


@patch.object(requests, "get")
@patch.dict(os.environ, required_environment_variables)
def test_get_trust_bundle_returns_certificate(mock_get):
    mock_response = mock.Mock(spec=requests.Response)
    mock_response.json.return_value = {"certificate": fake_certificate}
    mock_get.return_value = mock_response

    hsm = IotEdgeHsm()
    cert = hsm.get_trust_bundle()

    assert cert == fake_certificate
    mock_response.raise_for_status.assert_called_once_with()  # this verifies that a failed status code will throw
    mock_get.assert_called_once_with(
        fake_http_workload_uri + "trust-bundle", params={"api-version": fake_api_version}
    )


@patch.object(requests, "post")
@patch.dict(os.environ, required_environment_variables)
def test_sign_sends_post_with_proper_url_and_data(mock_post):
    mock_response = mock.Mock(spec=requests.Response)
    mock_response.json.return_value = {"digest": fake_digest}
    mock_post.return_value = mock_response

    hsm = IotEdgeHsm()
    digest = hsm.sign(fake_message)

    assert digest == fake_digest
    mock_response.raise_for_status.assert_called_once_with()  # this verifies that a failed status code will throw

    fake_url = (
        fake_http_workload_uri
        + "modules/"
        + fake_module_id
        + "/genid/"
        + fake_module_generation_id
        + "/sign"
    )
    fake_data = json.dumps(
        {
            "keyId": "primary",
            "algo": "HMACSHA256",
            "data": base64.b64encode(fake_message.encode()).decode(),
        }
    )
    mock_post.assert_called_once_with(
        fake_url, data=fake_data, params={"api-version": fake_api_version}
    )


@patch.object(requests, "get")
@patch.dict(os.environ, required_environment_variables)
def test_workload_uri_values_get_adjusted_correctly(mock_get):
    for (original_uri, adjusted_uri) in [
        ("http://foo", "http://foo/"),
        ("http://foo/", "http://foo/"),
        ("unix:///foo/bar", "http+unix://%2Ffoo%2Fbar/"),
        ("unix:///foo/bar/", "http+unix://%2Ffoo%2Fbar/"),
    ]:
        mock_get.reset_mock()

        env = required_environment_variables.copy()
        env["IOTEDGE_WORKLOADURI"] = original_uri
        with patch.dict(os.environ, env):
            hsm = IotEdgeHsm()
            hsm.get_trust_bundle()

            mock_get.assert_called_once_with(
                adjusted_uri + "trust-bundle", params={"api-version": fake_api_version}
            )
