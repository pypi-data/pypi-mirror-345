from abc import abstractmethod, ABC
from typing import Optional

from ..domain.models.hai_message import HaiMessage


class MessagePublisher(ABC):
    """
    Represents an abstract base class for a message publishing mechanism.

    This class serves as a template for creating message publishing systems
    that can either publish messages asynchronously or handle request-response
    patterns with optional timeouts. Subclasses must implement the abstract
    methods to provide specific functionality.
    """

    @abstractmethod
    async def publish(self, message: HaiMessage):
        """Publish a message."""
        pass

    @abstractmethod
    async def request(self, message: HaiMessage, timeout: float) -> Optional[HaiMessage]:
        """Send a request and wait for response."""
        pass
