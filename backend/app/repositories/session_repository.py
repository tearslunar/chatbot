"""
세션 및 메시지 리포지토리
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from .base import BaseRepository
from ..models.session import ChatSession, Message, SessionCreate, MessageCreate


class SessionRepository(BaseRepository[ChatSession, SessionCreate, dict]):
    """채팅 세션 리포지토리"""
    
    def __init__(self):
        super().__init__(ChatSession)
    
    def get_by_session_id(self, db: Session, *, session_id: str) -> Optional[ChatSession]:
        """세션 ID로 조회"""
        return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    
    def get_active_sessions(self, db: Session) -> List[ChatSession]:
        """활성 세션 목록 조회"""
        return db.query(ChatSession).filter(ChatSession.status == "active").all()
    
    def get_sessions_by_user(self, db: Session, *, user_id: str, limit: int = 10) -> List[ChatSession]:
        """사용자별 세션 목록"""
        return (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_expired_sessions(self, db: Session, *, hours: int = 24) -> List[ChatSession]:
        """만료된 세션 조회"""
        expiry_time = datetime.utcnow() - timedelta(hours=hours)
        return (
            db.query(ChatSession)
            .filter(
                and_(
                    ChatSession.status == "active",
                    ChatSession.created_at < expiry_time
                )
            )
            .all()
        )
    
    def end_session(self, db: Session, *, session_id: str) -> Optional[ChatSession]:
        """세션 종료"""
        session = self.get_by_session_id(db, session_id=session_id)
        if session:
            session.end_session()
            db.commit()
            db.refresh(session)
        return session
    
    def update_session_stats(self, db: Session, *, session_id: str, stats: Dict[str, Any]) -> Optional[ChatSession]:
        """세션 통계 업데이트"""
        session = self.get_by_session_id(db, session_id=session_id)
        if session:
            for key, value in stats.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            db.commit()
            db.refresh(session)
        return session
    
    def get_session_stats(self, db: Session, *, days: int = 7) -> Dict[str, Any]:
        """세션 통계 조회"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        stats = db.query(
            func.count(ChatSession.id).label('total_sessions'),
            func.count(func.nullif(ChatSession.status, 'active')).label('completed_sessions'),
            func.avg(ChatSession.duration_seconds).label('avg_duration'),
            func.avg(ChatSession.total_messages).label('avg_messages'),
            func.sum(func.case([(ChatSession.emotion_resolved == True, 1)], else_=0)).label('resolved_count'),
            func.sum(func.case([(ChatSession.escalation_triggered == True, 1)], else_=0)).label('escalation_count')
        ).filter(ChatSession.created_at >= start_date).first()
        
        total_sessions = stats.total_sessions or 0
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': stats.completed_sessions or 0,
            'avg_duration_minutes': (stats.avg_duration or 0) / 60,
            'avg_messages_per_session': stats.avg_messages or 0,
            'emotion_resolution_rate': (stats.resolved_count or 0) / max(total_sessions, 1),
            'escalation_rate': (stats.escalation_count or 0) / max(total_sessions, 1)
        }


class MessageRepository(BaseRepository[Message, MessageCreate, dict]):
    """메시지 리포지토리"""
    
    def __init__(self):
        super().__init__(Message)
    
    def get_by_session(self, db: Session, *, session_id: str, limit: int = 100) -> List[Message]:
        """세션의 메시지 목록 조회"""
        return (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .all()
        )
    
    def get_recent_messages(self, db: Session, *, session_id: str, count: int = 10) -> List[Message]:
        """최근 메시지 조회"""
        return (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(count)
            .all()
        )
    
    def get_user_messages(self, db: Session, *, session_id: str) -> List[Message]:
        """사용자 메시지만 조회"""
        return (
            db.query(Message)
            .filter(
                and_(
                    Message.session_id == session_id,
                    Message.role == "user"
                )
            )
            .order_by(Message.created_at.asc())
            .all()
        )
    
    def get_bot_messages(self, db: Session, *, session_id: str) -> List[Message]:
        """봇 메시지만 조회"""
        return (
            db.query(Message)
            .filter(
                and_(
                    Message.session_id == session_id,
                    Message.role == "bot"
                )
            )
            .order_by(Message.created_at.asc())
            .all()
        )
    
    def get_messages_with_emotion(self, db: Session, *, emotion: str, days: int = 7) -> List[Message]:
        """특정 감정의 메시지 조회"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return (
            db.query(Message)
            .filter(
                and_(
                    Message.emotion_data.isnot(None),
                    Message.created_at >= start_date
                )
            )
            .all()
        )
    
    def get_escalation_messages(self, db: Session, *, days: int = 7) -> List[Message]:
        """에스컬레이션 메시지 조회"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return (
            db.query(Message)
            .filter(
                and_(
                    Message.escalation_needed == True,
                    Message.created_at >= start_date
                )
            )
            .all()
        )
    
    def get_message_stats(self, db: Session, *, days: int = 7) -> Dict[str, Any]:
        """메시지 통계 조회"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        stats = db.query(
            func.count(Message.id).label('total_messages'),
            func.avg(Message.processing_time).label('avg_processing_time'),
            func.sum(func.case([(Message.escalation_needed == True, 1)], else_=0)).label('escalation_count'),
            func.sum(func.case([(Message.role == 'user', 1)], else_=0)).label('user_messages'),
            func.sum(func.case([(Message.role == 'bot', 1)], else_=0)).label('bot_messages')
        ).filter(Message.created_at >= start_date).first()
        
        total_messages = stats.total_messages or 0
        
        return {
            'total_messages': total_messages,
            'avg_processing_time': stats.avg_processing_time or 0,
            'escalation_rate': (stats.escalation_count or 0) / max(total_messages, 1),
            'user_messages': stats.user_messages or 0,
            'bot_messages': stats.bot_messages or 0,
            'conversation_ratio': (stats.user_messages or 0) / max(stats.bot_messages or 1, 1)
        }