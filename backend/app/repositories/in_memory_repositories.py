from typing import Dict, List, Optional, Any
import time
import uuid

class InMemorySessionRepository:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def create(self, obj_in: Dict[str, Any]) -> Dict[str, Any]:
        session_id = obj_in.get("session_id", str(uuid.uuid4()))
        session_data = {
            "session_id": session_id,
            "model_name": obj_in.get("model_name"),
            "status": obj_in.get("status", "active"),
            "start_time": obj_in.get("start_time", time.time()),
            "total_messages": obj_in.get("total_messages", 0),
            "persona_id": obj_in.get("persona_id"),
            "last_updated": time.time()
        }
        self.sessions[session_id] = session_data
        return session_data

    def update(self, db: Any, session_obj: Dict[str, Any], obj_in: Dict[str, Any]) -> Dict[str, Any]:
        session_obj.update(obj_in)
        session_obj["last_updated"] = time.time()
        return session_obj

class InMemoryMessageRepository:
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []

    def create(self, obj_in: Dict[str, Any]) -> Dict[str, Any]:
        message_data = {
            "id": str(uuid.uuid4()),
            "session_id": obj_in.get("session_id"),
            "role": obj_in.get("role"),
            "content": obj_in.get("content"),
            "model_used": obj_in.get("model_used"),
            "emotion_data": obj_in.get("emotion_data"),
            "processing_time": obj_in.get("processing_time"),
            "rag_results": obj_in.get("rag_results"),
            "search_strategy": obj_in.get("search_strategy"),
            "escalation_needed": obj_in.get("escalation_needed"),
            "session_ended": obj_in.get("session_ended"),
            "timestamp": time.time()
        }
        self.messages.append(message_data)
        return message_data

    def get_messages_by_session_id(self, db: Any, session_id: str) -> List[Dict[str, Any]]:
        return [msg for msg in self.messages if msg["session_id"] == session_id]
