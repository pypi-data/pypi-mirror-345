from abc import abstractmethod, ABC
from typing import Optional

from ..domain.models.hai_message import HaiMessage


class MessageProcessor(ABC):
    """
    Defines an abstract base class for processing messages.

    This class serves as a blueprint for creating message processing
    implementations. It enforces a concrete implementation of the
    'process' method, which is expected to handle a given message
    and optionally return a response. The specific logic of
    processing must be defined in derived subclasses.
    """

    @abstractmethod
    async def process(self, message: HaiMessage) -> Optional[HaiMessage]:
        """Process a message and optionally return a response."""
        pass
