"""
암호화 및 해싱 유틸리티
"""

import os
import hashlib
import secrets
import base64
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt
import jwt
from datetime import datetime, timedelta

from ..config.settings import settings


class CryptoManager:
    """암호화 관리자"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or settings.secret_key
        self._fernet = None
    
    def _get_fernet(self) -> Fernet:
        """Fernet 암호화 인스턴스 생성"""
        if self._fernet is None:
            # 시크릿 키에서 32바이트 키 유도
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'hicare_salt_2024',  # 고정 솔트 (실제로는 환경변수로 관리)
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
            self._fernet = Fernet(key)
        return self._fernet
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """데이터 암호화"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """데이터 복호화"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            fernet = self._get_fernet()
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"복호화 실패: {str(e)}")


# 전역 암호화 매니저
_crypto_manager = CryptoManager()


def encrypt_sensitive_data(data: str) -> str:
    """민감한 데이터 암호화"""
    return _crypto_manager.encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """민감한 데이터 복호화"""
    return _crypto_manager.decrypt(encrypted_data)


def hash_password(password: str) -> str:
    """비밀번호 해싱 (bcrypt 사용)"""
    if not password:
        raise ValueError("비밀번호가 비어있습니다.")
    
    # bcrypt로 해싱
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    if not password or not hashed_password:
        return False
    
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def generate_secure_token(length: int = 32) -> str:
    """보안 토큰 생성"""
    return secrets.token_urlsafe(length)


def generate_session_id() -> str:
    """세션 ID 생성"""
    timestamp = str(int(datetime.utcnow().timestamp()))
    random_part = secrets.token_urlsafe(16)
    return f"session_{timestamp}_{random_part}"


def hash_data(data: str, algorithm: str = 'sha256') -> str:
    """데이터 해싱"""
    if algorithm == 'sha256':
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(f"지원하지 않는 해싱 알고리즘: {algorithm}")


def generate_api_key() -> str:
    """API 키 생성"""
    prefix = "hc_"  # hi-care 접두사
    key_part = secrets.token_urlsafe(32)
    return f"{prefix}{key_part}"


class TokenManager:
    """JWT 토큰 관리자"""
    
    def __init__(self, secret_key: Optional[str] = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or settings.secret_key
        self.algorithm = algorithm
    
    def create_token(
        self, 
        payload: dict, 
        expires_in: int = 3600
    ) -> str:
        """JWT 토큰 생성"""
        now = datetime.utcnow()
        payload.update({
            'iat': now,  # 발급 시간
            'exp': now + timedelta(seconds=expires_in),  # 만료 시간
            'jti': generate_secure_token(16)  # 토큰 ID
        })
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            raise ValueError("유효하지 않은 토큰입니다.")
    
    def refresh_token(self, token: str, new_expires_in: int = 3600) -> str:
        """토큰 갱신"""
        try:
            # 만료 검증을 건너뛰고 페이로드 추출
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            
            # 새로운 토큰 생성 (기존 페이로드 유지, 시간 갱신)
            del payload['iat']
            del payload['exp']
            del payload['jti']
            
            return self.create_token(payload, new_expires_in)
            
        except jwt.InvalidTokenError:
            raise ValueError("유효하지 않은 토큰입니다.")


# 전역 토큰 매니저
_token_manager = TokenManager()


def generate_token(payload: dict, expires_in: int = 3600) -> str:
    """JWT 토큰 생성 (전역 함수)"""
    return _token_manager.create_token(payload, expires_in)


def verify_token(token: str) -> dict:
    """JWT 토큰 검증 (전역 함수)"""
    return _token_manager.verify_token(token)


def create_csrf_token() -> str:
    """CSRF 토큰 생성"""
    return generate_secure_token(24)


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """민감한 데이터 마스킹"""
    if not data or len(data) <= visible_chars:
        return "*" * len(data) if data else ""
    
    visible_part = data[:visible_chars]
    masked_part = "*" * (len(data) - visible_chars)
    return visible_part + masked_part


def generate_otp(length: int = 6) -> str:
    """OTP (일회용 비밀번호) 생성"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def constant_time_compare(a: str, b: str) -> bool:
    """상수 시간 문자열 비교 (타이밍 공격 방지)"""
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    
    return result == 0