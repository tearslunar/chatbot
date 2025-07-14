"""
기본 데이터베이스 모델
공통 필드와 메소드 정의
"""

from datetime import datetime
from typing import Any, Dict
import json

from sqlalchemy import Column, Integer, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from pydantic import BaseModel

Base = declarative_base()


class TimestampMixin:
    """타임스탬프 필드 믹스인"""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseDBModel(Base, TimestampMixin):
    """기본 데이터베이스 모델"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델을 딕셔너리로 변환"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]):
        """딕셔너리에서 모델 업데이트"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class JSONField(Text):
    """JSON 필드 타입"""
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


# Pydantic 응답 모델들
class BaseResponse(BaseModel):
    """기본 응답 모델"""
    
    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """페이지네이션 응답 모델"""
    
    items: list
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True