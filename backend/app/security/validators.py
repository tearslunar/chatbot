"""
입력 검증 및 보안 함수들
"""

import re
import html
import time
import hashlib
from typing import Dict, Optional, List, Any
from urllib.parse import urlparse
import bleach

from ..exceptions import ValidationError, SecurityError

# 허용된 HTML 태그와 속성
ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'br', 'p']
ALLOWED_ATTRIBUTES = {}

# 위험한 패턴들
SUSPICIOUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # JavaScript
    r'javascript:',  # JavaScript URL
    r'on\w+\s*=',  # 이벤트 핸들러
    r'data:text/html',  # Data URL
    r'vbscript:',  # VBScript
    r'expression\s*\(',  # CSS expression
    r'import\s+os',  # Python import
    r'exec\s*\(',  # Python exec
    r'eval\s*\(',  # JavaScript/Python eval
    r'__import__',  # Python import
    r'subprocess',  # Python subprocess
    r'system\s*\(',  # System calls
]

# SQL 인젝션 패턴
SQL_INJECTION_PATTERNS = [
    r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
    r"(\b(or|and)\s+\d+\s*=\s*\d+)",
    r"(\|\||&&|\bor\b|\band\b)\s+\d+\s*=\s*\d+",
    r"('|(\\')|(;|\\x00|\\n|\\r|\\x1a))",
]


def validate_user_input(
    text: str, 
    max_length: int = 1000,
    allow_html: bool = False,
    check_suspicious: bool = True
) -> str:
    """
    사용자 입력 검증 및 정화
    
    Args:
        text: 검증할 텍스트
        max_length: 최대 길이
        allow_html: HTML 허용 여부
        check_suspicious: 의심스러운 패턴 검사 여부
    
    Returns:
        정화된 텍스트
    
    Raises:
        ValidationError: 검증 실패 시
        SecurityError: 보안 위험 감지 시
    """
    if not isinstance(text, str):
        raise ValidationError("입력값은 문자열이어야 합니다.")
    
    # 길이 검증
    if len(text) > max_length:
        raise ValidationError(f"입력값이 너무 깁니다. (최대 {max_length}자)")
    
    # 빈 문자열 체크
    if not text.strip():
        raise ValidationError("빈 입력값은 허용되지 않습니다.")
    
    # 의심스러운 패턴 검사
    if check_suspicious:
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise SecurityError(f"의심스러운 패턴이 감지되었습니다: {pattern}")
    
    # SQL 인젝션 검사
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise SecurityError("SQL 인젝션 시도가 감지되었습니다.")
    
    # HTML 정화
    if allow_html:
        # 허용된 태그만 남기고 정화
        text = bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    else:
        # HTML 엔티티로 변환
        text = html.escape(text)
    
    return text.strip()


def sanitize_html(content: str, strict: bool = True) -> str:
    """
    HTML 콘텐츠 정화
    
    Args:
        content: HTML 콘텐츠
        strict: 엄격한 정화 여부
    
    Returns:
        정화된 HTML
    """
    if strict:
        # 모든 HTML 태그 제거
        return bleach.clean(content, tags=[], attributes={}, strip=True)
    else:
        # 안전한 태그만 허용
        return bleach.clean(
            content, 
            tags=ALLOWED_TAGS, 
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )


def validate_session_id(session_id: str) -> bool:
    """
    세션 ID 검증
    
    Args:
        session_id: 검증할 세션 ID
    
    Returns:
        유효성 여부
    """
    if not session_id:
        return False
    
    # 세션 ID 형식 검증 (영문자, 숫자, 하이픈, 언더스코어만 허용)
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        return False
    
    # 길이 검증 (10-100자)
    if not (10 <= len(session_id) <= 100):
        return False
    
    return True


def validate_file_upload(
    filename: str, 
    content_type: str, 
    file_size: int,
    max_size: int = 10 * 1024 * 1024  # 10MB
) -> bool:
    """
    파일 업로드 검증
    
    Args:
        filename: 파일명
        content_type: MIME 타입
        file_size: 파일 크기
        max_size: 최대 파일 크기
    
    Returns:
        유효성 여부
    """
    # 허용된 파일 확장자
    allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif'}
    
    # 허용된 MIME 타입
    allowed_mime_types = {
        'text/plain',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png', 
        'image/gif'
    }
    
    # 파일명 검증
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    # 확장자 검증
    file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    if file_ext not in allowed_extensions:
        return False
    
    # MIME 타입 검증
    if content_type not in allowed_mime_types:
        return False
    
    # 파일 크기 검증
    if file_size > max_size:
        return False
    
    return True


class RateLimiter:
    """레이트 리미터"""
    
    def __init__(self):
        self.requests = {}  # {key: [timestamps]}
        self.cleanup_interval = 300  # 5분마다 정리
        self.last_cleanup = time.time()
    
    def check_rate_limit(
        self, 
        key: str, 
        limit: int = 100, 
        window: int = 3600  # 1시간
    ) -> bool:
        """
        레이트 리미트 검사
        
        Args:
            key: 식별자 (IP, 사용자 ID 등)
            limit: 제한 횟수
            window: 시간 윈도우 (초)
        
        Returns:
            허용 여부
        """
        current_time = time.time()
        
        # 주기적 정리
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests(current_time - window)
            self.last_cleanup = current_time
        
        # 요청 기록 가져오기
        if key not in self.requests:
            self.requests[key] = []
        
        requests_list = self.requests[key]
        
        # 시간 윈도우 내의 요청만 남기기
        cutoff_time = current_time - window
        requests_list[:] = [req_time for req_time in requests_list if req_time > cutoff_time]
        
        # 제한 검사
        if len(requests_list) >= limit:
            return False
        
        # 현재 요청 기록
        requests_list.append(current_time)
        return True
    
    def _cleanup_old_requests(self, cutoff_time: float):
        """오래된 요청 기록 정리"""
        for key in list(self.requests.keys()):
            self.requests[key] = [
                req_time for req_time in self.requests[key] 
                if req_time > cutoff_time
            ]
            
            # 빈 리스트는 삭제
            if not self.requests[key]:
                del self.requests[key]


# 전역 레이트 리미터 인스턴스
_rate_limiter = RateLimiter()


def check_rate_limit(key: str, limit: int = 100, window: int = 3600) -> bool:
    """레이트 리미트 검사 (전역 함수)"""
    return _rate_limiter.check_rate_limit(key, limit, window)


def validate_url(url: str, allowed_schemes: List[str] = None) -> bool:
    """
    URL 검증
    
    Args:
        url: 검증할 URL
        allowed_schemes: 허용된 스킴 목록
    
    Returns:
        유효성 여부
    """
    if not url:
        return False
    
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    try:
        parsed = urlparse(url)
        
        # 스킴 검증
        if parsed.scheme not in allowed_schemes:
            return False
        
        # 호스트명 검증
        if not parsed.netloc:
            return False
        
        # 로컬 네트워크 접근 차단 (보안)
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False
        
        return True
        
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """이메일 주소 검증"""
    if not email or len(email) > 254:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def validate_phone_number(phone: str) -> bool:
    """전화번호 검증 (한국 형식)"""
    if not phone:
        return False
    
    # 하이픈 제거
    phone = phone.replace('-', '').replace(' ', '')
    
    # 한국 전화번호 패턴
    patterns = [
        r'^010\d{8}$',  # 휴대폰
        r'^02\d{7,8}$',  # 서울 지역번호
        r'^0\d{1,2}\d{7,8}$',  # 기타 지역번호
        r'^1\d{3}\d{4}$',  # 특수번호
    ]
    
    return any(re.match(pattern, phone) for pattern in patterns)