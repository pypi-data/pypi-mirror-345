import logging
from typing import Optional, Callable, Any

import nats
from nats.aio.client import Client as NatsClient

from ..infrastructure.nats_config import NatsConfig


class NatsClientRepository:
    """
    Repository for managing connection and interaction with a NATS server.

    This class provides methods to establish a connection with a NATS server,
    publish and subscribe to subjects, send requests and handle responses, and
    cleanly disconnect from the server. It abstracts the connection and ensures
    seamless communication with the NATS server.

    :ivar config: Configuration details for the NATS client, including server
        connection parameters, timeouts, and limits.
    :type config: NatsConfig
    :ivar client: Instance of the NATS client used for communication. Initialized
        as None and assigned upon connecting to a NATS server.
    :type client: Optional[NatsClient]
    :ivar subscriptions: List of active subscriptions for NATS subjects.
    :type subscriptions: list
    """

    def __init__(self, config: NatsConfig):
        self.config = config
        self.client: NatsClient | None = None

        self.subscriptions = []
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> None:
        """Connect to NATS server."""
        if self.client and self.client.is_connected:
            return
        self.logger.info(f"Connecting to NATS server at {self.config.server}")

        self.client = await nats.connect(
            servers=self.config.server,
            max_reconnect_attempts=self.config.max_reconnect_attempts,
            reconnect_time_wait=self.config.reconnect_time_wait,
            connect_timeout=self.config.connection_timeout,
            ping_interval=self.config.ping_interval,
            max_outstanding_pings=self.config.max_outstanding_pings
        ) #ignore client type warning

    async def publish(self, subject: str, payload: bytes) -> None:
        """Publish raw message to NATS."""
        if not self.client or not self.client.is_connected:
            await self.connect()

        try:
            await self.client.publish(subject, payload)
        except Exception as e:
            print(f"Failed to publish message: {e}")
            return

    async def subscribe(self, subject: str, callback: Callable) -> Any:
        """Subscribe to a subject with a callback."""
        if not self.client or not self.client.is_connected:
            await self.connect()

        subscription = await self.client.subscribe(subject, cb=callback)
        self.subscriptions.append(subscription)
        return subscription

    async def request(self, subject: str, payload: bytes, timeout: float = 2.0) -> Optional[bytes]:
        """Send a request and get raw response."""
        if not self.client or not self.client.is_connected:
            await self.connect()

        try:
            response = await self.client.request(subject, payload, timeout=timeout)
            return response.data
        except Exception as e:
            print(f"NATS request failed: {e}")
            return None

    async def close(self) -> None:
        """Close all subscriptions and NATS connection."""
        if self.client and self.client.is_connected:
            # Unsubscribe from all subscriptions
            for sub in self.subscriptions:
                await sub.unsubscribe()

            # Drain and close connection
            await self.client.drain()
            self.client = None
            self.subscriptions = []
