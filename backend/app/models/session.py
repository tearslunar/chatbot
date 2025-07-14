"""
세션 및 메시지 모델
채팅 세션과 메시지 관리
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from .base import BaseDBModel, JSONField, BaseResponse


class SessionStatus(str, Enum):
    """세션 상태"""
    ACTIVE = "active"
    ENDED = "ended"
    EXPIRED = "expired"


class MessageRole(str, Enum):
    """메시지 역할"""
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"


class ChatSession(BaseDBModel):
    """채팅 세션 모델"""
    
    __tablename__ = "chat_sessions"
    
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(100), index=True)  # 향후 사용자 인증을 위해
    status = Column(String(20), default=SessionStatus.ACTIVE.value)
    
    # 세션 메타데이터
    model_name = Column(String(50))
    persona_id = Column(String(50))
    total_messages = Column(Integer, default=0)
    
    # 세션 통계
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # 감정 관련
    dominant_emotion = Column(String(20))
    emotion_resolved = Column(Boolean, default=False)
    escalation_triggered = Column(Boolean, default=False)
    
    # 관계
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="session", cascade="all, delete-orphan")
    
    def end_session(self):
        """세션 종료"""
        self.status = SessionStatus.ENDED.value
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration_seconds = int((self.end_time - self.start_time).total_seconds())


class Message(BaseDBModel):
    """메시지 모델"""
    
    __tablename__ = "messages"
    
    session_id = Column(String(100), ForeignKey("chat_sessions.session_id"), index=True)
    role = Column(String(10), nullable=False)  # user, bot, system
    content = Column(Text, nullable=False)
    
    # 메시지 메타데이터
    model_used = Column(String(50))
    processing_time = Column(Float)  # 처리 시간 (초)
    
    # 감정 분석 결과
    emotion_data = Column(JSONField)  # JSON 형태로 저장
    
    # RAG 관련
    rag_results = Column(JSONField)  # 검색 결과
    search_strategy = Column(String(20))  # hybrid, faq_only, failed 등
    
    # 응답 품질
    escalation_needed = Column(Boolean, default=False)
    session_ended = Column(Boolean, default=False)
    
    # 관계
    session = relationship("ChatSession", back_populates="messages")


# Pydantic 모델들
class MessageCreate(BaseModel):
    """메시지 생성 모델"""
    session_id: str
    role: MessageRole
    content: str
    model_used: Optional[str] = None
    processing_time: Optional[float] = None
    emotion_data: Optional[Dict[str, Any]] = None
    rag_results: Optional[list] = None
    search_strategy: Optional[str] = None


class MessageResponse(BaseResponse):
    """메시지 응답 모델"""
    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime
    model_used: Optional[str] = None
    processing_time: Optional[float] = None
    emotion_data: Optional[Dict[str, Any]] = None


class SessionCreate(BaseModel):
    """세션 생성 모델"""
    session_id: str
    user_id: Optional[str] = None
    model_name: Optional[str] = None
    persona_id: Optional[str] = None


class SessionResponse(BaseResponse):
    """세션 응답 모델"""
    id: int
    session_id: str
    status: str
    total_messages: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    dominant_emotion: Optional[str] = None
    emotion_resolved: bool
    escalation_triggered: bool


class SessionStats(BaseModel):
    """세션 통계"""
    total_sessions: int
    active_sessions: int
    avg_duration_minutes: float
    avg_messages_per_session: float
    emotion_resolution_rate: float
    escalation_rate: float