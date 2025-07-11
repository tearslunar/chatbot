import hashlib
import hmac
import secrets
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

# 🔐 보안 설정
SECURITY_KEY = os.environ.get("SECURITY_ENCRYPTION_KEY", "hi-care-server-security-key-2024")
SALT = b'hi_care_salt_2024'

# 암호화 키 생성
def generate_encryption_key(password: str, salt: bytes) -> bytes:
    """PBKDF2를 사용하여 보안 키 생성"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

# 전역 암호화 객체
_fernet = Fernet(generate_encryption_key(SECURITY_KEY, SALT))

class PersonalDataSecurity:
    """개인정보 보안 처리 클래스"""
    
    @staticmethod
    def encrypt_personal_data(data: str) -> str:
        """개인정보 암호화"""
        try:
            if not data or not isinstance(data, str):
                return ""
            
            encrypted_data = _fernet.encrypt(data.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logging.error(f"[보안] 암호화 실패: {e}")
            return ""
    
    @staticmethod
    def decrypt_personal_data(encrypted_data: str) -> str:
        """개인정보 복호화"""
        try:
            if not encrypted_data or not isinstance(encrypted_data, str):
                return ""
            
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = _fernet.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logging.error(f"[보안] 복호화 실패: {e}")
            return ""
    
    @staticmethod
    def hash_sensitive_data(data: str) -> str:
        """민감정보 해시 처리 (검색용)"""
        try:
            if not data:
                return ""
            
            return hashlib.sha256(data.encode('utf-8')).hexdigest()
        except Exception as e:
            logging.error(f"[보안] 해시 실패: {e}")
            return ""
    
    @staticmethod
    def mask_personal_data(data: str, data_type: str) -> str:
        """개인정보 마스킹 처리"""
        if not data or not isinstance(data, str):
            return ""
        
        data = data.strip()
        
        if data_type == 'name':
            if len(data) <= 2:
                return data[0] + '*'
            return data[0] + '*' * (len(data) - 2) + data[-1]
        
        elif data_type == 'phone':
            # 010-1234-5678 → 010-****-5678
            if len(data) >= 11:
                return data[:3] + '-****-' + data[-4:]
            return data
        
        elif data_type == 'email':
            # example@email.com → ex***@email.com
            if '@' in data:
                local, domain = data.split('@', 1)
                if len(local) > 2:
                    masked_local = local[:2] + '*' * (len(local) - 2)
                else:
                    masked_local = local[0] + '*'
                return f"{masked_local}@{domain}"
            return data
        
        elif data_type == 'card':
            # 카드번호 마스킹
            digits_only = ''.join(filter(str.isdigit, data))
            if len(digits_only) >= 8:
                return digits_only[:4] + '-****-****-' + digits_only[-4:]
            return '*' * len(data)
        
        else:
            # 기본 마스킹
            if len(data) <= 4:
                return data[0] + '*' * (len(data) - 1)
            return data[:2] + '*' * (len(data) - 4) + data[-2:]

class SecurityAuditLogger:
    """보안 감사 로그 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger('security_audit')
        handler = logging.FileHandler('security_audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_personal_data_access(
        self, 
        action: str, 
        data_type: str, 
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """개인정보 접근 로그"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': action,
            'data_type': data_type,
            'user_id': user_id,
            'session_id': session_id,
            'metadata': metadata or {},
            'event_id': secrets.token_hex(16)
        }
        
        self.logger.info(f"PERSONAL_DATA_ACCESS: {json.dumps(log_entry)}")
    
    def log_security_event(
        self, 
        event_type: str, 
        severity: str, 
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """보안 이벤트 로그"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'severity': severity,
            'description': description,
            'metadata': metadata or {},
            'event_id': secrets.token_hex(16)
        }
        
        self.logger.warning(f"SECURITY_EVENT: {json.dumps(log_entry)}")
    
    def log_data_processing(
        self,
        process_type: str,
        data_count: int,
        session_id: Optional[str] = None,
        success: bool = True
    ):
        """데이터 처리 로그"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'process_type': process_type,
            'data_count': data_count,
            'session_id': session_id,
            'success': success,
            'event_id': secrets.token_hex(16)
        }
        
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, f"DATA_PROCESSING: {json.dumps(log_entry)}")

class DataValidation:
    """데이터 유효성 검증 클래스"""
    
    @staticmethod
    def validate_korean_name(name: str) -> bool:
        """한국어 이름 유효성 검증"""
        if not name or len(name.strip()) < 2:
            return False
        
        # 한글, 영문만 허용 (특수문자 제외)
        import re
        pattern = re.compile(r'^[가-힣a-zA-Z\s]{2,10}$')
        return bool(pattern.match(name.strip()))
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """전화번호 유효성 검증"""
        if not phone:
            return False
        
        import re
        # 010-1234-5678 또는 01012345678 형식
        pattern = re.compile(r'^010[-\s]?\d{4}[-\s]?\d{4}$')
        return bool(pattern.match(phone.replace(' ', '')))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """이메일 유효성 검증"""
        if not email:
            return False
        
        import re
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(pattern.match(email))
    
    @staticmethod
    def validate_card_number(card_number: str) -> bool:
        """카드번호 유효성 검증 (Luhn 알고리즘)"""
        if not card_number:
            return False
        
        # 숫자만 추출
        digits = ''.join(filter(str.isdigit, card_number))
        
        if len(digits) != 16:
            return False
        
        # Luhn 알고리즘 검증
        def luhn_check(card_num):
            total = 0
            reverse_digits = card_num[::-1]
            
            for i, char in enumerate(reverse_digits):
                n = int(char)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n = n // 10 + n % 10
                total += n
            
            return total % 10 == 0
        
        return luhn_check(digits)

# 전역 인스턴스
audit_logger = SecurityAuditLogger()
security_handler = PersonalDataSecurity()
data_validator = DataValidation()

# 보안 데코레이터
def audit_personal_data_access(action: str, data_type: str):
    """개인정보 접근 감사 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            session_id = kwargs.get('session_id', 'unknown')
            
            # 접근 로그
            audit_logger.log_personal_data_access(
                action=action,
                data_type=data_type,
                session_id=session_id
            )
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # 오류 로그
                audit_logger.log_security_event(
                    event_type='PERSONAL_DATA_ACCESS_ERROR',
                    severity='HIGH',
                    description=f"개인정보 접근 중 오류 발생: {str(e)}",
                    metadata={'function': func.__name__, 'session_id': session_id}
                )
                raise
        
        return wrapper
    return decorator 