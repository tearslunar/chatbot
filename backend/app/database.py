"""
데이터베이스 연결 및 세션 관리
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config.settings import settings
from .models.base import Base

# 데이터베이스 엔진 생성
if settings.database_url:
    # 실제 데이터베이스 사용
    if "sqlite" in settings.database_url:
        # SQLite용 설정
        engine = create_engine(
            settings.database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=settings.debug
        )
    else:
        # PostgreSQL, MySQL 등
        engine = create_engine(
            settings.database_url,
            echo=settings.debug
        )
else:
    # 기본값: 인메모리 SQLite
    engine = create_engine(
        "sqlite:///./chatbot.db",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=settings.debug
    )

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """데이터베이스 관리자"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_all_tables(self):
        """모든 테이블 생성"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_all_tables(self):
        """모든 테이블 삭제 (주의!)"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """새 세션 반환"""
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """데이터베이스 연결 상태 확인"""
        try:
            db = self.get_session()
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception:
            return False


# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()


# 애플리케이션 시작 시 테이블 생성
def init_database():
    """데이터베이스 초기화"""
    try:
        create_tables()
        print("✅ 데이터베이스 테이블이 생성되었습니다.")
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        raise