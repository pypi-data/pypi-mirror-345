from typing import Dict, Any

from ..adapters.nats_message_adapter import NatsMessageAdapter
from ..application.message_processor import MessageProcessor
from ..application.message_subcriber import MessageSubscriber
from ..infrastructure.nats_client_repository import NatsClientRepository


class NatsSubscriberAdapter(MessageSubscriber):
    """
    Handles subscription to message topics using a NATS client.

    The class provides methods to subscribe to specific topics with a
    message processor and to manage subscriptions by unsubscribing from
    all topics. It works with a NATS client repository and acts as a
    bridge between the messaging system and the application.

    :ivar nats_client: The NATS client repository used for managing
        subscriptions.
    :type nats_client: NatsClientRepository
    :ivar subscriptions: A list of active subscription objects.
    :type subscriptions: list
    :ivar adapters: A dictionary mapping topic names to their respective
        message adapters.
    :type adapters: Dict[str, NatsMessageAdapter]
    """

    def __init__(self, nats_client: NatsClientRepository):
        self.nats_client = nats_client
        self.subscriptions = []
        self.adapters: Dict[str, NatsMessageAdapter] = {}

    async def subscribe(self, topic: str, processor: MessageProcessor) -> Any:
        """Subscribe to a topic with a message handler."""
        # Create an adapter for this use case
        message_adapter = NatsMessageAdapter(processor)
        self.adapters[topic] = message_adapter

        # Subscribe to the topic
        subscription = await self.nats_client.subscribe(
            topic,
            callback=message_adapter.handle_nats_message
        )

        self.subscriptions.append(subscription)
        return subscription

    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all subscriptions."""
        for subscription in self.subscriptions:
            await subscription.unsubscribe()

        self.subscriptions = []
        self.adapters = {}
