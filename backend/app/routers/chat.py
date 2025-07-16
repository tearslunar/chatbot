"""
채팅 라우터
AI 챗봇과의 대화 처리, 감정 분석, RAG 검색 통합
"""


import logging
import random
import time
from typing import Dict, List, Optional
import json  # json 모듈 추가

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session


from ..sentiment.advanced import emotion_analyzer
from ..utils.chat import get_potensdot_answer_with_fallback, extract_insurance_entities
from ..utils.emotion_response import emotion_response
from ..rag.faq_rag import search_faqs
from ..rag.hybrid_rag import search_hybrid
from ..config.settings import settings
from ..exceptions import (
    ValidationError, 
    EmotionAnalysisError, 
    RAGSearchError, 
    APIConnectionError,
    SessionError
)
from ..database import get_db
from ..repositories.session_repository import SessionRepository, MessageRepository
from ..utils.persona_utils import persona_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

session_repository = SessionRepository()
message_repository = MessageRepository()


class ChatRequest(BaseModel):
    """채팅 요청"""
    message: str
    model: str = "claude-3.7-sonnet"
    history: Optional[List[Dict]] = None
    session_id: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValidationError('메시지가 비어있습니다.', field='message')
        if len(v) > 1000:
            raise ValidationError('메시지가 너무 깁니다. (최대 1000자)', field='message')
        return v.strip()
    
    @validator('model')
    def validate_model(cls, v):
        allowed_models = [
            "claude-3.7-sonnet", 
            "claude-4.0-sonnet", 
            "claude-3.5-haiku", 
            "claude-3.7-sonnet-extended"
        ]
        if v not in allowed_models:
            raise ValidationError(f'지원하지 않는 모델입니다: {v}', field='model')
        return v
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if v and (len(v) < 10 or len(v) > 100):
            raise ValidationError('세션 ID 형식이 올바르지 않습니다.', field='session_id')
        return v


class ChatResponse(BaseModel):
    """채팅 응답"""
    answer: str
    entities: Optional[Dict] = None
    emotion: Optional[Dict] = None
    escalation_needed: bool = False
    recommended_faqs: Optional[List] = None
    conversation_flow: Optional[Dict] = None
    search_strategy: Optional[str] = None
    processing_time: Optional[float] = None
    session_ended: bool = False
    # 감정 격화 관련 필드 추가
    escalation_analysis: Optional[Dict] = None
    intervention_type: Optional[str] = None
    requires_human_support: bool = False


class RatingSubmitRequest(BaseModel):
    """평점 제출 요청"""
    session_id: str
    rating: int
    feedback: str = ""
    timestamp: str
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValidationError('평점은 1-5 사이의 값이어야 합니다.', field='rating')
        return v
    
    @validator('feedback')
    def validate_feedback(cls, v):
        if len(v) > 500:
            raise ValidationError('피드백은 500자를 초과할 수 없습니다.', field='feedback')
        return v
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not v or len(v) < 10:
            raise ValidationError('올바른 세션 ID가 필요합니다.', field='session_id')
        return v


@router.post("/message", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    """메인 채팅 엔드포인트"""
    start_time = time.time()
    
    logger.info(f"채팅 요청: 세션={req.session_id}, 메시지 길이={len(req.message)}")
    
    # 1. 세션 및 페르소나 정보 조회
    persona_info = None
    persona_recommendations = None
    try:
        session = session_repository.get_by_session_id(db, session_id=req.session_id)
        if session and session.persona_id:
            persona_info = persona_manager.get_persona_by_id(session.persona_id)
            if persona_info:
                persona_recommendations = persona_manager.get_personalized_recommendations(persona_info)
                logger.info(f"페르소나 정보 로드: {persona_info.get('ID', 'unknown')}")
            else:
                logger.warning(f"DB에 persona_id {session.persona_id}가 있지만, persona_manager에 해당 페르소나가 없습니다.")
    except Exception as e:
        logger.warning(f"페르소나 정보 로드 실패: {str(e)}")
    
    # 2. 감정 분석
    emotion_result = None
    try:
        emotion_result = emotion_analyzer.analyze_emotion(req.message)
        logger.info(f"감정 분석 완료: {emotion_result.get('emotion', 'unknown')}")
    except Exception as e:
        logger.warning(f"감정 분석 실패: {str(e)}")
        # 감정 분석 실패 시 기본값 사용 (서비스 계속 진행)
        emotion_result = {"emotion": "중립", "confidence": 0.5}
        
    # 3. 보험 엔터티 추출
    entities = None
    try:
        entities = extract_insurance_entities(req.message)
        logger.info(f"엔터티 추출 완료: {len(entities) if entities else 0}개")
    except Exception as e:
        logger.warning(f"엔터티 추출 실패: {str(e)}")
        entities = {}
    
    # 4. RAG 검색 (페르소나 정보 결합)
    rag_results = []
    search_strategy = "none"
    search_query = req.message

    try:
        if persona_info:
            # 페르소나 정보를 바탕으로 검색 쿼리 보강
            persona_keywords = f"{persona_info.get('연령대', '')} {persona_info.get('직업', '')} {persona_info.get('가족 구성', '')}"
            if "추천" in req.message or "상품" in req.message:
                search_query = f"{persona_keywords}에게 적합한 보험 상품 추천"
                logger.info(f"페르소나 기반 검색 쿼리 생성: {search_query}")
            else:
                search_query = f"{req.message} ({persona_keywords} 관련)"

        rag_results = search_hybrid(search_query, max_results=settings.max_rag_results)
        search_strategy = "persona_hybrid" if persona_info else "hybrid"
        logger.info(f"RAG 검색 완료 ({search_strategy}): {len(rag_results)}개 결과")

    except Exception as e:
        logger.warning(f"RAG 검색 실패: {str(e)}")
        # 폴백: FAQ 검색만 시도
        try:
            rag_results = search_faqs(req.message, top_n=3)
            search_strategy = "faq_only"
            logger.info(f"폴백 FAQ 검색 완료: {len(rag_results)}개 결과")
        except Exception as e2:
            logger.error(f"폴백 검색도 실패: {str(e2)}")
            rag_results = []
            search_strategy = "failed"

    # 5. 메인 AI 응답 생성 (페르소나 정보 활용)
    try:
        # 페르소나 기반 응답 커스터마이징
        enhanced_persona_info = entities.copy() if entities else {}
        if persona_info:
            enhanced_persona_info.update({
                "persona_data": persona_info,
                "recommendations": persona_recommendations,
                "communication_tone": persona_recommendations.get('communication_tone', 'professional_standard') if persona_recommendations else 'professional_standard',
                "priority_concerns": persona_recommendations.get('priority_concerns', []) if persona_recommendations else []
            })

        ai_response = get_potensdot_answer_with_fallback(
            user_message=req.message,
            model_name=req.model,
            rag_results=rag_results,
            emotion_data=emotion_result,
            history=req.history or [],
            persona_info=enhanced_persona_info,
            search_metadata={"search_strategy": search_strategy, "persona_id": persona_info.get('ID') if persona_info else None, "original_query": req.message, "search_query": search_query}
        )
        logger.info("AI 응답 생성 완료")
    except Exception as e:
        logger.error(f"AI 응답 생성 실패: {str(e)}")
        # AI 응답 생성 실패 시 폴백 응답
        ai_response = _generate_fallback_response(req.message, emotion_result)
    
    # 6. 추천 FAQ 생성
    recommended_faqs = []
    if rag_results:
        recommended_faqs = [
            {
                "question": result.get("question", ""),
                "score": result.get("score", 0.0),
                "category": result.get("category", "일반")
            }
            for result in rag_results[:3]
            if result.get("score", 0) > 0.3
        ]
    
    # 7. 에스컬레이션 체크 (자동 종료 비활성화)
    escalation_needed = False  # 자동 에스컬레이션 완전 비활성화
    
    # 8. 세션 종료 조건 체크 (자동 종료 비활성화)
    session_ended = False  # 자동 세션 종료 완전 비활성화
    
    # 10. 응답 구성
    processing_time = time.time() - start_time
    
    response = ChatResponse(
        answer=ai_response,
        entities=entities,
        emotion=emotion_result,
        escalation_needed=escalation_needed,
        recommended_faqs=recommended_faqs,
        conversation_flow={
            "stage": _determine_conversation_stage(req.message, req.history),
            "next_actions": _suggest_next_actions(entities, emotion_result)
        },
        # 감정 격화 관련 정보 추가
        escalation_analysis={},
        intervention_type="none",
        requires_human_support=False,
        search_strategy=search_strategy,
        processing_time=processing_time,
        session_ended=session_ended
    )
    
    logger.info(f"채팅 응답 완료: 처리시간={processing_time:.3f}초")
    
    # DB 저장 로직 (실패해도 서비스 영향 X)
    try:
        # 1. 세션 생성/업데이트
        session_obj = session_repository.get_by_session_id(db, session_id=req.session_id)
        if not session_obj:
            # 신규 세션 생성
            session_obj = session_repository.create(db, obj_in={
                "session_id": req.session_id,
                "model_name": req.model,
                "status": "active",
                "start_time": time.time(),
                "total_messages": 1
            })
        else:
            # 메시지 수 증가
            session_obj.total_messages = (session_obj.total_messages or 0) + 1
            db.commit()
        # 2. 사용자 메시지 저장
        message_repository.create(db, obj_in={
            "session_id": req.session_id,
            "role": "user",
            "content": req.message,
            "model_used": req.model,
            "emotion_data": None,
            "processing_time": None,
            "rag_results": None,
            "search_strategy": None
        })
        # 3. AI 응답 메시지 저장
        message_repository.create(db, obj_in={
            "session_id": req.session_id,
            "role": "bot",
            "content": ai_response,
            "model_used": req.model,
            "emotion_data": json.dumps(emotion_result) if emotion_result else None,
            "processing_time": processing_time,
            "rag_results": json.dumps(rag_results) if rag_results else None,
            "search_strategy": search_strategy,
            "escalation_needed": escalation_needed,
            "session_ended": session_ended
        })
    except Exception as e:
        logger.warning(f"DB 저장 실패: {str(e)}")
    
    return response


@router.post("/end-session")
def end_session():
    """채팅 세션 종료"""
    try:
        # 실제 구현에서는 세션 정리 로직 추가
        return {
            "success": True,
            "message": "채팅 세션이 종료되었습니다. 이용해주셔서 감사합니다! 😊",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"세션 종료 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 종료 중 오류가 발생했습니다.")


@router.post("/submit-rating")
def submit_rating(request: RatingSubmitRequest):
    """채팅 평점 제출"""
    try:
        # 평점 유효성 검증
        if not 1 <= request.rating <= 5:
            raise HTTPException(status_code=400, detail="평점은 1-5 사이의 값이어야 합니다.")
        
        if len(request.feedback) > 500:
            raise HTTPException(status_code=400, detail="피드백은 500자를 초과할 수 없습니다.")
        
        # 평점 저장 로직 (실제 구현에서는 데이터베이스에 저장)
        rating_data = {
            "session_id": request.session_id,
            "rating": request.rating,
            "feedback": request.feedback,
            "timestamp": request.timestamp,
            "processed_at": time.time()
        }
        
        logger.info(f"평점 제출: 세션={request.session_id}, 평점={request.rating}")
        
        # 평점에 따른 응답 메시지
        if request.rating >= 4:
            message = "소중한 평가를 해주셔서 감사합니다! 😊 앞으로도 더 나은 서비스로 보답하겠습니다."
        elif request.rating >= 3:
            message = "평가해주셔서 감사합니다. 더 나은 서비스를 위해 노력하겠습니다. 💪"
        else:
            message = "아쉬운 평가를 주신 점 죄송합니다. 서비스 개선을 위해 더욱 노력하겠습니다. 🙏"
        
        return {
            "success": True,
            "message": message,
            "rating_saved": rating_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"평점 제출 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="평점 제출 중 오류가 발생했습니다.")


def _generate_fallback_response(message: str, emotion: Dict) -> str:
    """폴백 응답 생성"""
    emotion_type = emotion.get("emotion", "중립") if emotion else "중립"
    
    fallback_responses = {
        "불만": "불편을 끼쳐드려 죄송합니다. 전문 상담원과 연결해드릴까요? 📞",
        "분노": "화가 나셨을 상황을 이해합니다. 즉시 해결방안을 찾아보겠습니다. 😔",
        "불안": "걱정이 많으시군요. 차근차근 도움을 드리겠습니다. 안심하세요. 🤝",
        "슬픔": "마음이 무거우시군요. 따뜻하게 도와드리겠습니다. 💙",
        "기쁨": "기분이 좋으시네요! 더 도움이 되는 정보를 알려드릴게요. 😊",
        "중립": "질문을 좀 더 구체적으로 말씀해주시면 더 정확한 안내를 드릴 수 있어요. 🙂"
    }
    
    base_response = fallback_responses.get(emotion_type, fallback_responses["중립"])
    return f"{base_response}\n\n죄송하지만 일시적인 시스템 문제로 정확한 답변을 드리기 어렵습니다. 잠시 후 다시 시도해주세요."


def _check_escalation_needed(emotion: Dict, entities: Dict, message: str) -> bool:
    """에스컬레이션 필요성 판단"""
    if not emotion:
        return False
    
    # 강한 부정 감정
    if emotion.get("emotion") in ["분노", "불만"] and emotion.get("confidence", 0) > 0.7:
        return True
    
    # 복잡한 보험 용어나 클레임 관련
    escalation_keywords = ["소송", "법적", "피해보상", "불만", "항의", "취소", "환불", "담당자"]
    if any(keyword in message for keyword in escalation_keywords):
        return True
    
    return False


def _check_session_end_conditions(message: str, emotion: Dict) -> bool:
    """세션 종료 조건 체크"""
    end_keywords = ["종료", "끝", "그만", "안녕", "감사", "괜찮", "해결"]
    if any(keyword in message for keyword in end_keywords):
        return True
    
    # 만족도가 높고 감사 표현이 있는 경우
    if emotion and emotion.get("emotion") in ["기쁨", "만족"] and "감사" in message:
        return True
    
    return False


def _determine_conversation_stage(message: str, history: List) -> str:
    """대화 단계 판단"""
    if not history:
        return "greeting"
    
    if len(history) < 3:
        return "information_gathering"
    elif len(history) < 8:
        return "consultation"
    else:
        return "conclusion"


def _suggest_next_actions(entities: Dict, emotion: Dict) -> List[str]:
    """다음 액션 제안"""
    actions = []
    
    if entities and "보험상품" in entities:
        actions.append("상품 상세 정보 조회")
        actions.append("보험료 계산")
    
    if emotion and emotion.get("emotion") == "불안":
        actions.append("전문 상담원 연결")
    
    if not actions:
        actions = ["FAQ 확인", "추가 질문"]
    
    return actions 