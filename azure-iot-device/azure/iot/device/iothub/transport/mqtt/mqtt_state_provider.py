# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import six.moves.queue as queue
from .mqtt_provider import MQTTProvider
from transitions import Machine


"""
The below import is for generating the state machine graph.
"""
# from transitions.extensions import LockedGraphMachine as Machine

logger = logging.getLogger(__name__)


class TransportAction(object):
    """
    base class representing various actions that can be taken
    when the transport is connected.  When the MqttTransport user
    calls a function that requires the transport to be connected,
    a TransportAction object is created and added to the action
    queue.  Then, when the transport is actually connected, it
    loops through the objects in the action queue and executes them
    one by one.
    """

    def __init__(self, callback):
        self.callback = callback


class PublishAction(TransportAction):
    """
    TransportAction object used to send a telemetry message or an
    output message
    """

    def __init__(self, topic, payload, callback):
        TransportAction.__init__(self, callback)
        self.payload = payload


class SubscribeAction(TransportAction):
    """
    TransportAction object used to subscribe to a specific MQTT topic
    """

    def __init__(self, topic, qos, callback):
        TransportAction.__init__(self, callback)
        self.topic = topic
        self.qos = qos


class UnsubscribeAction(TransportAction):
    """
    TransportAction object used to unsubscribe from a specific MQTT topic
    """

    def __init__(self, topic, callback):
        TransportAction.__init__(self, callback)
        self.topic = topic


class MQTTStateProvider(object):
    def __init__(self, client_id, hostname, username, ca_cert=None):

        """
        Constructor for instantiating a state provider
        """
        self._mqtt_provider = None

        # Queue of actions that will be executed once the transport is connected.
        # Currently, we use a queue, which is FIFO, but the actual order doesn't matter
        # since each action stands on its own.
        self._pending_action_queue = queue.Queue()

        self._connect_callback = None
        self._disconnect_callback = None
        self.on_mqtt_message_received = None

        states = ["disconnected", "connecting", "connected", "disconnecting"]

        transitions = [
            {
                "trigger": "_trig_connect",
                "source": "disconnected",
                "dest": "connecting",
                "after": "_call_provider_connect",
            },
            {"trigger": "_trig_connect", "source": ["connecting", "connected"], "dest": None},
            {
                "trigger": "_trig_provider_connect_complete",
                "source": "connecting",
                "dest": "connected",
                "after": "_execute_actions_in_queue",
            },
            {
                "trigger": "_trig_disconnect",
                "source": ["disconnected", "disconnecting"],
                "dest": None,
            },
            {
                "trigger": "_trig_disconnect",
                "source": "connected",
                "dest": "disconnecting",
                "after": "_call_provider_disconnect",
            },
            {
                "trigger": "_trig_provider_disconnect_complete",
                "source": "disconnecting",
                "dest": "disconnected",
            },
            {
                "trigger": "_trig_add_action_to_pending_queue",
                "source": "connected",
                "before": "_add_action_to_queue",
                "dest": None,
                "after": "_execute_actions_in_queue",
            },
            {
                "trigger": "_trig_add_action_to_pending_queue",
                "source": "connecting",
                "before": "_add_action_to_queue",
                "dest": None,
            },
            {
                "trigger": "_trig_add_action_to_pending_queue",
                "source": "disconnected",
                "before": "_add_action_to_queue",
                "dest": "connecting",
                "after": "_call_provider_connect",
            },
            {
                "trigger": "_trig_reconnect",
                "source": "connected",
                "dest": "connecting",
                "after": "_call_provider_reconnect",
            },
            {
                "trigger": "_trig_reconnect",
                "source": ["disconnected", "disconnecting"],
                "dest": None,
            },
        ]

        def _on_transition_complete(event_data):
            if not event_data.transition:
                dest = "[no transition]"
            else:
                dest = event_data.transition.dest
            logger.info(
                "Transition complete.  Trigger=%s, Dest=%s, result=%s, error=%s",
                event_data.event.name,
                dest,
                str(event_data.result),
                str(event_data.error),
            )

        self._state_machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial="disconnected",
            send_event=True,  # This has nothing to do with telemetry events.  This tells the machine use event_data structures to hold transition arguments
            finalize_event=_on_transition_complete,
            queued=True,
        )

        # to render the state machine as a PNG:
        # 1. apt install graphviz
        # 2. pip install pygraphviz
        # 3. change import line at top of this file to import LockedGraphMachine as Machine
        # 4. uncomment the following line
        # 5. run this code
        # self.get_graph().draw('mqtt_transport.png', prog='dot')

        self._mqtt_provider = MQTTProvider(client_id, hostname, username, ca_cert=ca_cert)

    def _call_provider_connect(self, event_data):
        """
        Call into the provider to connect the transport.

        This is called by the state machine as part of a state transition

        :param EventData event_data:  Object created by the Transitions library with information about the state transition
        """
        logger.info("Calling provider connect")
        password = event_data.args[0]
        self._mqtt_provider.connect(password)

    def _call_provider_disconnect(self, event_data):
        """
        Call into the provider to disconnect the transport.

        This is called by the state machine as part of a state transition

        :param EventData event_data:  Object created by the Transitions library with information about the state transition
        """
        logger.info("Calling provider disconnect")
        self._mqtt_provider.disconnect()

    def _call_provider_reconnect(self, event_data):
        """
        Call into the provider to reconnect the transport.

        This is called by the state machine as part of a state transition

        :param EventData event_data:  Object created by the Transitions library with information about the state transition
        """
        logger.info("Calling provider connect")
        password = event_data.args[0]
        self._mqtt_provider.reconnect(password)

    def _on_provider_connect_complete(self):
        """
        Callback that is called by the provider when the connection has been established
        """
        logger.info("_on_provider_connect_complete")
        self._trig_provider_connect_complete()

        callback = self._connect_callback
        if callback:
            self._connect_callback = None
            callback()

    def _on_provider_disconnect_complete(self):
        """
        Callback that is called by the provider when the connection has been disconnected
        """
        logger.info("_on_provider_disconnect_complete")
        self._trig_provider_disconnect_complete()

        callback = self._disconnect_callback
        if callback:
            self._disconnect_callback = None
            callback()

    def _on_provider_message_received_callback(self, topic, payload):
        """
        Callback that is called by the provider when a message is received.  This message can be any MQTT message,
        including, but not limited to, a C2D message, an input message, a TWIN patch, a twin response (/res), and
        a method invocation.  This function needs to decide what kind of message it is based on the topic name and
        take the correct action.

        :param topic: MQTT topic name that the message arrived on
        :param payload: Payload of the message
        """
        logger.info("Message received on topic %s", topic)
        if self.on_mqtt_message_received:
            self.on_mqtt_message_received(topic, payload)

    def _add_action_to_queue(self, event_data):
        """
        Queue an action for running later.  All actions that need to run while connected end up in
        this queue, even if they're going to be run immediately.

        This is called by the state machine as part of a state transition

        :param EventData event_data:  Object created by the Transitions library with information about the state transition
        """
        self._pending_action_queue.put_nowait(event_data.args[0])

    def _execute_action(self, action):
        """
        Execute an action from the action queue.  This is called when the transport is connected and the
        state machine is able to execute individual actions.

        :param TransportAction action: object containing the details of the action to be executed
        """

        if isinstance(action, PublishAction):
            logger.info("running PublishAction")
            self._mqtt_provider.publish(action.topic, action.payload, callback=action.callback)

        elif isinstance(action, SubscribeAction):
            logger.info("running SubscribeAction topic=%s qos=%s", action.topic, action.qos)
            self._mqtt_provider.subscribe(action.topic, qos=action.qos, callback=action.callback)

        elif isinstance(action, UnsubscribeAction):
            logger.info("running UnsubscribeAction")
            self._mqtt_provider.unsubscribe(action.topic, callback=action.callback)

        else:
            logger.error("Removed unknown action type from queue.")

    def _execute_actions_in_queue(self, event_data):
        """
        Execute any actions that are waiting in the action queue.
        This is called by the state machine as part of a state transition.
        This function actually calls down into the provider to perform the necessary operations.

        :param EventData event_data:  Object created by the Transitions library with information about the state transition
        """
        logger.info("checking _pending_action_queue")
        while True:
            try:
                action = self._pending_action_queue.get_nowait()
            except queue.Empty:
                logger.info("done checking queue")
                return

            self._execute_action(action)

    def connect(self, password, callback=None):
        """
        Connect to the service.

        :param callback: callback which is called when the connection to the service is complete.
        """
        logger.info("connect called")
        self._connect_callback = callback
        self._trig_connect(password)

    def reconnect(self, password, callback=None):
        logger.info("reconnect called")
        self._connect_callback = callback
        self._trig_reconnect(password)

    def disconnect(self, callback=None):
        """
        Disconnect from the service.

        :param callback: callback which is called when the connection to the service has been disconnected
        """
        logger.info("disconnect called")
        self._disconnect_callback = callback
        self._trig_disconnect()

    def publish(self, topic, message_payload, callback=None):
        action = PublishAction(topic, message_payload, callback)
        self._trig_add_action_to_pending_queue(action)

    def subscribe(self, topic, qos=0, callback=None):
        action = SubscribeAction(topic, qos, callback)
        self._trig_add_action_to_pending_queue(action)

    def unsubscribe(self, topic, callback=None):
        action = UnsubscribeAction(topic, callback)
        self._trig_add_action_to_pending_queue(action)
