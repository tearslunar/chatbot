"""
커스텀 예외 클래스들
애플리케이션별 에러 처리를 위한 전용 예외들
"""

from typing import Optional, Dict, Any


class ChatbotBaseException(Exception):
    """챗봇 기본 예외 클래스"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(ChatbotBaseException):
    """입력 검증 오류"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, status_code=422, **kwargs)
        if field:
            self.details["field"] = field


class APIConnectionError(ChatbotBaseException):
    """외부 API 연결 오류"""
    
    def __init__(self, service: str, message: str = None, **kwargs):
        message = message or f"{service} API 연결에 실패했습니다."
        super().__init__(message, status_code=503, **kwargs)
        self.details["service"] = service


class APIRateLimitError(ChatbotBaseException):
    """API 요청 제한 초과"""
    
    def __init__(self, service: str, retry_after: Optional[int] = None, **kwargs):
        message = f"{service} API 요청 제한을 초과했습니다."
        super().__init__(message, status_code=429, **kwargs)
        self.details["service"] = service
        if retry_after:
            self.details["retry_after"] = retry_after


class EmotionAnalysisError(ChatbotBaseException):
    """감정 분석 오류"""
    
    def __init__(self, message: str = "감정 분석 중 오류가 발생했습니다.", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class RAGSearchError(ChatbotBaseException):
    """RAG 검색 오류"""
    
    def __init__(self, search_type: str, message: str = None, **kwargs):
        message = message or f"{search_type} 검색 중 오류가 발생했습니다."
        super().__init__(message, status_code=500, **kwargs)
        self.details["search_type"] = search_type


class PersonaError(ChatbotBaseException):
    """페르소나 관련 오류"""
    
    def __init__(self, message: str = "페르소나 처리 중 오류가 발생했습니다.", **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class SessionError(ChatbotBaseException):
    """세션 관련 오류"""
    
    def __init__(self, session_id: str, message: str = None, **kwargs):
        message = message or f"세션 {session_id} 처리 중 오류가 발생했습니다."
        super().__init__(message, status_code=400, **kwargs)
        self.details["session_id"] = session_id


class ConfigurationError(ChatbotBaseException):
    """설정 오류"""
    
    def __init__(self, config_name: str, message: str = None, **kwargs):
        message = message or f"설정 '{config_name}'이 올바르지 않습니다."
        super().__init__(message, status_code=500, **kwargs)
        self.details["config_name"] = config_name


class ModelNotAvailableError(ChatbotBaseException):
    """모델 사용 불가 오류"""
    
    def __init__(self, model_name: str, **kwargs):
        message = f"모델 '{model_name}'를 사용할 수 없습니다."
        super().__init__(message, status_code=503, **kwargs)
        self.details["model_name"] = model_name


class InsuranceDataError(ChatbotBaseException):
    """보험 데이터 관련 오류"""
    
    def __init__(self, data_type: str, message: str = None, **kwargs):
        message = message or f"보험 {data_type} 데이터 처리 중 오류가 발생했습니다."
        super().__init__(message, status_code=500, **kwargs)
        self.details["data_type"] = data_type


class SecurityError(ChatbotBaseException):
    """보안 관련 오류"""
    
    def __init__(self, security_issue: str, **kwargs):
        message = f"보안 문제가 감지되었습니다: {security_issue}"
        super().__init__(message, status_code=403, **kwargs)
        self.details["security_issue"] = security_issue


# 에러 코드 매핑
ERROR_CODE_MAPPING = {
    ValidationError: "VALIDATION_ERROR",
    APIConnectionError: "API_CONNECTION_ERROR", 
    APIRateLimitError: "API_RATE_LIMIT_ERROR",
    EmotionAnalysisError: "EMOTION_ANALYSIS_ERROR",
    RAGSearchError: "RAG_SEARCH_ERROR",
    PersonaError: "PERSONA_ERROR",
    SessionError: "SESSION_ERROR",
    ConfigurationError: "CONFIGURATION_ERROR",
    ModelNotAvailableError: "MODEL_NOT_AVAILABLE_ERROR",
    InsuranceDataError: "INSURANCE_DATA_ERROR",
    SecurityError: "SECURITY_ERROR"
}


def get_error_code(exception_class) -> str:
    """예외 클래스에서 에러 코드 추출"""
    return ERROR_CODE_MAPPING.get(exception_class, "UNKNOWN_ERROR")