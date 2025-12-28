from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class MessageType(Enum):
    EVENT = "event"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"

class Message:
    def __init__(self, message_type: MessageType, topic: str, data: Dict[str, Any], source: str, target: Optional[str] = None, correlation_id: Optional[str] = None):
        self.type, self.topic, self.data, self.source, self.target = message_type, topic, data, source, target
        self.correlation_id = correlation_id or f"{source}_{datetime.now().timestamp()}"
        self.timestamp, self.processed = datetime.now(), False

    def to_dict(self) -> Dict[str, Any]:
        return {**self.__dict__, 'type': self.type.value, 'timestamp': str(self.timestamp)}

    def __repr__(self) -> str:
        return f"<Message({self.type.value}, {self.topic}, from={self.source})>"
