# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class DeviceJobStatistics(Model):
    """The job counts, e.g., number of failed/succeeded devices.

    :param device_count: Number of devices in the job
    :type device_count: int
    :param failed_count: The number of failed jobs
    :type failed_count: int
    :param succeeded_count: The number of Successed jobs
    :type succeeded_count: int
    :param running_count: The number of running jobs
    :type running_count: int
    :param pending_count: The number of pending (scheduled) jobs
    :type pending_count: int
    """

    _attribute_map = {
        'device_count': {'key': 'deviceCount', 'type': 'int'},
        'failed_count': {'key': 'failedCount', 'type': 'int'},
        'succeeded_count': {'key': 'succeededCount', 'type': 'int'},
        'running_count': {'key': 'runningCount', 'type': 'int'},
        'pending_count': {'key': 'pendingCount', 'type': 'int'},
    }

    def __init__(self, **kwargs):
        super(DeviceJobStatistics, self).__init__(**kwargs)
        self.device_count = kwargs.get('device_count', None)
        self.failed_count = kwargs.get('failed_count', None)
        self.succeeded_count = kwargs.get('succeeded_count', None)
        self.running_count = kwargs.get('running_count', None)
        self.pending_count = kwargs.get('pending_count', None)
