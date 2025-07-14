"""
채팅 라우터
AI 챗봇과의 대화 처리, 감정 분석, RAG 검색 통합
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import time
import logging
import random

from ..sentiment.advanced import emotion_analyzer
from ..utils.chat import get_potensdot_answer_with_fallback, extract_insurance_entities
from ..utils.emotion_response import emotion_response
from ..rag.faq_rag import search_faqs
from ..rag.hybrid_rag import search_hybrid
from ..config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """채팅 요청"""
    message: str
    model: str = "claude-3.7-sonnet"
    history: Optional[List[Dict]] = None
    session_id: Optional[str] = None


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


class RatingSubmitRequest(BaseModel):
    """평점 제출 요청"""
    session_id: str
    rating: int
    feedback: str = ""
    timestamp: str


@router.post("/message", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """메인 채팅 엔드포인트"""
    start_time = time.time()
    
    try:
        logger.info(f"채팅 요청: 세션={req.session_id}, 메시지 길이={len(req.message)}")
        
        # 1. 기본 유효성 검사
        if not req.message or len(req.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="메시지가 비어있습니다.")
        
        if len(req.message) > 1000:
            raise HTTPException(status_code=400, detail="메시지가 너무 깁니다. (최대 1000자)")
        
        # 2. 감정 분석
        emotion_result = None
        try:
            emotion_result = emotion_analyzer.analyze_emotion(req.message)
            logger.info(f"감정 분석 완료: {emotion_result.get('emotion', 'unknown')}")
        except Exception as e:
            logger.warning(f"감정 분석 실패: {str(e)}")
            emotion_result = {"emotion": "중립", "confidence": 0.5}
        
        # 3. 보험 엔터티 추출
        entities = None
        try:
            entities = extract_insurance_entities(req.message)
            logger.info(f"엔터티 추출 완료: {len(entities) if entities else 0}개")
        except Exception as e:
            logger.warning(f"엔터티 추출 실패: {str(e)}")
            entities = {}
        
        # 4. RAG 검색 (하이브리드)
        rag_results = []
        search_strategy = "none"
        try:
            rag_results = search_hybrid(req.message, limit=settings.max_rag_results)
            search_strategy = "hybrid"
            logger.info(f"RAG 검색 완료: {len(rag_results)}개 결과")
        except Exception as e:
            logger.warning(f"RAG 검색 실패: {str(e)}")
            # 폴백: FAQ 검색만 시도
            try:
                rag_results = search_faqs(req.message, limit=3)
                search_strategy = "faq_only"
                logger.info(f"폴백 FAQ 검색 완료: {len(rag_results)}개 결과")
            except Exception as e2:
                logger.error(f"폴백 검색도 실패: {str(e2)}")
                rag_results = []
        
        # 5. 메인 AI 응답 생성
        try:
            ai_response = get_potensdot_answer_with_fallback(
                user_message=req.message,
                model_name=req.model,
                history=req.history or [],
                rag_results=rag_results,
                emotion_data=emotion_result,
                persona_info=entities
            )
            logger.info("AI 응답 생성 완료")
        except Exception as e:
            logger.error(f"AI 응답 생성 실패: {str(e)}")
            # 폴백 응답
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
        
        # 7. 에스컬레이션 필요성 판단
        escalation_needed = _check_escalation_needed(emotion_result, entities, req.message)
        
        # 8. 세션 종료 조건 체크
        session_ended = _check_session_end_conditions(req.message, emotion_result)
        
        # 9. 응답 구성
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
            search_strategy=search_strategy,
            processing_time=processing_time,
            session_ended=session_ended
        )
        
        logger.info(f"채팅 응답 완료: 처리시간={processing_time:.3f}초")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"채팅 처리 중 오류: {str(e)} (처리시간: {processing_time:.3f}초)")
        raise HTTPException(status_code=500, detail="채팅 처리 중 오류가 발생했습니다.")


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