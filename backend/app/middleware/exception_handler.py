"""
글로벌 예외 핸들러
모든 예외를 일관성 있게 처리하고 로깅
"""

import logging
import traceback
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from ..exceptions import ChatbotBaseException, get_error_code

logger = logging.getLogger(__name__)


class ExceptionHandler:
    """예외 처리 클래스"""
    
    @staticmethod
    def create_error_response(
        error_code: str,
        message: str,
        status_code: int = 500,
        details: dict = None,
        request_id: str = None
    ) -> JSONResponse:
        """표준화된 에러 응답 생성"""
        
        response_data = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "timestamp": __import__('time').time()
            }
        }
        
        if details:
            response_data["error"]["details"] = details
            
        if request_id:
            response_data["error"]["request_id"] = request_id
            
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    @staticmethod
    async def chatbot_exception_handler(request: Request, exc: ChatbotBaseException):
        """커스텀 챗봇 예외 핸들러"""
        
        # 에러 로깅
        logger.error(
            f"ChatbotException: {exc.error_code} - {exc.message}",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "details": exc.details,
                "path": str(request.url.path),
                "method": request.method
            }
        )
        
        return ExceptionHandler.create_error_response(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            request_id=getattr(request.state, 'request_id', None)
        )
    
    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Pydantic 검증 오류 핸들러"""
        
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Validation error: {len(errors)} fields failed validation",
            extra={
                "errors": errors,
                "path": str(request.url.path),
                "method": request.method
            }
        )
        
        return ExceptionHandler.create_error_response(
            error_code="VALIDATION_ERROR",
            message="입력 데이터 검증에 실패했습니다.",
            status_code=422,
            details={"validation_errors": errors}
        )
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException):
        """FastAPI HTTPException 핸들러"""
        
        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "method": request.method
            }
        )
        
        # 상태 코드별 사용자 친화적 메시지
        user_messages = {
            400: "잘못된 요청입니다. 입력 내용을 확인해주세요.",
            401: "인증이 필요합니다.",
            403: "접근 권한이 없습니다.",
            404: "요청하신 리소스를 찾을 수 없습니다.",
            405: "허용되지 않는 메소드입니다.",
            429: "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
            500: "서버 내부 오류가 발생했습니다.",
            502: "게이트웨이 오류가 발생했습니다.",
            503: "서비스를 일시적으로 사용할 수 없습니다.",
            504: "게이트웨이 시간 초과가 발생했습니다."
        }
        
        user_message = user_messages.get(exc.status_code, str(exc.detail))
        
        return ExceptionHandler.create_error_response(
            error_code=f"HTTP_{exc.status_code}",
            message=user_message,
            status_code=exc.status_code,
            details={"original_detail": str(exc.detail)} if exc.detail != user_message else None
        )
    
    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception):
        """일반 예외 핸들러 (마지막 보루)"""
        
        # 상세한 에러 로깅
        logger.error(
            f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
            extra={
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc(),
                "path": str(request.url.path),
                "method": request.method
            }
        )
        
        # 프로덕션에서는 상세 에러 정보 숨김
        from ..config.settings import settings
        
        if settings.is_development:
            details = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback.format_exc().split('\n')
            }
        else:
            details = None
        
        return ExceptionHandler.create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다. 문제가 지속되면 고객센터로 연락해주세요.",
            status_code=500,
            details=details
        )


def setup_exception_handlers(app):
    """FastAPI 앱에 예외 핸들러 등록"""
    
    # 커스텀 챗봇 예외
    app.add_exception_handler(
        ChatbotBaseException, 
        ExceptionHandler.chatbot_exception_handler
    )
    
    # Pydantic 검증 오류
    app.add_exception_handler(
        RequestValidationError, 
        ExceptionHandler.validation_exception_handler
    )
    
    # FastAPI HTTP 예외
    app.add_exception_handler(
        HTTPException, 
        ExceptionHandler.http_exception_handler
    )
    
    # 기타 모든 예외
    app.add_exception_handler(
        Exception, 
        ExceptionHandler.general_exception_handler
    )
    
    logger.info("예외 핸들러 설정 완료")