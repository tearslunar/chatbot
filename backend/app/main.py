from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from fastapi.responses import JSONResponse
from backend.app.sentiment.advanced import emotion_analyzer
from backend.app.utils.chat import get_potensdot_answer, extract_insurance_entities
from backend.app.utils.emotion_response import emotion_response
from mangum import Mangum
from backend.app.rag.faq_rag import search_faqs

app = FastAPI()

# CORS 설정 (프론트엔드 로컬 개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    model: str = "claude-3.7-sonnet"

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
def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    model_name = req.model or "claude-3.7-sonnet"
    
    print(f"[로그] 사용자 메시지: {user_msg}")
    # 감정 분석: 사용자 메시지에만 적용
    emotion_data = emotion_analyzer.analyze_emotion(user_msg)
    print(f"[로그] 감정 분석 결과: {emotion_data}")
    emotion_trend = emotion_analyzer.get_emotion_trend()
    print(f"[로그] 감정 트렌드: {emotion_trend}")
    
    # RAG FAQ 검색 (Top-3)
    rag_faqs = search_faqs(user_msg, top_n=3)
    print(f"[로그] 추천 FAQ 개수: {len(rag_faqs)}")
    if rag_faqs:
        print(f"[로그] 추천 FAQ 샘플: {rag_faqs[0]}")
    
    # 기본 답변 생성 (감정 정보 포함)
    try:
        base_answer = get_potensdot_answer(user_msg, model_name, rag_faqs, emotion_data)
        print(f"[로그] LLM 답변 생성 완료")
    except Exception as e:
        print(f"[에러] LLM 답변 생성 중 예외 발생: {e}")
        base_answer = ""
    
    # 감정 기반 응답 강화 (챗봇 메시지에만 적용)
    enhanced_answer = emotion_response.get_emotion_enhanced_response(base_answer, emotion_data)
    print(f"[로그] 감정 기반 응답 강화 완료")
    
    # 상담사 연결 제안 추가
    escalation_suggestion = emotion_response.get_escalation_suggestion(emotion_data, emotion_trend)
    if escalation_suggestion:
        print(f"[로그] 상담사 연결 제안 추가됨")
        enhanced_answer += escalation_suggestion
    
    # 보험 엔티티 추출
    entities = extract_insurance_entities(user_msg)
    print(f"[로그] 보험 엔티티 추출 결과: {entities}")
    
    # 상담사 연결 필요 여부
    escalation_needed = emotion_analyzer.is_escalation_needed()
    print(f"[로그] 상담사 연결 필요 여부: {escalation_needed}")
    
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
    print(f"[로그] 추천 FAQ 리스트 구성 완료")
    
    return ChatResponse(
        answer=enhanced_answer, 
        entities=entities, 
        emotion=emotion_data,  # 사용자 메시지에 대한 감정만 반환
        escalation_needed=escalation_needed,
        recommended_faqs=recommended_faqs
    )

handler = Mangum(app)