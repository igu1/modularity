from typing import Dict, List, Callable, Any, Optional
from threading import Lock
import uuid
from .message import Message, MessageType
class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._module_services: Dict[str, Any] = {}
        self._lock = Lock()
        self._message_history: List[Message] = []
    def subscribe(self, topic: str, callback: Callable[[Message], None]) -> str:
        with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            subscription_id = str(uuid.uuid4())
            self._subscribers[topic].append((subscription_id, callback))
            return subscription_id
    def unsubscribe(self, topic: str, subscription_id: str) -> bool:
        with self._lock:
            if topic in self._subscribers:
                self._subscribers[topic] = [
                    (sid, cb) for sid, cb in self._subscribers[topic] 
                    if sid != subscription_id
                ]
                return True
            return False
    def publish(self, message: Message) -> bool:
        with self._lock:
            self._message_history.append(message)
            if message.topic not in self._subscribers:
                return False
            delivered = False
            for subscription_id, callback in self._subscribers[message.topic]:
                try:
                    callback(message)
                    message.processed = True
                    delivered = True
                except Exception as e:
                    print(f"Error delivering message to {subscription_id}: {e}")
            return delivered
    def publish_event(self, topic: str, data: Dict[str, Any], source_module: str) -> bool:
        message = Message(
            message_type=MessageType.EVENT,
            topic=topic,
            data=data,
            source_module=source_module
        )
        return self.publish(message)
    def send_request(self, topic: str, data: Dict[str, Any], source_module: str, target_module: str) -> bool:
        message = Message(
            message_type=MessageType.REQUEST,
            topic=topic,
            data=data,
            source_module=source_module,
            target_module=target_module
        )
        return self.publish(message)
    def send_response(self, topic: str, data: Dict[str, Any], source_module: str, correlation_id: str) -> bool:
        message = Message(
            message_type=MessageType.RESPONSE,
            topic=topic,
            data=data,
            source_module=source_module,
            correlation_id=correlation_id
        )
        return self.publish(message)
    def register_module_service(self, module_name: str, service_instance: Any):
        with self._lock:
            self._module_services[module_name] = service_instance
    def get_module_service(self, module_name: str) -> Optional[Any]:
        with self._lock:
            return self._module_services.get(module_name)
    def get_available_modules(self) -> List[str]:
        with self._lock:
            return list(self._module_services.keys())
    def get_subscribed_topics(self) -> List[str]:
        with self._lock:
            return list(self._subscribers.keys())
    def get_message_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            return [msg.to_dict() for msg in self._message_history[-limit:]]
    def clear_history(self):
        with self._lock:
            self._message_history.clear()
_global_event_bus = EventBus()
def get_event_bus() -> EventBus:
    return _global_event_bus
