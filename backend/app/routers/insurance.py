"""
보험 업무 라우터
보험 상품 정보, 보험료 계산, 개인정보 검증, 가입 신청 등
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging

from ..utils.security import (
    security_handler, 
    audit_logger, 
    data_validator,
    audit_personal_data_access
)
from ..config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insurance", tags=["insurance"])


class PersonalDataValidationRequest(BaseModel):
    """개인정보 검증 요청"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[str] = None
    address: Optional[str] = None


class PersonalDataValidationResponse(BaseModel):
    """개인정보 검증 응답"""
    is_valid: bool
    errors: Dict = {}
    warnings: List = []
    sanitized_data: Dict = {}


class SecureInsuranceApplicationRequest(BaseModel):
    """보안 강화 보험 가입 신청"""
    session_id: str
    form_data: Dict
    persona: Optional[Dict] = None
    consent_agreements: Dict
    security_metadata: Optional[Dict] = None


@router.post("/validate-personal-data", response_model=PersonalDataValidationResponse)
@audit_personal_data_access("validate", "personal_info")
def validate_personal_data(request: PersonalDataValidationRequest, session_id: str = "unknown"):
    """개인정보 유효성 검증 API"""
    try:
        logger.info(f"개인정보 검증 요청: 세션={session_id}")
        
        # 개인정보를 딕셔너리로 변환
        personal_data = request.dict(exclude_none=True)
        
        if not personal_data:
            return PersonalDataValidationResponse(
                is_valid=False,
                errors={"general": "검증할 개인정보가 제공되지 않았습니다."}
            )
        
        # 데이터 검증
        validation_result = data_validator.validate_personal_data(personal_data)
        
        # 로깅
        logger.info(f"개인정보 검증 완료: 유효={validation_result['is_valid']}")
        
        return PersonalDataValidationResponse(**validation_result)
        
    except Exception as e:
        logger.error(f"개인정보 검증 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="개인정보 검증 중 오류가 발생했습니다.")


@router.post("/submit-secure-application")
@audit_personal_data_access("submit", "insurance_application")
def submit_secure_insurance_application(request: SecureInsuranceApplicationRequest):
    """보안 강화 보험 가입 신청 API"""
    try:
        logger.info(f"보험 가입 신청: 세션={request.session_id}")
        
        # 1. 보안 검증
        security_check = security_handler.verify_application_security(
            request.form_data,
            request.consent_agreements,
            request.security_metadata or {}
        )
        
        if not security_check["is_secure"]:
            logger.warning(f"보안 검증 실패: {security_check.get('reason', 'unknown')}")
            raise HTTPException(
                status_code=400, 
                detail=f"보안 검증 실패: {security_check.get('reason', '알 수 없는 오류')}"
            )
        
        # 2. 필수 동의 항목 확인
        required_consents = ["개인정보처리동의", "마케팅동의", "서비스이용약관"]
        missing_consents = [
            consent for consent in required_consents 
            if not request.consent_agreements.get(consent, False)
        ]
        
        if missing_consents:
            raise HTTPException(
                status_code=400,
                detail=f"필수 동의 항목이 누락되었습니다: {', '.join(missing_consents)}"
            )
        
        # 3. 폼 데이터 검증
        if not request.form_data:
            raise HTTPException(status_code=400, detail="가입 신청 데이터가 비어있습니다.")
        
        # 4. 필수 필드 검증
        required_fields = ["이름", "전화번호", "이메일", "생년월일"]
        missing_fields = [
            field for field in required_fields 
            if not request.form_data.get(field)
        ]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"필수 입력 항목이 누락되었습니다: {', '.join(missing_fields)}"
            )
        
        # 5. 신청서 처리 (실제 구현에서는 외부 시스템 연동)
        application_id = f"APP_{request.session_id}_{int(__import__('time').time())}"
        
        application_data = {
            "application_id": application_id,
            "session_id": request.session_id,
            "form_data": request.form_data,
            "persona": request.persona,
            "consent_agreements": request.consent_agreements,
            "security_metadata": request.security_metadata,
            "status": "접수완료",
            "created_at": __import__('time').time()
        }
        
        # 6. 감사 로그 기록
        audit_logger.log_insurance_application(application_data)
        
        logger.info(f"보험 가입 신청 완료: ID={application_id}")
        
        return {
            "success": True,
            "application_id": application_id,
            "status": "접수완료",
            "message": "보험 가입 신청이 성공적으로 접수되었습니다. 영업일 기준 1-2일 내에 연락드리겠습니다.",
            "next_steps": [
                "신청서 검토 (1-2 영업일)",
                "본인 확인 연락 (유선)",
                "최종 승인 및 계약서 발송",
                "보험료 납입 안내"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"보험 가입 신청 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="보험 가입 신청 처리 중 오류가 발생했습니다.")


@router.get("/products")
def get_insurance_products(category: Optional[str] = None, limit: int = 10):
    """보험 상품 목록 조회"""
    try:
        # 실제 구현에서는 데이터베이스나 외부 API에서 조회
        products = [
            {
                "id": "auto_basic",
                "name": "Hi-Care 자동차보험 (기본형)",
                "category": "자동차보험",
                "monthly_premium": "7만원대",
                "coverage": "대인/대물/자손/자차",
                "features": ["24시간 사고접수", "무료 견인서비스", "렌터카 지원"]
            },
            {
                "id": "health_premium",
                "name": "Hi-Care 건강보험 (프리미엄)",
                "category": "건강보험",
                "monthly_premium": "12만원대",
                "coverage": "실손의료비/암진단/수술비",
                "features": ["MRI/CT 100% 보장", "항암치료비 지원", "2차 의료진 서비스"]
            },
            {
                "id": "life_family",
                "name": "Hi-Care 가족생명보험",
                "category": "생명보험",
                "monthly_premium": "15만원대",
                "coverage": "사망/후유장해/암진단",
                "features": ["가족 모두 보장", "생존급여 지급", "만기환급금"]
            }
        ]
        
        # 카테고리 필터링
        if category:
            products = [p for p in products if p["category"] == category]
        
        # 제한
        products = products[:limit]
        
        logger.info(f"보험 상품 조회: 카테고리={category}, 결과={len(products)}개")
        
        return {
            "success": True,
            "products": products,
            "total": len(products),
            "category": category
        }
        
    except Exception as e:
        logger.error(f"보험 상품 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="보험 상품 조회 중 오류가 발생했습니다.")


@router.post("/calculate-premium")
def calculate_insurance_premium(calculation_data: Dict):
    """보험료 계산 API"""
    try:
        logger.info("보험료 계산 요청")
        
        # 필수 데이터 검증
        if not calculation_data:
            raise HTTPException(status_code=400, detail="계산 데이터가 제공되지 않았습니다.")
        
        # 기본 계산 로직 (실제 구현에서는 복잡한 보험료 계산 엔진 사용)
        product_type = calculation_data.get("product_type", "auto")
        age = calculation_data.get("age", 30)
        coverage_amount = calculation_data.get("coverage_amount", 1000000)
        
        # 간단한 보험료 계산
        base_premium = 50000  # 기본 보험료
        
        # 나이별 할증/할인
        if age < 25:
            age_factor = 1.3  # 젊은 연령 할증
        elif age < 35:
            age_factor = 1.0  # 기준
        elif age < 50:
            age_factor = 0.9  # 중년 할인
        else:
            age_factor = 1.1  # 고령 할증
        
        # 보장금액별 조정
        coverage_factor = min(coverage_amount / 1000000, 5.0)
        
        calculated_premium = int(base_premium * age_factor * coverage_factor)
        
        result = {
            "monthly_premium": calculated_premium,
            "annual_premium": calculated_premium * 12,
            "calculation_factors": {
                "base_premium": base_premium,
                "age_factor": age_factor,
                "coverage_factor": coverage_factor
            },
            "discounts": [],
            "surcharges": []
        }
        
        # 할인 적용
        if calculation_data.get("no_claim_discount"):
            result["discounts"].append({"name": "무사고 할인", "rate": 0.1})
            result["monthly_premium"] = int(result["monthly_premium"] * 0.9)
        
        logger.info(f"보험료 계산 완료: 월 보험료={result['monthly_premium']:,}원")
        
        return {
            "success": True,
            "calculation_result": result,
            "input_data": calculation_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"보험료 계산 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="보험료 계산 중 오류가 발생했습니다.") 