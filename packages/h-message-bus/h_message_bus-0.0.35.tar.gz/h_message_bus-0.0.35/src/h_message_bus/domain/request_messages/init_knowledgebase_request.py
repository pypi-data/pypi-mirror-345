from typing import TypeVar, Dict, Any, Type

from ..models.request_message_topic import RequestMessageTopic
from ...domain.models.hai_message import HaiMessage

T = TypeVar('T', bound='HaiMessage')

class InitKnowledgeBaseRequestMessage(HaiMessage):


    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls) -> 'InitKnowledgeBaseRequestMessage':
        """Create a message requesting to clear the graph"""
        return cls.create(
            topic=RequestMessageTopic.INIT_KNOWLEDGE_BASE,
            payload={}
        )

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'InitKnowledgeBaseRequestMessage':
        return cls.create_message()