from typing import Dict, List, Callable, Any, Optional
from threading import Lock
import uuid
from .message import Message, MessageType

class EventBus:
    def __init__(self):
        self._subs: Dict[str, List[tuple]] = {}
        self._svcs: Dict[str, Any] = {}
        self._lock = Lock()
        self._hist: List[Message] = []

    def subscribe(self, topic: str, cb: Callable[[Message], None]) -> str:
        with self._lock:
            sid = str(uuid.uuid4())
            self._subs.setdefault(topic, []).append((sid, cb))
            return sid

    def unsubscribe(self, topic: str, sid: str) -> bool:
        with self._lock:
            if topic in self._subs:
                self._subs[topic] = [s for s in self._subs[topic] if s[0] != sid]
                return True
            return False

    def publish(self, msg: Message) -> bool:
        with self._lock:
            self._hist.append(msg)
            if msg.topic not in self._subs: return False
            delivered = False
            for _, cb in self._subs[msg.topic]:
                try:
                    cb(msg); msg.processed = delivered = True
                except Exception as e: print(f"Bus Error: {e}")
            return delivered

    def publish_event(self, topic: str, data: Dict, src: str) -> bool:
        return self.publish(Message(MessageType.EVENT, topic, data, src))

    def send_request(self, topic: str, data: Dict, src: str, tgt: str) -> bool:
        return self.publish(Message(MessageType.REQUEST, topic, data, src, tgt))

    def send_response(self, topic: str, data: Dict, src: str, cid: str) -> bool:
        return self.publish(Message(MessageType.RESPONSE, topic, data, src, correlation_id=cid))

    def register_service(self, name: str, inst: Any):
        with self._lock: self._svcs[name] = inst

    def get_service(self, name: str) -> Optional[Any]:
        with self._lock: return self._svcs.get(name)

    def get_history(self, limit: int = 100) -> List[Dict]:
        with self._lock: return [m.to_dict() for m in self._hist[-limit:]]

_bus = EventBus()
def get_event_bus() -> EventBus: return _bus
