"""
분석 및 메트릭 모델
감정 분석, 대화 품질 등의 분석 데이터
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from .base import BaseDBModel, JSONField, BaseResponse


class EmotionType(str, Enum):
    """감정 타입"""
    POSITIVE = "긍정"
    NEGATIVE = "부정"
    NEUTRAL = "중립"
    ANGRY = "분노"
    ANXIOUS = "불안"
    SAD = "슬픔"
    HAPPY = "기쁨"
    SATISFIED = "만족"
    FRUSTRATED = "불만"


class EmotionAnalysis(BaseDBModel):
    """감정 분석 결과 모델"""
    
    __tablename__ = "emotion_analysis"
    
    session_id = Column(String(100), ForeignKey("chat_sessions.session_id"), index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), index=True)
    
    # 감정 분석 결과
    emotion = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    intensity = Column(Float, default=0.0)  # 0.0 - 1.0
    
    # 분석 메타데이터
    analyzer_version = Column(String(20))
    processing_time_ms = Column(Float)
    
    # 원본 데이터
    original_text = Column(Text)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    session = relationship("ChatSession")
    message = relationship("Message")


class ConversationMetrics(BaseDBModel):
    """대화 메트릭 모델"""
    
    __tablename__ = "conversation_metrics"
    
    session_id = Column(String(100), ForeignKey("chat_sessions.session_id"), index=True)
    
    # 대화 품질 메트릭
    user_satisfaction_score = Column(Float)  # 추정 만족도
    response_relevance_score = Column(Float)  # 응답 관련성
    conversation_coherence = Column(Float)  # 대화 일관성
    
    # 효율성 메트릭
    avg_response_time = Column(Float)  # 평균 응답 시간
    total_tokens_used = Column(Integer)  # 사용된 토큰 수
    api_calls_count = Column(Integer)  # API 호출 횟수
    
    # 해결 메트릭
    issue_resolved = Column(Boolean, default=False)
    escalation_needed = Column(Boolean, default=False)
    handoff_to_human = Column(Boolean, default=False)
    
    # RAG 효과성
    rag_usage_rate = Column(Float)  # RAG 사용 비율
    rag_relevance_score = Column(Float)  # RAG 결과 관련성
    
    # 계산된 날짜
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    session = relationship("ChatSession")


class DailyAnalytics(BaseDBModel):
    """일일 분석 집계 모델"""
    
    __tablename__ = "daily_analytics"
    
    date = Column(DateTime, index=True, nullable=False)
    
    # 세션 통계
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0.0)
    
    # 메시지 통계
    total_messages = Column(Integer, default=0)
    avg_messages_per_session = Column(Float, default=0.0)
    avg_response_time = Column(Float, default=0.0)
    
    # 감정 통계
    positive_emotion_rate = Column(Float, default=0.0)
    negative_emotion_rate = Column(Float, default=0.0)
    emotion_resolution_rate = Column(Float, default=0.0)
    
    # 만족도 통계
    avg_rating = Column(Float, default=0.0)
    satisfaction_rate = Column(Float, default=0.0)  # 4-5점 비율
    
    # 에스컬레이션 통계
    escalation_rate = Column(Float, default=0.0)
    human_handoff_rate = Column(Float, default=0.0)
    
    # 기술적 메트릭
    api_success_rate = Column(Float, default=0.0)
    avg_processing_time = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)


# Pydantic 모델들
class EmotionAnalysisCreate(BaseModel):
    """감정 분석 생성 모델"""
    session_id: str
    message_id: Optional[int] = None
    emotion: str
    confidence: float
    intensity: Optional[float] = 0.0
    analyzer_version: Optional[str] = None
    processing_time_ms: Optional[float] = None
    original_text: Optional[str] = None


class EmotionAnalysisResponse(BaseResponse):
    """감정 분석 응답 모델"""
    id: int
    session_id: str
    emotion: str
    confidence: float
    intensity: float
    analyzed_at: datetime


class ConversationMetricsCreate(BaseModel):
    """대화 메트릭 생성 모델"""
    session_id: str
    user_satisfaction_score: Optional[float] = None
    response_relevance_score: Optional[float] = None
    conversation_coherence: Optional[float] = None
    avg_response_time: Optional[float] = None
    total_tokens_used: Optional[int] = None
    api_calls_count: Optional[int] = None
    issue_resolved: Optional[bool] = False
    escalation_needed: Optional[bool] = False
    handoff_to_human: Optional[bool] = False
    rag_usage_rate: Optional[float] = None
    rag_relevance_score: Optional[float] = None


class ConversationMetricsResponse(BaseResponse):
    """대화 메트릭 응답 모델"""
    id: int
    session_id: str
    user_satisfaction_score: Optional[float]
    response_relevance_score: Optional[float]
    issue_resolved: bool
    escalation_needed: bool
    calculated_at: datetime


class AnalyticsDashboard(BaseModel):
    """분석 대시보드 데이터"""
    
    # 요약 통계
    total_sessions_today: int
    avg_satisfaction_today: float
    emotion_resolution_rate_today: float
    
    # 트렌드 데이터 (최근 7일)
    session_trend: list
    satisfaction_trend: list
    emotion_trend: list
    
    # 실시간 메트릭
    active_sessions: int
    avg_response_time: float
    api_success_rate: float
    
    # 인사이트
    top_emotions: list
    common_issues: list
    improvement_suggestions: list