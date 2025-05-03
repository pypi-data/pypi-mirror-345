import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, TypeVar

T = TypeVar('T', bound='HaiMessage')


@dataclass
class HaiMessage:
    """
    Represents a domain message with metadata and payload.

    This class is used for handling messages with a specific topic and payload,
    along with metadata such as an identifier and a timestamp. It provides
    functionality for creation, serialization to JSON, and deserialization from JSON.

    :ivar id: Unique identifier for the message.
    :type id: str
    :ivar topic: The topic associated with the message.
    :type topic: str
    :ivar payload: The payload of the message, represented as a dictionary.
    :type payload: Dict[Any, Any]
    :ivar timestamp: The timestamp indicating when the message was created.
    :type timestamp: str
    """
    id: str
    topic: str
    payload: Dict[Any, Any]
    timestamp: str = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

    @classmethod
    def create(cls, topic: str, payload: Dict[Any, Any]) -> T:
        """Factory method to create a new domain message."""
        return cls(
            id=str(uuid.uuid4()),
            topic=topic,
            payload=payload,
            timestamp=datetime.utcnow().isoformat()
        )

    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps({
            "id": self.id,
            "topic": self.topic,
            "payload": self.payload,
            "timestamp": self.timestamp
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'HaiMessage':
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            topic=data["topic"],
            payload=data["payload"],
            timestamp=data.get("timestamp", datetime.utcnow().isoformat())
        )
