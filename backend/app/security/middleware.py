"""
보안 미들웨어
요청 검증, 레이트 리미팅, 보안 헤더 추가
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .validators import check_rate_limit, validate_user_input
from .crypto import hash_data
from ..exceptions import SecurityError

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """보안 미들웨어"""
    
    def __init__(self, app, config: dict = None):
        super().__init__(app)
        self.config = config or {}
        
        # 기본 설정
        self.rate_limit_enabled = self.config.get('rate_limit_enabled', True)
        self.rate_limit_requests = self.config.get('rate_limit_requests', 100)
        self.rate_limit_window = self.config.get('rate_limit_window', 3600)
        
        self.security_headers_enabled = self.config.get('security_headers_enabled', True)
        self.input_validation_enabled = self.config.get('input_validation_enabled', True)
        
        # 제외할 경로들
        self.excluded_paths = self.config.get('excluded_paths', ['/docs', '/redoc', '/openapi.json'])
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """요청 처리"""
        start_time = time.time()
        
        # 제외 경로 확인
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        try:
            # 1. IP 기반 레이트 리미팅
            if self.rate_limit_enabled:
                client_ip = self._get_client_ip(request)
                if not check_rate_limit(
                    key=f"ip:{client_ip}",
                    limit=self.rate_limit_requests,
                    window=self.rate_limit_window
                ):
                    logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Too Many Requests",
                            "message": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요."
                        }
                    )
            
            # 2. 의심스러운 요청 패턴 감지
            await self._detect_suspicious_patterns(request)
            
            # 3. 요청 처리
            response = await call_next(request)
            
            # 4. 보안 헤더 추가
            if self.security_headers_enabled:
                self._add_security_headers(response)
            
            # 5. 로깅
            processing_time = time.time() - start_time
            logger.info(
                f"Request processed: {request.method} {request.url.path} "
                f"Status: {response.status_code} Time: {processing_time:.3f}s"
            )
            
            return response
            
        except SecurityError as e:
            logger.error(f"Security error: {str(e)} for IP: {self._get_client_ip(request)}")
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Security Error",
                    "message": "보안 정책 위반이 감지되었습니다."
                }
            )
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "서버 내부 오류가 발생했습니다."
                }
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 추출"""
        # X-Forwarded-For 헤더 확인 (프록시/로드밸런서 뒤에 있는 경우)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip.strip()
        
        # 직접 연결된 클라이언트 IP
        return request.client.host if request.client else "unknown"
    
    async def _detect_suspicious_patterns(self, request: Request):
        """의심스러운 요청 패턴 감지"""
        # User-Agent 검사
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or len(user_agent) < 10:
            raise SecurityError("의심스러운 User-Agent")
        
        # 알려진 봇/크롤러 차단 (필요한 경우)
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'masscan']
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            raise SecurityError("악성 User-Agent 감지")
        
        # URL 길이 검사
        if len(str(request.url)) > 2048:
            raise SecurityError("비정상적으로 긴 URL")
        
        # 헤더 크기 검사
        total_header_size = sum(len(k) + len(v) for k, v in request.headers.items())
        if total_header_size > 8192:  # 8KB
            raise SecurityError("비정상적으로 큰 헤더")
    
    def _add_security_headers(self, response: Response):
        """보안 헤더 추가"""
        security_headers = {
            # XSS 보호
            'X-XSS-Protection': '1; mode=block',
            
            # 콘텐츠 타입 스니핑 방지
            'X-Content-Type-Options': 'nosniff',
            
            # 클릭재킹 방지
            'X-Frame-Options': 'DENY',
            
            # HSTS (HTTPS 강제)
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            
            # 콘텐츠 보안 정책
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self'"
            ),
            
            # 리퍼러 정책
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # 권한 정책
            'Permissions-Policy': (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            ),
            
            # 서버 정보 숨김
            'Server': 'Hi-Care-Server'
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """요청 로깅 미들웨어"""
    
    def __init__(self, app, log_level: str = "INFO"):
        super().__init__(app)
        self.log_level = getattr(logging, log_level.upper())
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """요청 로깅"""
        start_time = time.time()
        
        # 요청 정보 수집
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get('User-Agent', 'unknown')
        
        # 요청 로깅
        logger.log(
            self.log_level,
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} [{user_agent}]"
        )
        
        # 요청 처리
        response = await call_next(request)
        
        # 응답 로깅
        processing_time = time.time() - start_time
        logger.log(
            self.log_level,
            f"Response: {response.status_code} "
            f"in {processing_time:.3f}s"
        )
        
        return response


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API 키 검증 미들웨어"""
    
    def __init__(self, app, api_keys: list = None, header_name: str = "X-API-Key"):
        super().__init__(app)
        self.api_keys = set(api_keys or [])
        self.header_name = header_name
        
        # API 키가 필요한 경로들
        self.protected_paths = ['/admin', '/analytics', '/management']
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """API 키 검증"""
        # 보호된 경로인지 확인
        path = request.url.path
        needs_api_key = any(path.startswith(protected) for protected in self.protected_paths)
        
        if needs_api_key:
            api_key = request.headers.get(self.header_name)
            
            if not api_key:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "Missing API Key",
                        "message": f"{self.header_name} 헤더가 필요합니다."
                    }
                )
            
            if api_key not in self.api_keys:
                logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Invalid API Key",
                        "message": "유효하지 않은 API 키입니다."
                    }
                )
        
        return await call_next(request)