from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    EVENT = "event"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


class Message:
    
    def __init__(
        self,
        message_type: MessageType,
        topic: str,
        data: Dict[str, Any],
        source_module: str,
        target_module: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        self.message_type = message_type
        self.topic = topic
        self.data = data
        self.source_module = source_module
        self.target_module = target_module
        self.correlation_id = correlation_id or f"{source_module}_{datetime.now().timestamp()}"
        self.timestamp = datetime.now()
        self.processed = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_type': self.message_type.value,
            'topic': self.topic,
            'data': self.data,
            'source_module': self.source_module,
            'target_module': self.target_module,
            'correlation_id': self.correlation_id,
            'timestamp': str(self.timestamp),
            'processed': self.processed
        }
    
    def __repr__(self) -> str:
        return f"<Message({self.message_type.value}, {self.topic}, from={self.source_module})>"
