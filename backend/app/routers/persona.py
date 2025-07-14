"""
페르소나 관리 라우터
고객 페르소나 선택, 인사말 생성, 페르소나별 맞춤형 서비스 제공
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging

from ..utils.persona_utils import persona_manager
from ..config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/persona", tags=["persona"])

# 세션별 페르소나 매핑 (실제 서비스에서는 데이터베이스 또는 Redis 사용)
session_persona_map: Dict[str, dict] = {}


class PersonaSetRequest(BaseModel):
    """페르소나 설정 요청"""
    session_id: str
    persona_id: str


class PersonaGreetingRequest(BaseModel):
    """페르소나 인사말 요청"""
    session_id: str


class PersonaResponse(BaseModel):
    """페르소나 응답"""
    success: bool
    persona: Optional[dict] = None
    greeting: Optional[str] = None
    error: Optional[str] = None


@router.post("/set", response_model=PersonaResponse)
def set_persona(request: PersonaSetRequest):
    """세션별 페르소나 선택/적용 API"""
    try:
        persona = persona_manager.get_persona_by_id(request.persona_id)
        
        if not persona:
            logger.warning(f"페르소나를 찾을 수 없음: {request.persona_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"페르소나 ID '{request.persona_id}'를 찾을 수 없습니다."
            )
        
        session_persona_map[request.session_id] = persona
        
        logger.info(f"페르소나 설정 성공: 세션={request.session_id}, 페르소나={request.persona_id}")
        
        return PersonaResponse(
            success=True,
            persona=persona
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"페르소나 설정 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="페르소나 설정 중 오류가 발생했습니다.")


@router.get("/get")
def get_persona(session_id: str = Query(..., description="세션 ID")):
    """현재 세션의 페르소나 조회"""
    try:
        persona = session_persona_map.get(session_id)
        
        if not persona:
            logger.info(f"페르소나가 설정되지 않은 세션: {session_id}")
            return PersonaResponse(
                success=False,
                error="페르소나가 설정되지 않았습니다."
            )
        
        return PersonaResponse(
            success=True,
            persona=persona
        )
        
    except Exception as e:
        logger.error(f"페르소나 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="페르소나 조회 중 오류가 발생했습니다.")


@router.post("/greeting", response_model=PersonaResponse)
def get_persona_greeting(request: PersonaGreetingRequest):
    """페르소나 기반 맞춤형 인사말 생성 API"""
    try:
        persona = session_persona_map.get(request.session_id)
        
        if not persona:
            logger.warning(f"페르소나가 설정되지 않은 세션: {request.session_id}")
            return PersonaResponse(
                success=False,
                error="페르소나가 설정되지 않았습니다. 먼저 페르소나를 선택해주세요."
            )
        
        greeting = generate_persona_greeting(persona)
        
        logger.info(f"페르소나 인사말 생성 성공: 세션={request.session_id}")
        
        return PersonaResponse(
            success=True,
            greeting=greeting,
            persona=persona
        )
        
    except Exception as e:
        logger.error(f"페르소나 인사말 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="인사말 생성 중 오류가 발생했습니다.")


@router.get("/list")
def persona_list(
    keyword: str = Query(None, description="검색 키워드"), 
    limit: int = Query(100, description="최대 결과 수")
):
    """페르소나 목록 조회"""
    try:
        personas = persona_manager.list_personas(keyword=keyword, limit=limit)
        
        logger.info(f"페르소나 목록 조회: 키워드='{keyword}', 결과={len(personas)}개")
        
        return {
            "success": True,
            "personas": personas,
            "total": len(personas),
            "keyword": keyword
        }
        
    except Exception as e:
        logger.error(f"페르소나 목록 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="페르소나 목록 조회 중 오류가 발생했습니다.")


def generate_persona_greeting(persona: dict) -> str:
    """페르소나 정보를 바탕으로 맞춤형 인사말 생성"""
    이름 = persona.get('페르소나명', '고객')
    연령대 = persona.get('연령대', '')
    성별 = persona.get('성별', '')
    직업 = persona.get('직업', '')
    거주지 = persona.get('거주지', '')
    가족구성 = persona.get('가족 구성', '')
    차량정보 = persona.get('차량 정보', '')
    핵심니즈 = persona.get('핵심 니즈', '')
    가입상품 = persona.get('현재 가입 상품 (Hi-Care)', '')
    
    # 기본 인사말
    greeting = f"안녕하세요, {이름}님! 😊\n\n"
    
    # 연령대와 성별을 고려한 맞춤형 인사
    if '20대' in 연령대:
        greeting += "젊은 나이에 보험에 관심을 가지시다니 정말 현명하시네요! ☀️\n"
    elif '30대' in 연령대:
        greeting += "인생의 중요한 시기에 든든한 보장을 준비하시는군요! 👍\n"
    elif '40대' in 연령대:
        greeting += "가족과 미래를 위해 보험을 알아보시는 책임감이 대단하세요! 🏠\n"
    elif '50대' in 연령대:
        greeting += "인생의 안정과 노후 준비를 위해 찾아주셨네요! 🌟\n"
    elif '60대' in 연령대:
        greeting += "풍부한 경험과 지혜를 바탕으로 안전한 보장을 생각하시는군요! 👴\n"
    
    # 직업을 고려한 맞춤형 메시지
    if 'IT' in 직업 or '개발자' in 직업:
        greeting += "IT 분야에서 활약하시는 분이시군요. 바쁜 업무 중에도 보험 상담을 받으시려 하니 감사합니다.\n"
    elif '의사' in 직업:
        greeting += "의료진으로서 건강의 중요성을 잘 아시는 분이시네요. 더욱 안전한 보장을 위해 도와드리겠습니다.\n"
    elif '교사' in 직업 or '강사' in 직업:
        greeting += "교육 분야에서 활동하시는 분이시군요. 안정적인 보장을 위해 함께 알아보아요.\n"
    elif '주부' in 직업:
        greeting += "가정을 돌보시면서도 가족의 안전을 생각하시는 따뜻한 마음이 느껴져요.\n"
    elif '자영업' in 직업 or '대표' in 직업:
        greeting += "사업을 하시면서 위험 관리에 신경 쓰시는 모습이 인상적이네요.\n"
    elif '공무원' in 직업:
        greeting += "공직에서 봉사하시는 분이시군요. 안정적인 보장을 위해 도와드릴게요.\n"
    
    # 가족 구성을 고려한 맞춤형 메시지
    if '자녀' in 가족구성:
        greeting += "자녀가 있으시니 더욱 든든한 보장이 중요하시겠네요.\n"
    elif '1인 가구' in 가족구성:
        greeting += "1인 가구로서 스스로를 위한 보장을 생각하시는 모습이 좋으시네요.\n"
    elif '배우자' in 가족구성:
        greeting += "가족과 함께 하시는 만큼 안전한 보장이 더욱 중요하시겠어요.\n"
    
    # 차량 정보를 고려한 맞춤형 안내
    if '현대' in 차량정보:
        greeting += "현대 차량을 이용하고 계시는군요! Hi-Care와 더욱 잘 맞는 보장을 제공해드릴 수 있어요. 🚗\n"
    elif '기아' in 차량정보:
        greeting += "기아 차량을 이용하고 계시는군요! 안전한 운전을 위한 보장을 함께 준비해보아요. 🚗\n"
    elif '테슬라' in 차량정보 or '전기' in 차량정보:
        greeting += "전기차를 이용하시는군요! 친환경 운전을 위한 특별한 보장을 알려드릴게요. ⚡\n"
    elif '벤츠' in 차량정보 or 'BMW' in 차량정보 or '제네시스' in 차량정보:
        greeting += "프리미엄 차량을 이용하시는군요! 고급 차량에 맞는 완벽한 보장을 제공해드릴게요. 🏆\n"
    
    # 핵심 니즈를 고려한 맞춤형 안내
    if '보험료' in 핵심니즈:
        greeting += "합리적인 보험료에 관심이 많으시군요. 최적의 가격으로 든든한 보장을 제공해드릴게요! 💰\n"
    elif '안전' in 핵심니즈:
        greeting += "안전에 대한 관심이 높으시군요. 완벽한 보장으로 마음의 평안을 드리겠습니다! 🛡️\n"
    elif '편리' in 핵심니즈:
        greeting += "편리한 서비스를 원하시는군요. 간편하고 빠른 절차로 도와드리겠습니다! 📱\n"
    
    # 기존 가입 상품을 고려한 멘트
    if '자동차' in 가입상품:
        greeting += "이미 Hi-Care 자동차보험을 이용해주고 계시는군요! 감사합니다. 🚙\n"
    elif '건강' in 가입상품:
        greeting += "Hi-Care 건강보험 고객이시군요! 늘 건강한 일상을 응원하겠습니다. 💊\n"
    elif '생명' in 가입상품:
        greeting += "Hi-Care 생명보험으로 이미 든든한 준비를 하고 계시네요! 👨‍👩‍👧‍👦\n"
    
    # 마무리 멘트
    greeting += "\n어떤 것이 궁금하시거나 도움이 필요하시면 언제든 말씀해주세요! 햇살봇이 성심껏 도와드릴게요. ☀️"
    
    return greeting 