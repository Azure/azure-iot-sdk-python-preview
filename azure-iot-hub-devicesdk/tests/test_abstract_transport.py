# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest
from azure.iot.hub.devicesdk.transport.abstract_transport import AbstractTransport


def test_raises_exception_on_init_of_abstract_transport():
    with pytest.raises(TypeError) as error:
        AbstractTransport()
    msg = str(error.value)
    expected_msg = "Can't instantiate abstract class AbstractTransport with abstract methods connect, disconnect, send_event"
    assert msg == expected_msg
