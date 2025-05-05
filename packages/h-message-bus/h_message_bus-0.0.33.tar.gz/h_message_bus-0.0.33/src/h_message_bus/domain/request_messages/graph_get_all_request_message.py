
from typing import TypeVar, Dict, Any, Type, List

from ..models.request_message_topic import RequestMessageTopic
from ...domain.models.hai_message import HaiMessage

T = TypeVar('T', bound='HaiMessage')

class GraphGetAllRequestMessage(HaiMessage):
    """Message to get all nodes and relationships from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls) -> 'GraphGetAllRequestMessage':
        """Create a message requesting to get all nodes and relationships"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_GET_ALL,
            payload={}
        )

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphGetAllRequestMessage':
        return cls.create_message()
