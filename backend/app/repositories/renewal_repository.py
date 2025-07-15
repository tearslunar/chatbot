"""
갱신 관련 리포지토리
갱신 알림, 갱신 프로세스, 갱신 히스토리 관리
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc

from .base import BaseRepository
from ..models.renewal import (
    RenewalReminder, RenewalProcess, RenewalHistory,
    RenewalReminderCreate, RenewalProcessCreate,
    RenewalStatus, NotificationStatus
)


class RenewalRepository(BaseRepository[RenewalReminder, RenewalReminderCreate, dict]):
    """갱신 알림 리포지토리"""
    
    def __init__(self):
        super().__init__(RenewalReminder)
    
    def get_due_reminders(self, db: Session) -> List[RenewalReminder]:
        """발송 예정인 갱신 알림 조회"""
        now = datetime.now()
        return (
            db.query(RenewalReminder)
            .filter(
                and_(
                    RenewalReminder.scheduled_date <= now,
                    RenewalReminder.status == NotificationStatus.SCHEDULED
                )
            )
            .order_by(RenewalReminder.scheduled_date)
            .all()
        )
    
    def get_renewals_by_period(self, db: Session, *, days_ahead: int = 30) -> List[RenewalReminder]:
        """특정 기간 내 갱신 예정 조회"""
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days_ahead)
        
        return (
            db.query(RenewalReminder)
            .filter(
                and_(
                    RenewalReminder.renewal_date >= start_date,
                    RenewalReminder.renewal_date <= end_date
                )
            )
            .order_by(RenewalReminder.renewal_date)
            .all()
        )
    
    def get_by_persona_id(self, db: Session, *, persona_id: str) -> List[RenewalReminder]:
        """페르소나별 갱신 알림 조회"""
        return (
            db.query(RenewalReminder)
            .filter(RenewalReminder.persona_id == persona_id)
            .order_by(desc(RenewalReminder.created_at))
            .all()
        )
    
    def get_upcoming_renewals(self, db: Session, *, persona_id: str, days: int = 60) -> List[RenewalReminder]:
        """특정 페르소나의 다가오는 갱신 조회"""
        cutoff_date = datetime.now().date() + timedelta(days=days)
        
        return (
            db.query(RenewalReminder)
            .filter(
                and_(
                    RenewalReminder.persona_id == persona_id,
                    RenewalReminder.renewal_date <= cutoff_date,
                    RenewalReminder.renewal_date >= datetime.now().date()
                )
            )
            .order_by(RenewalReminder.renewal_date)
            .all()
        )
    
    def mark_as_sent(self, db: Session, *, reminder_id: int) -> Optional[RenewalReminder]:
        """알림 발송 완료 처리"""
        reminder = db.query(RenewalReminder).filter(RenewalReminder.id == reminder_id).first()
        if reminder:
            reminder.mark_as_sent()
            db.commit()
            db.refresh(reminder)
        return reminder
    
    def mark_as_clicked(self, db: Session, *, reminder_id: int) -> Optional[RenewalReminder]:
        """알림 클릭 처리"""
        reminder = db.query(RenewalReminder).filter(RenewalReminder.id == reminder_id).first()
        if reminder:
            reminder.mark_as_clicked()
            db.commit()
            db.refresh(reminder)
        return reminder
    
    def get_notification_stats(self, db: Session, *, days: int = 30) -> Dict[str, Any]:
        """알림 성과 통계"""
        start_date = datetime.now() - timedelta(days=days)
        
        stats = (
            db.query(
                func.count(RenewalReminder.id).label('total_sent'),
                func.sum(func.case([(RenewalReminder.status == NotificationStatus.CLICKED, 1)], else_=0)).label('clicked_count'),
                func.sum(func.case([(RenewalReminder.status == NotificationStatus.CONVERTED, 1)], else_=0)).label('converted_count'),
                func.avg(RenewalReminder.response_time).label('avg_response_time')
            )
            .filter(
                and_(
                    RenewalReminder.sent_at >= start_date,
                    RenewalReminder.status != NotificationStatus.SCHEDULED
                )
            )
            .first()
        )
        
        total_sent = stats.total_sent or 0
        clicked_count = stats.clicked_count or 0
        converted_count = stats.converted_count or 0
        
        return {
            'total_sent': total_sent,
            'clicked_count': clicked_count,
            'converted_count': converted_count,
            'click_rate': clicked_count / max(total_sent, 1),
            'conversion_rate': converted_count / max(total_sent, 1),
            'avg_response_time': stats.avg_response_time or 0
        }
    
    def create_renewal_reminder(self, db: Session, *, persona_id: str, renewal_date: date, insurance_type: str, persona_data: Dict[str, Any]) -> RenewalReminder:
        """갱신 알림 생성"""
        # 갱신 30일 전 알림 스케줄
        reminder_days = 30
        scheduled_date = datetime.combine(renewal_date, datetime.min.time()) - timedelta(days=reminder_days)
        
        reminder = RenewalReminder(
            persona_id=persona_id,
            insurance_type=insurance_type,
            renewal_date=renewal_date,
            reminder_days=reminder_days,
            scheduled_date=scheduled_date,
            persona_data=persona_data,
            status=NotificationStatus.SCHEDULED
        )
        
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder


class RenewalProcessRepository(BaseRepository[RenewalProcess, RenewalProcessCreate, dict]):
    """갱신 프로세스 리포지토리"""
    
    def __init__(self):
        super().__init__(RenewalProcess)
    
    def get_active_processes(self, db: Session) -> List[RenewalProcess]:
        """진행 중인 갱신 프로세스 조회"""
        return (
            db.query(RenewalProcess)
            .filter(RenewalProcess.status == RenewalStatus.IN_PROGRESS)
            .order_by(RenewalProcess.started_at)
            .all()
        )
    
    def get_by_persona_id(self, db: Session, *, persona_id: str) -> List[RenewalProcess]:
        """페르소나별 갱신 프로세스 조회"""
        return (
            db.query(RenewalProcess)
            .filter(RenewalProcess.persona_id == persona_id)
            .order_by(desc(RenewalProcess.started_at))
            .all()
        )
    
    def get_current_process(self, db: Session, *, persona_id: str) -> Optional[RenewalProcess]:
        """현재 진행 중인 갱신 프로세스 조회"""
        return (
            db.query(RenewalProcess)
            .filter(
                and_(
                    RenewalProcess.persona_id == persona_id,
                    RenewalProcess.status == RenewalStatus.IN_PROGRESS
                )
            )
            .first()
        )
    
    def start_renewal_process(self, db: Session, *, persona_id: str, reminder_id: Optional[int] = None, persona_data: Dict[str, Any] = None) -> RenewalProcess:
        """갱신 프로세스 시작"""
        process = RenewalProcess(
            persona_id=persona_id,
            reminder_id=reminder_id,
            status=RenewalStatus.IN_PROGRESS,
            current_step="initial",
            persona_preferences=persona_data or {}
        )
        
        db.add(process)
        db.commit()
        db.refresh(process)
        return process
    
    def advance_process_step(self, db: Session, *, process_id: int, next_step: str) -> Optional[RenewalProcess]:
        """갱신 프로세스 단계 진행"""
        process = db.query(RenewalProcess).filter(RenewalProcess.id == process_id).first()
        if process:
            process.advance_step(next_step)
            db.commit()
            db.refresh(process)
        return process
    
    def complete_renewal(self, db: Session, *, process_id: int, new_product: str, new_premium: float) -> Optional[RenewalProcess]:
        """갱신 완료 처리"""
        process = db.query(RenewalProcess).filter(RenewalProcess.id == process_id).first()
        if process:
            process.new_product = new_product
            process.new_premium = new_premium
            process.advance_step("complete")
            db.commit()
            db.refresh(process)
        return process
    
    def abandon_renewal(self, db: Session, *, process_id: int, reason: str) -> Optional[RenewalProcess]:
        """갱신 포기 처리"""
        process = db.query(RenewalProcess).filter(RenewalProcess.id == process_id).first()
        if process:
            process.status = RenewalStatus.CANCELLED
            process.abandonment_reason = reason
            db.commit()
            db.refresh(process)
        return process
    
    def get_conversion_stats(self, db: Session, *, days: int = 30) -> Dict[str, Any]:
        """갱신 전환율 통계"""
        start_date = datetime.now() - timedelta(days=days)
        
        stats = (
            db.query(
                func.count(RenewalProcess.id).label('total_processes'),
                func.sum(func.case([(RenewalProcess.conversion_success == True, 1)], else_=0)).label('successful_renewals'),
                func.avg(RenewalProcess.satisfaction_score).label('avg_satisfaction'),
                func.count(func.case([(RenewalProcess.consultation_needed == True, 1)], else_=None)).label('consultation_needed_count')
            )
            .filter(RenewalProcess.started_at >= start_date)
            .first()
        )
        
        total_processes = stats.total_processes or 0
        successful_renewals = stats.successful_renewals or 0
        
        return {
            'total_processes': total_processes,
            'successful_renewals': successful_renewals,
            'conversion_rate': successful_renewals / max(total_processes, 1),
            'avg_satisfaction': stats.avg_satisfaction or 0,
            'consultation_rate': (stats.consultation_needed_count or 0) / max(total_processes, 1)
        }


class RenewalHistoryRepository(BaseRepository[RenewalHistory, dict, dict]):
    """갱신 히스토리 리포지토리"""
    
    def __init__(self):
        super().__init__(RenewalHistory)
    
    def get_by_persona_id(self, db: Session, *, persona_id: str) -> List[RenewalHistory]:
        """페르소나별 갱신 히스토리 조회"""
        return (
            db.query(RenewalHistory)
            .filter(RenewalHistory.persona_id == persona_id)
            .order_by(desc(RenewalHistory.renewal_date))
            .all()
        )
    
    def get_recent_renewals(self, db: Session, *, days: int = 90) -> List[RenewalHistory]:
        """최근 갱신 히스토리 조회"""
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        return (
            db.query(RenewalHistory)
            .filter(RenewalHistory.renewal_date >= cutoff_date)
            .order_by(desc(RenewalHistory.renewal_date))
            .all()
        )
    
    def create_renewal_history(self, db: Session, *, process: RenewalProcess) -> RenewalHistory:
        """갱신 히스토리 생성"""
        savings = process.calculate_savings()
        
        history = RenewalHistory(
            persona_id=process.persona_id,
            process_id=process.id,
            previous_product=process.current_product,
            new_product=process.new_product,
            renewal_date=datetime.now().date(),
            previous_premium=process.current_premium,
            new_premium=process.new_premium,
            savings_amount=savings,
            renewal_type="manual" if process.consultation_needed else "automatic",
            satisfaction_score=process.satisfaction_score
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        return history
    
    def get_savings_summary(self, db: Session, *, days: int = 365) -> Dict[str, Any]:
        """절약 금액 요약"""
        start_date = datetime.now().date() - timedelta(days=days)
        
        stats = (
            db.query(
                func.count(RenewalHistory.id).label('total_renewals'),
                func.sum(RenewalHistory.savings_amount).label('total_savings'),
                func.avg(RenewalHistory.savings_amount).label('avg_savings'),
                func.avg(RenewalHistory.satisfaction_score).label('avg_satisfaction')
            )
            .filter(RenewalHistory.renewal_date >= start_date)
            .first()
        )
        
        return {
            'total_renewals': stats.total_renewals or 0,
            'total_savings': stats.total_savings or 0,
            'avg_savings': stats.avg_savings or 0,
            'avg_satisfaction': stats.avg_satisfaction or 0
        }