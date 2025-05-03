import asyncio
from typing import Optional

from ..application.message_publisher import MessagePublisher
from ..domain.models.hai_message import HaiMessage
from ..infrastructure.nats_client_repository import NatsClientRepository


class NatsPublisherAdapter(MessagePublisher):
    """
    Adapter for publishing and requesting messages using a NATS client.

    This class interacts with a NATS client to publish messages to specified
    topics or send requests and wait for responses. It is designed to work
    with the `HaiMessage` format for message objects. The adapter encapsulates
    underlying communication details and provides an easy-to-use interface
    for message-based interactions.

    :ivar nats_client: Instance of NatsClientRepository used for interacting
                       with the NATS system.
    :type nats_client: NatsClientRepository
    """

    def __init__(self, nats_client: NatsClientRepository):
        self.nats_client = nats_client

    async def publish(self, message: HaiMessage, wait_time: float = 0.1):
        """Publish a message to NATS."""
        try:
            await self.nats_client.publish(
                message.topic,
                message.to_json().encode()
            )
            await asyncio.sleep(wait_time)
        except Exception as e:
            print(f"Failed to publish message: {e}")
            return

    async def request(self, message: HaiMessage, timeout: float = 2.0) -> Optional[HaiMessage]:
        """Send a request and wait for a response."""
        try:
            response = await self.nats_client.request(
                message.topic,
                message.to_json().encode(),
                timeout=timeout
            )
            if response:
                return HaiMessage.from_json(response.decode())
            return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None
