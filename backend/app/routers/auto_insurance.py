"""
자동차보험 가입 프로세스 라우터
단계별 대화형 자동차보험 가입 시스템
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from datetime import datetime

from ..utils.persona_utils import persona_manager
from ..config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auto-insurance", tags=["auto-insurance"])

# 세션별 가입 진행 상태 저장 (실제 서비스에서는 데이터베이스 사용)
session_progress: Dict[str, Dict] = {}


class SubscriptionStep(str, Enum):
    """가입 단계"""
    PERSONAL_INFO = "personal_info"
    IDENTITY_VERIFICATION = "identity_verification"
    VEHICLE_BASIC = "vehicle_basic"
    VEHICLE_DETAIL = "vehicle_detail"
    VEHICLE_OPTIONS = "vehicle_options"
    DRIVER_SCOPE = "driver_scope"
    DISCOUNT_OPTIONS = "discount_options"
    COVERAGE_REVIEW = "coverage_review"
    PAYMENT_COMPLETION = "payment_completion"


class VehicleType(str, Enum):
    """차량 종류"""
    PASSENGER = "승용차"
    VAN = "승합차"
    TRUCK = "화물차"


class DriverScope(str, Enum):
    """운전자 범위"""
    SELF_ONLY = "본인"
    COUPLE = "부부"
    FAMILY = "가족"
    ANYONE = "누구나"
    EMPLOYEE = "임직원"
    SELF_PLUS_ONE = "본인+1인"
    COUPLE_PLUS_ONE = "부부+1인"
    COUPLE_PLUS_CHILDREN = "부부+자녀"
    SELF_PLUS_CHILDREN = "본인+자녀"
    CHILDREN_ONLY = "자녀"


class PersonalInfoRequest(BaseModel):
    """개인정보 입력 요청"""
    session_id: str
    name: str
    resident_number: str  # 실제 서비스에서는 암호화 필요
    phone: str
    consents: Dict[str, bool]  # 동의 항목들


class VehicleBasicRequest(BaseModel):
    """차량 기본정보 요청"""
    session_id: str
    vehicle_number: Optional[str] = None
    chassis_number: Optional[str] = None
    purchase_planned: bool = False  # 구입 예정 여부
    vehicle_type: VehicleType


class VehicleDetailRequest(BaseModel):
    """차량 상세정보 요청"""
    session_id: str
    manufacturer: str  # 제조사
    model_name: str   # 대표차명
    year: int         # 등록연도
    detailed_model: str  # 세부차명
    detailed_spec: str   # 세부형식


class VehicleOptionsRequest(BaseModel):
    """차량 옵션 정보 요청"""
    session_id: str
    blackbox_installed: bool = False
    additional_parts: List[str] = []
    special_purpose: bool = False
    commercial_use: bool = False  # 요금 및 대가를 받는 경우
    leisure_towing: bool = False  # 레저장비 견인
    tuning: bool = False
    disability_conversion: bool = False  # 장애인보험전환 대상


class DriverScopeRequest(BaseModel):
    """운전자 범위 요청"""
    session_id: str
    driver_scope: DriverScope
    additional_info: Optional[Dict] = None


class DiscountOptionsRequest(BaseModel):
    """할인특약 요청"""
    session_id: str
    mileage_discount: Optional[int] = None  # 연간 주행거리
    safe_driving_discount: bool = False
    safe_driving_app: Optional[str] = None  # TMAP, 네이버 등
    blackbox_discount: bool = False
    child_discount: bool = False
    green_service: bool = False
    connected_car: bool = False
    advanced_safety: bool = False
    hi_work: bool = False  # 걸음수 할인
    monthly_safety_score: bool = False


class SubscriptionResponse(BaseModel):
    """가입 프로세스 응답"""
    success: bool
    session_id: str
    current_step: SubscriptionStep
    next_step: Optional[SubscriptionStep] = None
    progress_percentage: float
    step_data: Optional[Dict] = None
    recommendations: Optional[Dict] = None
    estimated_premium: Optional[int] = None
    error: Optional[str] = None


@router.post("/start", response_model=SubscriptionResponse)
def start_subscription(session_id: str):
    """자동차보험 가입 프로세스 시작"""
    try:
        # 세션 초기화
        session_progress[session_id] = {
            "current_step": SubscriptionStep.PERSONAL_INFO,
            "steps_completed": [],
            "data": {},
            "started_at": datetime.now().isoformat(),
            "persona": None
        }
        
        logger.info(f"자동차보험 가입 프로세스 시작: 세션={session_id}")
        
        return SubscriptionResponse(
            success=True,
            session_id=session_id,
            current_step=SubscriptionStep.PERSONAL_INFO,
            next_step=SubscriptionStep.IDENTITY_VERIFICATION,
            progress_percentage=0.0,
            step_data={
                "required_fields": ["name", "resident_number", "phone"],
                "consent_items": [
                    "개인정보 수집·이용 동의",
                    "개인정보 제3자 제공 동의", 
                    "마케팅 정보 수신 동의",
                    "본인인증 서비스 이용 동의"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"가입 프로세스 시작 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="가입 프로세스 시작 중 오류가 발생했습니다.")


@router.post("/personal-info", response_model=SubscriptionResponse)
def submit_personal_info(request: PersonalInfoRequest):
    """개인정보 입력 처리"""
    try:
        if request.session_id not in session_progress:
            raise HTTPException(status_code=404, detail="가입 세션을 찾을 수 없습니다.")
        
        session = session_progress[request.session_id]
        
        # 개인정보 저장 (실제 서비스에서는 암호화 필요)
        session["data"]["personal_info"] = {
            "name": request.name,
            "resident_number": request.resident_number,
            "phone": request.phone,
            "consents": request.consents
        }
        
        # 다음 단계로 진행
        session["current_step"] = SubscriptionStep.IDENTITY_VERIFICATION
        session["steps_completed"].append(SubscriptionStep.PERSONAL_INFO)
        
        # 페르소나 매칭 시도 (기본 정보 기반)
        customer_info = {
            "name": request.name,
            "phone": request.phone
        }
        
        logger.info(f"개인정보 입력 완료: 세션={request.session_id}")
        
        return SubscriptionResponse(
            success=True,
            session_id=request.session_id,
            current_step=SubscriptionStep.IDENTITY_VERIFICATION,
            next_step=SubscriptionStep.VEHICLE_BASIC,
            progress_percentage=11.1,  # 1/9 단계 완료
            step_data={
                "verification_methods": ["휴대폰 인증", "카카오페이 인증", "PASS 인증"],
                "message": "본인인증을 진행해주세요."
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"개인정보 입력 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="개인정보 입력 중 오류가 발생했습니다.")


@router.post("/vehicle-basic", response_model=SubscriptionResponse)
def submit_vehicle_basic(request: VehicleBasicRequest):
    """차량 기본정보 입력 처리"""
    try:
        if request.session_id not in session_progress:
            raise HTTPException(status_code=404, detail="가입 세션을 찾을 수 없습니다.")
        
        session = session_progress[request.session_id]
        
        # 차량 기본정보 저장
        session["data"]["vehicle_basic"] = {
            "vehicle_number": request.vehicle_number,
            "chassis_number": request.chassis_number,
            "purchase_planned": request.purchase_planned,
            "vehicle_type": request.vehicle_type.value
        }
        
        # 다음 단계로 진행
        session["current_step"] = SubscriptionStep.VEHICLE_DETAIL
        session["steps_completed"].append(SubscriptionStep.VEHICLE_BASIC)
        
        logger.info(f"차량 기본정보 입력 완료: 세션={request.session_id}")
        
        return SubscriptionResponse(
            success=True,
            session_id=request.session_id,
            current_step=SubscriptionStep.VEHICLE_DETAIL,
            next_step=SubscriptionStep.VEHICLE_OPTIONS,
            progress_percentage=33.3,  # 3/9 단계 완료
            step_data={
                "manufacturers": ["현대", "기아", "쉐보레", "르노삼성", "쌍용", "BMW", "벤츠", "아우디", "토요타", "렉서스", "테슬라"],
                "message": "차량 상세정보를 입력해주세요. 제조사부터 선택해주세요."
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"차량 기본정보 입력 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="차량 기본정보 입력 중 오류가 발생했습니다.")


@router.post("/vehicle-detail", response_model=SubscriptionResponse)
def submit_vehicle_detail(request: VehicleDetailRequest):
    """차량 상세정보 입력 처리"""
    try:
        if request.session_id not in session_progress:
            raise HTTPException(status_code=404, detail="가입 세션을 찾을 수 없습니다.")
        
        session = session_progress[request.session_id]
        
        # 차량 상세정보 저장
        session["data"]["vehicle_detail"] = {
            "manufacturer": request.manufacturer,
            "model_name": request.model_name,
            "year": request.year,
            "detailed_model": request.detailed_model,
            "detailed_spec": request.detailed_spec
        }
        
        # 페르소나 매칭 업데이트 (차량 정보 추가)
        customer_info = {
            "vehicle": f"{request.manufacturer} {request.model_name}"
        }
        
        # 다음 단계로 진행
        session["current_step"] = SubscriptionStep.VEHICLE_OPTIONS
        session["steps_completed"].append(SubscriptionStep.VEHICLE_DETAIL)
        
        logger.info(f"차량 상세정보 입력 완료: 세션={request.session_id}")
        
        return SubscriptionResponse(
            success=True,
            session_id=request.session_id,
            current_step=SubscriptionStep.VEHICLE_OPTIONS,
            next_step=SubscriptionStep.DRIVER_SCOPE,
            progress_percentage=44.4,  # 4/9 단계 완료
            step_data={
                "blackbox_discount_rate": "2.2% ~ 6.7%",
                "message": "차량 옵션 정보를 입력해주세요. 블랙박스 설치 시 할인 혜택이 있습니다."
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"차량 상세정보 입력 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="차량 상세정보 입력 중 오류가 발생했습니다.")


@router.post("/driver-scope", response_model=SubscriptionResponse)
def submit_driver_scope(request: DriverScopeRequest):
    """운전자 범위 입력 처리"""
    try:
        if request.session_id not in session_progress:
            raise HTTPException(status_code=404, detail="가입 세션을 찾을 수 없습니다.")
        
        session = session_progress[request.session_id]
        
        # 운전자 범위 저장
        session["data"]["driver_scope"] = {
            "driver_scope": request.driver_scope.value,
            "additional_info": request.additional_info
        }
        
        # 페르소나 기반 할인 특약 추천
        recommendations = {}
        if session.get("persona"):
            recommendations = persona_manager.get_personalized_recommendations(session["persona"])
        
        # 다음 단계로 진행
        session["current_step"] = SubscriptionStep.DISCOUNT_OPTIONS
        session["steps_completed"].append(SubscriptionStep.DRIVER_SCOPE)
        
        logger.info(f"운전자 범위 입력 완료: 세션={request.session_id}")
        
        return SubscriptionResponse(
            success=True,
            session_id=request.session_id,
            current_step=SubscriptionStep.DISCOUNT_OPTIONS,
            next_step=SubscriptionStep.COVERAGE_REVIEW,
            progress_percentage=66.7,  # 6/9 단계 완료
            step_data={
                "available_discounts": [
                    {"name": "마일리지할인", "description": "연간 주행거리에 따른 할인"},
                    {"name": "안전운전할인", "description": "텔레매틱스/UBI 기반 할인"},
                    {"name": "블랙박스할인", "description": "블랙박스 설치 시 할인"},
                    {"name": "자녀할인", "description": "자녀가 있는 경우 할인"},
                    {"name": "그린서비스", "description": "친환경 서비스 할인"},
                    {"name": "커넥티드카", "description": "스마트카 연동 할인"}
                ],
                "message": "할인 특약을 선택해주세요. 고객님께 맞는 할인 혜택을 추천드립니다."
            },
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"운전자 범위 입력 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="운전자 범위 입력 중 오류가 발생했습니다.")


@router.post("/calculate-premium")
def calculate_premium(session_id: str):
    """보험료 계산"""
    try:
        if session_id not in session_progress:
            raise HTTPException(status_code=404, detail="가입 세션을 찾을 수 없습니다.")
        
        session = session_progress[session_id]
        data = session["data"]
        
        # 기본 보험료 (차종, 연령, 운전경력 등 고려)
        base_premium = 100000  # 기본 10만원
        
        # 차량 종류별 조정
        vehicle_type = data.get("vehicle_basic", {}).get("vehicle_type", "")
        if vehicle_type == "승용차":
            base_premium *= 1.0
        elif vehicle_type == "승합차":
            base_premium *= 1.2
        elif vehicle_type == "화물차":
            base_premium *= 1.5
        
        # 할인 적용
        total_discount = 0.0
        discount_info = data.get("discount_options", {})
        
        if discount_info.get("blackbox_discount"):
            total_discount += 0.05  # 5% 할인
        
        if discount_info.get("mileage_discount"):
            mileage = discount_info["mileage_discount"]
            if mileage <= 5000:
                total_discount += 0.15  # 15% 할인
            elif mileage <= 10000:
                total_discount += 0.10  # 10% 할인
            elif mileage <= 15000:
                total_discount += 0.05  # 5% 할인
        
        if discount_info.get("safe_driving_discount"):
            total_discount += 0.10  # 10% 할인
        
        # 최종 보험료 계산
        final_premium = int(base_premium * (1 - total_discount))
        
        session["data"]["calculated_premium"] = {
            "base_premium": int(base_premium),
            "total_discount_rate": total_discount,
            "final_premium": final_premium,
            "calculated_at": datetime.now().isoformat()
        }
        
        logger.info(f"보험료 계산 완료: 세션={session_id}, 보험료={final_premium}")
        
        return {
            "success": True,
            "session_id": session_id,
            "premium_info": {
                "base_premium": int(base_premium),
                "discount_rate": total_discount,
                "final_premium": final_premium,
                "monthly_premium": final_premium // 12
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"보험료 계산 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="보험료 계산 중 오류가 발생했습니다.")


@router.get("/progress/{session_id}")
def get_progress(session_id: str):
    """가입 진행 상황 조회"""
    try:
        if session_id not in session_progress:
            raise HTTPException(status_code=404, detail="가입 세션을 찾을 수 없습니다.")
        
        session = session_progress[session_id]
        
        total_steps = len(SubscriptionStep)
        completed_steps = len(session["steps_completed"])
        progress_percentage = (completed_steps / total_steps) * 100
        
        return {
            "success": True,
            "session_id": session_id,
            "current_step": session["current_step"],
            "steps_completed": session["steps_completed"],
            "progress_percentage": progress_percentage,
            "data": session["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"진행 상황 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="진행 상황 조회 중 오류가 발생했습니다.")


@router.get("/vehicle-models/{manufacturer}")
def get_vehicle_models(manufacturer: str):
    """제조사별 차량 모델 목록 조회 (실제 서비스에서는 DB 연동)"""
    try:
        # 샘플 데이터 (실제로는 차량 DB에서 조회)
        vehicle_models = {
            "현대": ["아반떼", "쏘나타", "그랜저", "코나", "투싼", "싼타페", "팰리세이드", "캐스퍼", "아이오닉5"],
            "기아": ["K3", "K5", "K8", "스포티지", "쏘렌토", "모하비", "카니발", "레이", "EV6"],
            "쉐보레": ["스파크", "크루즈", "말리부", "이쿼녹스", "트레일블레이저", "타호"],
            "BMW": ["1시리즈", "3시리즈", "5시리즈", "7시리즈", "X1", "X3", "X5", "X7"],
            "벤츠": ["A클래스", "C클래스", "E클래스", "S클래스", "GLA", "GLC", "GLE", "GLS"],
            "테슬라": ["Model 3", "Model Y", "Model S", "Model X"]
        }
        
        models = vehicle_models.get(manufacturer, [])
        
        return {
            "success": True,
            "manufacturer": manufacturer,
            "models": models
        }
        
    except Exception as e:
        logger.error(f"차량 모델 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="차량 모델 조회 중 오류가 발생했습니다.")