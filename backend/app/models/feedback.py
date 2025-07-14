"""
사용자 피드백 및 평점 모델
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel, validator

from .base import BaseDBModel, BaseResponse


class RatingValue(int, Enum):
    """평점 값"""
    VERY_DISSATISFIED = 1
    DISSATISFIED = 2
    NEUTRAL = 3
    SATISFIED = 4
    VERY_SATISFIED = 5


class UserFeedback(BaseDBModel):
    """사용자 피드백 모델"""
    
    __tablename__ = "user_feedback"
    
    session_id = Column(String(100), ForeignKey("chat_sessions.session_id"), index=True)
    user_id = Column(String(100), index=True)
    
    # 피드백 내용
    feedback_text = Column(Text)
    rating = Column(Integer, nullable=False)  # 1-5 점
    
    # 피드백 카테고리 (향후 확장용)
    category = Column(String(50))  # response_quality, speed, helpfulness 등
    
    # 메타데이터
    submitted_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))  # IPv6 지원
    user_agent = Column(String(500))
    
    # 관계
    session = relationship("ChatSession", back_populates="feedback")


class Rating(BaseDBModel):
    """평점 집계 모델"""
    
    __tablename__ = "ratings"
    
    # 집계 단위
    date = Column(DateTime, index=True)  # 일별 집계
    model_name = Column(String(50), index=True)
    
    # 평점 통계
    total_ratings = Column(Integer, default=0)
    rating_sum = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    # 점수별 개수
    rating_1_count = Column(Integer, default=0)
    rating_2_count = Column(Integer, default=0)
    rating_3_count = Column(Integer, default=0)
    rating_4_count = Column(Integer, default=0)
    rating_5_count = Column(Integer, default=0)
    
    def add_rating(self, rating_value: int):
        """평점 추가"""
        self.total_ratings += 1
        self.rating_sum += rating_value
        self.average_rating = self.rating_sum / self.total_ratings
        
        # 개별 카운트 증가
        if rating_value == 1:
            self.rating_1_count += 1
        elif rating_value == 2:
            self.rating_2_count += 1
        elif rating_value == 3:
            self.rating_3_count += 1
        elif rating_value == 4:
            self.rating_4_count += 1
        elif rating_value == 5:
            self.rating_5_count += 1


# Pydantic 모델들
class FeedbackCreate(BaseModel):
    """피드백 생성 모델"""
    session_id: str
    feedback_text: Optional[str] = ""
    rating: int
    category: Optional[str] = None
    user_id: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('평점은 1-5 사이의 값이어야 합니다.')
        return v
    
    @validator('feedback_text')
    def validate_feedback_text(cls, v):
        if v and len(v) > 1000:
            raise ValueError('피드백은 1000자를 초과할 수 없습니다.')
        return v


class FeedbackResponse(BaseResponse):
    """피드백 응답 모델"""
    id: int
    session_id: str
    feedback_text: Optional[str]
    rating: int
    category: Optional[str]
    submitted_at: datetime


class RatingStats(BaseModel):
    """평점 통계"""
    total_ratings: int
    average_rating: float
    rating_distribution: dict  # {1: count, 2: count, ...}
    period: str  # 'daily', 'weekly', 'monthly'
    date_range: str


class FeedbackAnalytics(BaseModel):
    """피드백 분석 결과"""
    total_feedback: int
    average_rating: float
    rating_trend: list  # 시간대별 평점 변화
    common_keywords: list  # 자주 언급되는 키워드
    satisfaction_rate: float  # 만족도 (4-5점 비율)
    improvement_areas: list  # 개선 필요 영역