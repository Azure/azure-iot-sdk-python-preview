# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import logging
import threading
from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

"""
This module uses concurrent.futures.Future and the ThreadPoolExecutor because:

1. The thread pooling with a pool size of 1 gives us a single thread to run all
  pipeline operations and a different (single) thread to run all callbacks.  If
  the code attempts to run a second pipeline operation (or callback) while a
  different one is running, the ThreadPoolExecutor will queue the code until the
  first call is completed.

2. The concurent.futures.Future object properly handles both Exception and
  BaseException errors, re-raising them when the Future.result method is called.
  threading.Thread.get() was not an option because it doesn't re-raise
  BaseException errors when Thread.get is called.

3. concurrent.futures is available as a backport to 2.7.
"""


def get_named_executor(thread_name):
    executor = getattr(get_named_executor, thread_name, None)
    if not executor:
        logger.info("Creating {} executor".format(thread_name))
        executor = ThreadPoolExecutor(max_workers=1)
        setattr(get_named_executor, thread_name, ThreadPoolExecutor(max_workers=1))
    return executor


def get_thread_local_storage():
    if not getattr(get_thread_local_storage, "local", None):
        logger.info("Creating thread local storage")
        get_thread_local_storage.local = threading.local()
    return get_thread_local_storage.local


def _invoke_on_executor_thread(thread_name, block=True, _func=None):
    def decorator(func):
        function_name = getattr(func, "__name__", str(func))

        def wrapper(*args, **kwargs):
            if not getattr(get_thread_local_storage(), "in_{}_thread".format(thread_name), False):
                logger.info("Starting {} in {} thread".format(function_name, thread_name))

                def thread_proc():
                    setattr(get_thread_local_storage(), "in_{}_thread".format(thread_name), True)
                    return func(*args, **kwargs)

                # BKTODO: timeout with exception?
                future = get_named_executor(thread_name).submit(thread_proc)
                if block:
                    return future.result()
                else:
                    return future
            else:
                logger.debug("Already in {} thread for {}".format(thread_name, function_name))
                return func(*args, **kwargs)

        # Silly hack:  On 2.7, we can't use @functools.wraps on callables don't have a __name__ attribute
        # attribute(like MagicMock object), so we only do it when we have a name.  functools.update_wrapper
        # below is the same as using the @functools.wraps(func) decorator on the wrapper function above.
        if getattr(func, "__name__", None):
            return functools.update_wrapper(wrapped=func, wrapper=wrapper)
        else:
            return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def invoke_on_pipeline_thread(_func=None):
    return _invoke_on_executor_thread(thread_name="pipeline", _func=_func)


def invoke_on_pipeline_thread_nowait(_func=None):
    return _invoke_on_executor_thread(thread_name="pipeline", block=False, _func=_func)


def invoke_on_callback_thread_nowait(_func=None):
    return _invoke_on_executor_thread(thread_name="callback", block=False, _func=_func)


def _assert_executor_thread(thread_name, _func=None):
    def decorator(func):
        function_name = getattr(func, "__name__", str(func))

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not getattr(get_thread_local_storage(), "in_{}_thread".format(thread_name), False):
                assert False, """Function {function_name} is not running inside {thread_name} thread.
                    It should be. You should use invoke_on_{function_name}_thread(_nowait) to enter the
                    {thread_name} thread before calling this function.  If you're hitting this from
                    inside a test function, you may need to add the fake_pipeline_thread fixture to
                    your test.  (grep for apply_fake_pipeline_thread).""".format(
                    function_name=function_name, thread_name=thread_name
                )

            return func(*args, **kwargs)

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def assert_pipeline_thread(_func=None):
    return _assert_executor_thread(thread_name="pipeline", _func=_func)
