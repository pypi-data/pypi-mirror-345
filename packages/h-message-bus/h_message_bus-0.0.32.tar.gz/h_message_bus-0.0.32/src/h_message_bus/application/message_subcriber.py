from abc import ABC, abstractmethod
from typing import Callable


class MessageSubscriber(ABC):
    """
    Abstract base class representing a message subscriber.

    This class defines the contract for subscribing to and unsubscribing from
    message topics. Subclasses are required to implement the methods for
    subscribing to topics with message handlers and unsubscribing from all
    active subscriptions.

    """

    @abstractmethod
    async def subscribe(self, topic: str, handler: Callable) -> None:
        """Subscribe to a topic with a message handler."""
        pass

    @abstractmethod
    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all subscriptions."""
        pass
