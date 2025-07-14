import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict # SettingsConfigDict 임포트
from pydantic import Field
from enum import Enum


class Environment(str, Enum):
    """환경 타입"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """기본 설정 클래스"""
    
    # Pydantic V2의 model_config 사용
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"  # 추가 필드 허용
    )
    
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
    
    # CORS 설정 (환경 변수에서 쉼표로 구분된 문자열을 받아 처리)
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
    
    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.environment == Environment.DEVELOPMENT

    # 기본 CORS 오리진 (자식 클래스에서 오버라이드)
    @property
    def cors_origins(self) -> List[str]:
        # allowed_origins는 쉼표로 구분된 문자열이므로, 리스트로 변환
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    # 기본 신뢰할 수 있는 호스트 (자식 클래스에서 오버라이드)
    @property
    def trusted_hosts(self) -> List[str]:
        return [] # 기본적으로 비워둠
    
    def validate_api_keys(self) -> bool:
        """기본 API 키 검증 (경고만 발생)"""
        missing_keys = []
        
        if not self.google_api_key:
            missing_keys.append("GOOGLE_API_KEY")
        
        if not self.potensdot_api_key:
            missing_keys.append("POTENSDOT_API_KEY")
        
        if missing_keys:
            print(f"⚠️ 경고: 다음 API 키가 설정되지 않았습니다: {', '.join(missing_keys)}")
            return False
        
        return True


class DevelopmentSettings(Settings):
    """개발 환경 설정"""
    
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"
    
    @property
    def cors_origins(self) -> List[str]:
        # 부모 클래스의 기본 오리진에 개발용 오리진 추가
        return super().cors_origins + [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8080",
            "*"  # 개발 환경에서는 모든 오리진 허용
        ]
    
    @property
    def trusted_hosts(self) -> List[str]:
        return ["*"]  # 개발 환경에서는 모든 호스트 허용


class ProductionSettings(Settings):
    """프로덕션 환경 설정"""
    
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    reload: bool = False
    log_level: str = "INFO"
    
    # 보안 강화: SECRET_KEY는 프로덕션에서 필수 환경변수
    secret_key: str = Field(env="SECRET_KEY") 
    
    @property
    def cors_origins(self) -> List[str]:
        base_origins = [
            "https://new-hyundai-chatbot.web.app",
            "https://new-hyundai-chatbot.firebaseapp.com",
            "https://new-hi-care-chatbot.web.app",
            "https://new-hi-care-chatbot.firebaseapp.com",
            "https://hi-care.com",
            "https://*.hi-care.com"
        ]
        
        # 부모 클래스의 allowed_origins를 파싱하여 추가
        additional_origins = super().cors_origins 
        if additional_origins:
            return list(set(base_origins + additional_origins)) # 중복 제거
        
        return base_origins
    
    @property
    def trusted_hosts(self) -> List[str]:
        return [
            "hi-care.com",
            "*.hi-care.com",
            "new-hyundai-chatbot.web.app",
            "new-hi-care-chatbot.web.app"
        ]
    
    def validate_api_keys(self) -> bool:
        """프로덕션에서는 모든 필수 API 키가 필요하며, 누락 시 예외 발생"""
        # 부모 클래스의 검증을 먼저 수행 (선택 사항: 경고는 표시될 수 있음)
        super().validate_api_keys()

        required_production_keys = []
        
        # 프로덕션에서 필수로 필요한 키들
        if self.potensdot_api_key is None:
            required_production_keys.append("POTENSDOT_API_KEY")
        if self.secret_key is None:
            required_production_keys.append("SECRET_KEY")
        # 필요하다면 다른 API 키들도 프로덕션에서 필수로 지정
        # if self.google_api_key is None:
        #     required_production_keys.append("GOOGLE_API_KEY")
        
        if required_production_keys:
            raise ValueError(f"프로덕션 환경에서 다음 필수 설정이 누락되었습니다: {', '.join(required_production_keys)}")
        
        return True


class TestingSettings(Settings):
    """테스트 환경 설정"""
    
    environment: Environment = Environment.TESTING
    debug: bool = True
    log_level: str = "WARNING"
    
    # 테스트용 API 키 (더미)
    google_api_key: str = "test-google-key"
    potensdot_api_key: str = "test-potensdot-key"
    secret_key: str = "test-secret-key"
    
    # 테스트용 데이터베이스
    database_url: str = "sqlite:///./test.db"
    
    @property
    def cors_origins(self) -> List[str]:
        return ["http://testserver"]
    
    @property
    def trusted_hosts(self) -> List[str]:
        return ["testserver", "localhost", "127.0.0.1"]


def get_settings() -> Settings:
    """환경에 따른 설정 객체 반환"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# 전역 설정 인스턴스
settings = get_settings()

# 설정 검증
try:
    if not settings.validate_api_keys():
        print("🔑 API 키 설정을 확인해주세요!")
except ValueError as e:
    print(f"❌ 설정 검증 실패: {e}")
    if settings.environment == Environment.PRODUCTION:
        # 프로덕션 환경에서 설정 실패 시 애플리케이션 시작을 중단
        raise
    else:
        # 개발/테스트 환경에서는 경고만 표시하고 계속 진행 (선택 사항)
        pass

print(f"🚀 Hi-Care AI 챗봇 설정 로드됨")
print(f"   환경: {settings.environment.value}")
print(f"   디버그: {settings.debug}")
print(f"   CORS 오리진: {len(settings.cors_origins)}개")
print(f"   신뢰할 수 있는 호스트: {len(settings.trusted_hosts)}개")