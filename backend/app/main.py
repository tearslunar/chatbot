from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from fastapi.responses import JSONResponse
from backend.app.sentiment.advanced import emotion_analyzer, emotion_router
from backend.app.utils.chat import get_potensdot_answer, extract_insurance_entities, llm_router
from backend.app.utils.emotion_response import emotion_response
from mangum import Mangum
from backend.app.rag.faq_rag import search_faqs
from backend.app.rag.hybrid_rag import search_hybrid
import httpx
import time
import random
from backend.app.utils.persona_utils import persona_manager
from typing import Dict

app = FastAPI()
app.include_router(emotion_router)
app.include_router(llm_router)

# CORS 설정 (환경변수로 관리)
allowed_origins_str = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# 임시 하드코딩 (환경변수 문제 해결용)
if not allowed_origins or len(allowed_origins) == 1 and allowed_origins[0] == "http://localhost:5173":
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://new-hyundai-chatbot.web.app",
        "https://new-hyundai-chatbot.firebaseapp.com",
        "https://218457e5970e.ngrok-free.app"
    ]
    print(f"[DEBUG] Using hardcoded CORS origins: {allowed_origins}")
else:
    print(f"[DEBUG] Using env CORS origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 세션별 페르소나 매핑 (간단 구현, 실제 서비스는 인증/세션 연동 필요)
session_persona_map: Dict[str, dict] = {}

class PersonaSetRequest(BaseModel):
    session_id: str
    persona_id: str

@app.post("/set-persona")
def set_persona(request: PersonaSetRequest):
    """세션별 페르소나 선택/적용 API"""
    persona = persona_manager.get_persona_by_id(request.persona_id)
    if not persona:
        return {"success": False, "error": "Persona not found"}
    session_persona_map[request.session_id] = persona
    return {"success": True, "persona": persona}

class PersonaGreetingRequest(BaseModel):
    session_id: str

@app.post("/get-persona-greeting")
def get_persona_greeting(request: PersonaGreetingRequest):
    """페르소나 기반 맞춤형 인사말 생성 API"""
    persona = session_persona_map.get(request.session_id)
    if not persona:
        return {"success": False, "error": "No persona found for session"}
    
    # 페르소나 정보 기반 맞춤형 인사말 생성
    greeting = generate_persona_greeting(persona)
    return {"success": True, "greeting": greeting}

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
    가입상품 = persona.get('현재 가입 상품 (현대해상)', '')
    
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
        greeting += "현대 차량을 이용하고 계시는군요! 현대해상과 더욱 잘 맞는 보장을 제공해드릴 수 있어요. 🚗\n"
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
        greeting += "안전에 대한 관심이 높으시군요. 완벽한 보장으로 안심하시도록 도와드릴게요! 🛡️\n"
    elif '긴급' in 핵심니즈:
        greeting += "긴급 상황에 대비하는 마음이 대단하시네요. 24시간 든든한 서비스를 제공해드릴게요! 🚨\n"
    
    greeting += "\n궁금한 점이 있으시면 언제든 편하게 말씀해 주세요. 햇살봇이 친절하게 도와드릴게요! 🌞"
    
    return greeting

@app.get("/get-persona")
def get_persona(session_id: str = Query(...)):
    """현재 세션의 페르소나 조회 API"""
    persona = session_persona_map.get(session_id)
    return {"persona": persona}

class ChatRequest(BaseModel):
    message: str
    model: str = "claude-3.7-sonnet"
    history: list = None  # 대화 이력 추가
    session_id: str = None  # 세션 ID 추가

class ChatResponse(BaseModel):
    answer: str
    entities: dict = None
    emotion: dict = None
    escalation_needed: bool = False
    recommended_faqs: list = None

@app.get("/")
def read_root():
    return {"message": "Hyundai Chatbot API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/emotion-summary")
def get_emotion_summary():
    """현재 세션의 감정 분석 요약"""
    return emotion_analyzer.get_emotion_summary()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        total_start = time.time()
        print("==== POST /chat 요청 도착 ====")
        user_msg = req.message
        print("user_msg:", user_msg)
        model_name = req.model or "claude-3.7-sonnet"
        print("model_name:", model_name)
        history = req.history or []
        print("history:", history)
        session_id = req.session_id or "default"
        print("session_id:", session_id)
        
        # 세션별 페르소나 정보 조회
        persona_info = session_persona_map.get(session_id)
        print("persona_info:", persona_info)

        INTERNAL_API_BASE = os.environ.get("INTERNAL_API_BASE", "http://localhost:8888")
        print("INTERNAL_API_BASE:", INTERNAL_API_BASE)

        async with httpx.AsyncClient() as client:
            print("httpx.AsyncClient 생성")
            # 감정 분석 비동기 호출
            t_emotion_start = time.time()
            emotion_task = client.post(
                f"{INTERNAL_API_BASE}/emotion-analyze-async",
                json={"text": user_msg}
            )
            print("emotion_task 생성")
            # 대화 흐름 인식 향상된 검색 (FAQ + 약관 + 컨텍스트)
            t_rag_start = time.time()
            from backend.app.rag.enhanced_hybrid_rag import search_with_conversation_context
            enhanced_search_result = search_with_conversation_context(
                history, user_msg, faq_top_n=3, terms_top_n=5, max_results=5
            )
            rag_results = enhanced_search_result["results"]
            search_metadata = enhanced_search_result["search_metadata"]
            print(f"[속도] 대화 흐름 인식 검색: {time.time() - t_rag_start:.2f}초")
            print(f"검색 전략: {search_metadata.get('search_strategy')}")
            print(f"대화 흐름: {search_metadata.get('conversation_flow')}")
            print("rag_results:", rag_results)
            # 감정 분석 결과 대기
            emotion_resp = await emotion_task
            print(f"[속도] 감정 분석: {time.time() - t_emotion_start:.2f}초")
            print("emotion_resp status:", emotion_resp.status_code)
            emotion_data = emotion_resp.json()
            print("emotion_data:", emotion_data)
            emotion_trend = emotion_analyzer.get_emotion_trend()
            print("emotion_trend:", emotion_trend)
            # LLM 호출 비동기
            t_llm_start = time.time()
            # 프롬프트 경량화: 대화 흐름 인식 검색 결과, 감정 정보는 emotion/intensity만, history는 최근 2개만 전달
            llm_task = client.post(
                f"{INTERNAL_API_BASE}/llm-answer-async",
                json={
                    "user_message": user_msg,
                    "model_name": model_name,
                    "rag_results": rag_results,  # 대화 흐름 인식 검색 결과 전달
                    "search_metadata": search_metadata,  # 검색 메타데이터 추가
                    "emotion_data": {
                        "emotion": emotion_data.get("emotion"),
                        "intensity": emotion_data.get("intensity")
                    },
                    "history": history[-2:] if history else [],
                    "persona_info": persona_info
                }
            )
            print("llm_task 생성")
            llm_resp = await llm_task
            print(f"[속도] LLM 답변 생성: {time.time() - t_llm_start:.2f}초")
            print("llm_resp status:", llm_resp.status_code)
            base_answer = llm_resp.json()["answer"]
            print("base_answer:", base_answer)
        # 감정 기반 응답 강화 (챗봇 메시지에만 적용)
        t_enhance_start = time.time()
        enhanced_answer = emotion_response.get_emotion_enhanced_response(base_answer, emotion_data)
        print(f"[속도] 감정 기반 응답 강화: {time.time() - t_enhance_start:.2f}초")
        print("enhanced_answer:", enhanced_answer)
        # 상담사 연결 제안 추가
        escalation_suggestion = emotion_response.get_escalation_suggestion(emotion_data, emotion_trend)
        if escalation_suggestion:
            print("상담사 연결 제안 추가됨")
            enhanced_answer += escalation_suggestion
        # 보험 엔티티 추출
        t_entity_start = time.time()
        entities = extract_insurance_entities(user_msg)
        print(f"[속도] 보험 엔티티 추출: {time.time() - t_entity_start:.2f}초")
        print("entities:", entities)
        # 상담사 연결 필요 여부
        escalation_needed = emotion_analyzer.is_escalation_needed()
        print("escalation_needed:", escalation_needed)
        # 추천 FAQ 리스트 구성 (FAQ 결과만 필터링)
        recommended_faqs = []
        for item in rag_results:
            if item.get('source_type') == 'faq':
                faq_data = item.get('faq', {})
                recommended_faqs.append({
                    'question': faq_data.get('question', ''),
                    'answer': faq_data.get('content', ''),
                    'score': round(item.get('weighted_score', 0), 3),
                    'category': faq_data.get('subject', ''),
                    'tags': [faq_data.get('subject', '')]
                })
        
        # FAQ가 부족하면 기존 FAQ 검색으로 보충
        if len(recommended_faqs) < 3:
            additional_faqs = search_faqs(user_msg, top_n=3)
            for item in additional_faqs:
                if len(recommended_faqs) >= 3:
                    break
                faq_data = item.get('faq', {})
                # 중복 제거
                if not any(existing['question'] == faq_data.get('question', '') for existing in recommended_faqs):
                    recommended_faqs.append({
                        'question': faq_data.get('question', ''),
                        'answer': faq_data.get('content', ''),
                        'score': round(item.get('score', 0), 3),
                        'category': faq_data.get('subject', ''),
                        'tags': [faq_data.get('subject', '')]
                    })
        print("recommended_faqs:", recommended_faqs)
        print(f"[속도] 전체 처리 시간: {time.time() - total_start:.2f}초")
        print("==== POST /chat 응답 완료 ====")
        return ChatResponse(
            answer=enhanced_answer, 
            entities=entities, 
            emotion=emotion_data,  # 사용자 메시지에 대한 감정만 반환
            escalation_needed=escalation_needed,
            recommended_faqs=recommended_faqs
        )
    except Exception as e:
        print("!!! /chat 처리 중 예외 발생:", e)
        import traceback; traceback.print_exc()
        raise

@app.post("/end-session")
def end_session():
    """
    상담 종료 시점에 부정적 감정 메시지 중 랜덤하게 1개를 선택, 추가 해소 분석을 수행하고 결과를 반환
    """
    negative_emotions = [e for e in emotion_analyzer.emotion_history if e.get('emotion') in ['부정', '불만', '분노', '불안', '슬픔']]
    selected = random.choice(negative_emotions) if negative_emotions else None
    # 해소 분석: intensity가 3 이하로 떨어졌거나, 마지막 감정이 긍정/중립/기쁨/놀람이면 해소로 간주
    resolved = False
    if selected:
        last_emotion = emotion_analyzer.emotion_history[-1] if emotion_analyzer.emotion_history else None
        if last_emotion and last_emotion.get('emotion') in ['긍정', '중립', '기쁨', '놀람']:
            resolved = True
        elif last_emotion and last_emotion.get('intensity', 3) <= 3:
            resolved = True
    return {
        "random_negative_emotion": selected,
        "resolved": resolved
    }

@app.get("/persona-list")
def persona_list(keyword: str = Query(None, description="검색 키워드"), limit: int = 100):
    """고객 페르소나 목록/검색 API"""
    return persona_manager.list_personas(keyword=keyword, limit=limit)

handler = Mangum(app)