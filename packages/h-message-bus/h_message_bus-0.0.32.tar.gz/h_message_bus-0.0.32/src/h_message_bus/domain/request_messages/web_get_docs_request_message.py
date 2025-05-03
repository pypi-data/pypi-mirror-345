from typing import Type, TypeVar, Dict, Any, Optional

from ..models.request_message_topic import RequestMessageTopic
from ...domain.models.hai_message import HaiMessage

T = TypeVar('T', bound='HaiMessage')

class WebGetDocsRequestMessage(HaiMessage):

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, collection_name: str, twitter_user: Optional[str], root_url: Optional[str]) -> 'WebGetDocsRequestMessage':
        return cls.create(
            topic=RequestMessageTopic.WEB_GET_DOCS,
            payload={
                "twitter_user": twitter_user,
                "root_url": root_url,
                "collection_name": collection_name,
            },
        )

    @property
    def twitter_user(self) -> str:
        return self.payload.get("twitter_user", "")

    @property
    def root_url(self) -> str:
        return self.payload.get("root_url", "")

    @property
    def collection_name(self) -> str:
        return self.payload.get("collection_name", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'WebGetDocsRequestMessage':
        payload = message.payload

        return cls.create_message(
            twitter_user=payload.get("twitter_user", ""),
            root_url=payload.get("root_url", ""),
            collection_name=payload.get("collection_name", "")
        )