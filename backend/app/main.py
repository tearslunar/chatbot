from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from fastapi.responses import JSONResponse
from backend.app.sentiment.advanced import emotion_analyzer, emotion_router
from backend.app.utils.chat import get_potensdot_answer, extract_insurance_entities, llm_router
from backend.app.utils.emotion_response import emotion_response
from mangum import Mangum
from backend.app.rag.faq_rag import search_faqs
import httpx
import time

app = FastAPI()
app.include_router(emotion_router)
app.include_router(llm_router)

# CORS 설정 (프론트엔드 도메인 명시)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chatbot-1-uz5m.onrender.com",  # 프론트엔드 Render 도메인
        "http://localhost:5173",                # 개발용(필요시)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    model: str = "claude-3.7-sonnet"
    history: list = None  # 대화 이력 추가

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

        INTERNAL_API_BASE = os.environ.get("INTERNAL_API_BASE", "http://localhost:8000")
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
            # FAQ 검색은 동기 처리
            t_faq_start = time.time()
            rag_faqs = search_faqs(user_msg, top_n=3)
            print(f"[속도] FAQ 추천: {time.time() - t_faq_start:.2f}초")
            print("rag_faqs:", rag_faqs)
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
            # 프롬프트 경량화: rag_faqs는 Top-1만, 감정 정보는 emotion/intensity만, history는 최근 2개만 전달
            llm_task = client.post(
                f"{INTERNAL_API_BASE}/llm-answer-async",
                json={
                    "user_message": user_msg,
                    "model_name": model_name,
                    "faq": rag_faqs[0]["faq"] if rag_faqs else {},
                    "emotion": {
                        "emotion": emotion_data.get("emotion"),
                        "intensity": emotion_data.get("intensity")
                    },
                    "history": history[-2:] if history else []
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
        # 추천 FAQ 리스트 구성
        recommended_faqs = [
            {
                'question': item['faq']['question'],
                'answer': item['faq']['content'],
                'score': round(item['score'], 3),
                'category': item['faq'].get('subject', ''),
                'tags': [item['faq'].get('subject', '')]
            }
            for item in rag_faqs
        ]
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

handler = Mangum(app)