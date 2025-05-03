from dataclasses import dataclass
from typing import TypeVar, Dict, Any, Type, List

from ..models.request_message_topic import RequestMessageTopic
from ..models.twitter_message_metadata import TwitterMessageMetaData
from ...domain.models.hai_message import HaiMessage

T = TypeVar('T', bound='HaiMessage')
@dataclass
class TwitterUserTweetsResponseMessage(HaiMessage):
    """Message containing tweets from a Twitter user"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, user_id: str, tweets: List[Dict[str, Any]],
                       success: bool = True, error: str = None) -> 'TwitterUserTweetsResponseMessage':
        """Create a message with tweets from a Twitter user"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_USER_TWEETS_RESPONSE,
            payload={
                "user_id": user_id,
                "tweets": tweets,
                "success": success,
                "error": error
            },
        )

    @property
    def user_id(self) -> str:
        """Get the user ID from the payload"""
        return self.payload.get("user_id")

    @property
    def tweets(self) -> List[Dict[str, Any]]:
        """Get the tweets from the payload"""
        return self.payload.get("tweets", [])

    @property
    def success(self) -> bool:
        """Get whether the request was successful"""
        return self.payload.get("success", False)

    @property
    def error(self) -> str:
        """Get any error message"""
        return self.payload.get("error")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterUserTweetsResponseMessage':
        """Create a TwitterUserTweetsResponseMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            user_id=payload.get("user_id", ""),
            tweets=payload.get("tweets", []),
            success=payload.get("success", False),
            error=payload.get("error")
        )

    @classmethod
    def from_twitter_messages(cls, user_id: str,
                              twitter_messages: List[TwitterMessageMetaData]) -> 'TwitterUserTweetsResponseMessage':
        """Create a response message from a list of TwitterMessage objects"""
        tweets = []

        for message in twitter_messages:
            user = message.user

            tweet_data = {
                "tweet_id": str(message.tweet_id),
                "message": message.message,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "view_count": message.view_count,
                "retweet_count": message.retweet_count,
                "reply_count": message.reply_count,
                "user": message.user.to_dict() if user else None,
            }

            tweets.append(tweet_data)

        return cls.create_message(
            user_id=user_id,
            tweets=tweets,
            success=True
        )
