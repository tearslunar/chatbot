"""
피드백 리포지토리
사용자 피드백 및 평점 관리
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from .base import BaseRepository
from ..models.feedback import UserFeedback, FeedbackCreate


class FeedbackRepository(BaseRepository[UserFeedback, FeedbackCreate, dict]):
    """피드백 리포지토리"""
    
    def __init__(self):
        super().__init__(UserFeedback)
    
    def get_by_session(self, db: Session, *, session_id: str) -> List[UserFeedback]:
        """세션의 피드백 목록 조회"""
        return db.query(UserFeedback).filter(UserFeedback.session_id == session_id).all()
    
    def get_recent_feedback(self, db: Session, *, days: int = 7, limit: int = 100) -> List[UserFeedback]:
        """최근 피드백 조회"""
        start_date = datetime.now() - timedelta(days=days)
        return (
            db.query(UserFeedback)
            .filter(UserFeedback.submitted_at >= start_date)
            .order_by(desc(UserFeedback.submitted_at))
            .limit(limit)
            .all()
        )
    
    def get_feedback_stats(self, db: Session, *, days: int = 7) -> Dict[str, Any]:
        """피드백 통계 조회"""
        start_date = datetime.now() - timedelta(days=days)
        
        stats = db.query(
            func.count(UserFeedback.id).label('total_feedback'),
            func.avg(UserFeedback.rating).label('avg_rating'),
            func.sum(func.case([(UserFeedback.rating >= 4, 1)], else_=0)).label('satisfied_count'),
            func.sum(func.case([(UserFeedback.rating <= 2, 1)], else_=0)).label('dissatisfied_count')
        ).filter(UserFeedback.submitted_at >= start_date).first()
        
        total_feedback = stats.total_feedback or 0
        
        return {
            'total_feedback': total_feedback,
            'avg_rating': float(stats.avg_rating or 0),
            'satisfaction_rate': (stats.satisfied_count or 0) / max(total_feedback, 1),
            'dissatisfaction_rate': (stats.dissatisfied_count or 0) / max(total_feedback, 1)
        }

