"""
애플리케이션 설정 관리
환경변수를 통한 설정 로드 및 검증
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from enum import Enum


class Environment(str, Enum):
    """환경 타입"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본 설정
    app_name: str = Field(default="Hi-Care AI 챗봇", env="APP_NAME")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    version: str = Field(default="2.0.0", env="APP_VERSION")
    
    # 서버 설정
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    
    # API 키 설정
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    groqcloud_api_key: Optional[str] = Field(default=None, env="GROQCLOUD_API_KEY")
    potensdot_api_key: Optional[str] = Field(default=None, env="POTENSDOT_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # CORS 설정
    allowed_origins: str = Field(
        default="http://localhost:5173",
        env="ALLOWED_ORIGINS"
    )
    
    # 보안 설정
    secret_key: str = Field(default="hi-care-secret-key-2024", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # 데이터베이스 설정 (향후 확장용)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # 로깅 설정
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # 성능 설정
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    workers: Optional[str] = Field(default=None, env="WORKERS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # 알림 설정
    webhook_url: Optional[str] = Field(default=None, env="WEBHOOK_URL")
    notification_email: Optional[str] = Field(default=None, env="NOTIFICATION_EMAIL")
    
    # RAG 설정
    max_rag_results: int = Field(default=5, env="MAX_RAG_RESULTS")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 정의되지 않은 필드 무시
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "allow"  # 추가 필드 허용
    }
    
    @property
    def cors_origins(self) -> List[str]:
        """CORS 허용 오리진 목록 반환"""
        # 기본 허용 오리진 (모든 환경)
        base_origins = [
            "https://new-hyundai-chatbot.web.app",
            "https://new-hyundai-chatbot.firebaseapp.com",
            "https://new-hi-care-chatbot.web.app",
            "https://new-hi-care-chatbot.firebaseapp.com",
            "https://hi-care.com",
            "https://*.hi-care.com",
            "https://*.ngrok-free.app",  # ngrok 도메인 허용
            "https://*.ngrok.io"  # ngrok.io 도메인도 허용
        ]
        
        if self.environment == Environment.PRODUCTION:
            # 프로덕션 환경에서는 기본 오리진 + 환경변수
            origins = [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
            return list(set(base_origins + origins))
        else:
            # 개발 환경에서는 더 유연한 CORS 정책
            origins = [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
            if not origins:
                origins = [
                    "http://localhost:3000",
                    "http://localhost:5173",
                    "http://localhost:8080",
                    "https://218457e5970e.ngrok-free.app"
                ]
            return list(set(base_origins + origins))
    
    @property
    def trusted_hosts(self) -> List[str]:
        """신뢰할 수 있는 호스트 목록"""
        if self.environment == Environment.PRODUCTION:
            return ["hi-care.com", "*.hi-care.com", "*.ngrok-free.app", "*.ngrok.io"]
        return ["*", "localhost", "127.0.0.1", "*.ngrok-free.app", "*.ngrok.io"]  # 개발 환경에서는 모든 호스트 허용
    
    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.environment == Environment.DEVELOPMENT
    
    def validate_api_keys(self) -> bool:
        """필수 API 키 검증"""
        required_keys = []
        
        if not self.google_api_key:
            required_keys.append("GOOGLE_API_KEY")
        
        if not self.potensdot_api_key:
            required_keys.append("POTENSDOT_API_KEY")
        
        if required_keys:
            print(f"⚠️ 경고: 다음 API 키가 설정되지 않았습니다: {', '.join(required_keys)}")
            return False
        
        return True


# 전역 설정 인스턴스
settings = Settings()

# 설정 검증
if not settings.validate_api_keys():
    print("🔑 API 키 설정을 확인해주세요!")

print(f"🚀 Hi-Care AI 챗봇 설정 로드됨")
print(f"   환경: {settings.environment}")
print(f"   디버그: {settings.debug}")
print(f"   CORS 오리진: {len(settings.cors_origins)}개") 