"""
Hi-Care AI 챗봇 보안 미들웨어
보안 헤더, CORS, 인증 등을 담당하는 미들웨어 모음
"""

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging
from typing import Callable

from ..config.settings import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 기본 보안 헤더
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            
            # 프로덕션 환경 추가 보안 헤더
            if settings.is_production:
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                response.headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "connect-src 'self' https://ai.potens.ai https://*.potensdot.com;"
                )
            
            # 응답 시간 헤더 추가 (개발 환경)
            if settings.is_development:
                process_time = time.time() - start_time
                response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            process_time = time.time() - start_time
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "process_time": process_time
                }
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """레이트 리미팅 미들웨어"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # 실제 서비스에서는 Redis 사용 권장
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.is_production:
            # 개발 환경에서는 레이트 리미팅 비활성화
            return await call_next(request)
        
        client_ip = request.client.host
        current_time = time.time()
        
        # 클라이언트별 요청 추적
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # 오래된 요청 제거
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]
        
        # 레이트 리미트 체크
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "message": f"Rate limit exceeded. Try again in {self.window_seconds} seconds."
                }
            )
        
        # 현재 요청 기록
        self.requests[client_ip].append(current_time)
        
        response = await call_next(request)
        
        # 레이트 리미트 정보를 헤더에 추가
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(self.max_requests - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 요청 로깅
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 응답 로깅
            logger.info(
                f"Response: {response.status_code} "
                f"in {process_time:.4f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"Error: {str(e)} in {process_time:.4f}s"
            )
            raise


def setup_middleware(app):
    """애플리케이션에 미들웨어 설정"""
    
    # 보안 미들웨어 추가
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 신뢰할 수 있는 호스트 설정 (프로덕션)
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts
        )
    
    # 레이트 리미팅 (프로덕션)
    if settings.is_production:
        app.add_middleware(
            RateLimitMiddleware,
            max_requests=100,
            window_seconds=60
        )
    
    # CORS 미들웨어
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # 로깅 미들웨어 (개발 환경)
    if settings.is_development:
        app.add_middleware(LoggingMiddleware)
    
    logger.info(f"🔐 미들웨어 설정 완료 (환경: {settings.environment})")
    logger.info(f"   CORS 오리진: {len(settings.cors_origins)}개")
    logger.info(f"   신뢰 호스트: {len(settings.trusted_hosts)}개") 