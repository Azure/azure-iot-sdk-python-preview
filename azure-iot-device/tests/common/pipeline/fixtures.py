# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from tests.common.pipeline import helpers
from azure.iot.device.common.pipeline import (
    pipeline_events_base,
    pipeline_ops_base,
    pipeline_thread,
)


@pytest.fixture
def callback(mocker):
    return mocker.Mock()


@pytest.fixture
def fake_exception():
    return Exception()


@pytest.fixture
def fake_base_exception():
    return helpers.UnhandledException()


class FakeEvent(pipeline_events_base.PipelineEvent):
    def __init__(self):
        super(FakeEvent, self).__init__()


@pytest.fixture
def event():
    return FakeEvent()


class FakeOperation(pipeline_ops_base.PipelineOperation):
    def __init__(self, callback=None):
        super(FakeOperation, self).__init__(callback=callback)


@pytest.fixture
def op(callback):
    op = FakeOperation(callback=callback)
    op.name = "op"
    return op


@pytest.fixture
def op2(callback):
    op = FakeOperation(callback=callback)
    op.name = "op2"
    return op


@pytest.fixture
def op3(callback):
    op = FakeOperation(callback=callback)
    op.name = "op3"
    return op


@pytest.fixture
def finally_op(callback):
    op = FakeOperation(callback=callback)
    op.name = "finally_op"
    return op


@pytest.fixture
def new_op(callback):
    op = FakeOperation(callback=callback)
    op.name = "new_op"
    return op


@pytest.fixture
def fake_pipeline_thread(mocker):
    # BKTODO doc
    class mock_local(object):
        def __init__(self):
            self.in_pipeline_thread = True

    mocker.patch.object(pipeline_thread, "get_thread_local_storage", mock_local)
