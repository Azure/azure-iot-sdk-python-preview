"""Azure IoT Device Library - Asynchronous

This library provides asynchronous clients for communicating with Azure IoT services
from an IoT device.
"""

import azure.iot.device.iothub as iothub
from azure.iot.device.iothub.aio import *

__all__ = iothub.aio.__all__
