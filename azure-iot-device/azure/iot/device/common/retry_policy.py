# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""This module contains abstract classes for the various clients of the Azure IoT Hub Device SDK
"""

import six
import abc
import logging
import random
from . import errors

logger = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class AbstractRetryPolicy(object):
    @abc.abstractmethod
    def get_next_retry_timeoue(self, retry_count, is_throttled):
        """
        Computes the interval to wait before retrying at each new retry tentative.

        @param {number} retryCount    Current retry tentative.
        @param {boolean} isThrottled  Boolean indicating whether the Azure IoT hub is throttling operations.
        @returns {number}             The time to wait before attempting a retry in milliseconds.
        """
        pass

    @abc.abstractmethod
    def should_retry(self, error):
        """
        Based on the error passed as argument, determines if an error is transient and if the operation should be retried or not.

        @param {Error} error The error encountered by the operation.
        @returns {boolean}   Whether the operation should be retried or not.
        """
        pass


default_retry_error_filter = [
    errors.ConnectionDroppedError,
    errors.ConnectionFailedError,
    errors.TimeoutError,
    errors.InternalServiceError,
    errors.QuotaExceededError,
    errors.ThrottlineError,
    errors.ServiceUnavailableError,
]


class NoRetryPolicy(AbstractRetryPolicy):
    def get_next_retry_timeoue(self, retry_count, is_throttled):
        return -1

    def should_retry(self, error):
        return False


class ExponentialBackoffWithJitterParameters(object):
    """
    Initial retry interval (c): 100 ms by default.
    Minimal interval between each retry (cMin). 100 milliseconds by default
    * Maximum interval between each retry (cMax). 10 seconds by default
    * Jitter up factor (Ju). 0.25 by default.
    * Jitter down factor (Jd). 0.5 by default
    """

    def __init__(self):
        self.initial_retry_interval = 0.1
        self.minimum_interval_between_retries = 0.1
        self.maximum_interval_between_retries = 10
        self.jitter_up_factor = 0.25
        self.jitter_down_factor = 0.5


class ExponentialBackoffWithJitterThrottledParameters(object):
    """
    Initial retry interval (c): 5 s by default.
    Minimal interval between each retry (cMin). 10 seconds by default
    * Maximum interval between each retry (cMax). 60 seconds by default
    * Jitter up factor (Ju). 0.25 by default.
    * Jitter down factor (Jd). 0.5 by default
    """

    def __init__(self):
        self.initial_retry_interval = 5
        self.minimum_interval_between_retries = 10
        self.maximum_interval_between_retries = 60
        self.jitter_up_factor = 0.25
        self.jitter_down_factor = 0.5


"""
 * Implements an Exponential Backoff with Jitter retry strategy.
 * The function to calculate the next interval is the following (x is the xth retry):
 * F(x) = min(Cmin+ (2^(x-1)-1) * rand(C * (1 – Jd), C*(1-Ju)), Cmax)
"""


class ExponentialBackOffWithJitter(AbstractRetryPolicy):
    def __init__(
        self,
        immediate_first_retry=False,
        normal_parameters=None,
        throttled_parameters=None,
        error_filter=default_retry_error_filter,
    ):
        # Retry parameters used to calculate the delay between each retry in normal situations (ie. not throttled).
        self.normal_parameters = normal_parameters | ExponentialBackoffWithJitterParameters()

        # Retry parameters used to calculate the delay between each retry in throttled situations.
        self.throttled_parameters = (
            throttled_parameters | ExponentialBackoffWithJitterThrottledParameters()
        )

        # Boolean indicating whether the first retry should be immediate (if set to true) or after the normalParameters.c delay (if set to false).
        self.immediate_first_retry = immediate_first_retry

        self.error_filter = error_filter.copy()

    def get_next_retry_timeout(self, retry_count, is_throttled):
        if self.immediate_first_retry and retry_count == 0 and not is_throttled:
            return 0
        else:
            constants = self.throttled_parameters if is_throttled else self.normal_parameters
            min_random_factor = constants.initial_retry_interval * (
                1 - constants.jitter_down_factor
            )
            max_random_factor = constants.initial_retry_interval * (1 - constants.jitter_up_factor)
            random_jitter = random.random() * (max_random_factor - min_random_factor)

            return min(
                constants.minimum_interval_between_retries
                + (pow(2, retry_count - 1) - 1) * random_jitter,
                constants.maximum_interval_between_retries,
            )

    def should_retry(self, error):
        return error in self.error_filter
