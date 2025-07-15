"""
분석 리포지토리
감정 분석, 대화 메트릭 등 분석 데이터 관리
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from .base import BaseRepository
from ..models.analytics import EmotionAnalysis, EmotionAnalysisCreate


class AnalyticsRepository(BaseRepository[EmotionAnalysis, EmotionAnalysisCreate, dict]):
    """분석 리포지토리"""
    
    def __init__(self):
        super().__init__(EmotionAnalysis)
    
    def get_emotion_by_session(self, db: Session, *, session_id: str) -> List[EmotionAnalysis]:
        """세션의 감정 분석 결과 조회"""
        return (
            db.query(EmotionAnalysis)
            .filter(EmotionAnalysis.session_id == session_id)
            .order_by(EmotionAnalysis.analyzed_at.asc())
            .all()
        )
    
    def get_emotion_distribution(self, db: Session, *, days: int = 7) -> Dict[str, Any]:
        """감정 분포 통계"""
        start_date = datetime.now() - timedelta(days=days)
        
        results = (
            db.query(
                EmotionAnalysis.emotion,
                func.count(EmotionAnalysis.id).label('count')
            )
            .filter(EmotionAnalysis.analyzed_at >= start_date)
            .group_by(EmotionAnalysis.emotion)
            .all()
        )
        
        distribution = {}
        total_count = sum(result.count for result in results)
        
        for result in results:
            distribution[result.emotion] = {
                'count': result.count,
                'percentage': (result.count / max(total_count, 1)) * 100
            }
        
        return distribution
