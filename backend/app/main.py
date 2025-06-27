from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from fastapi.responses import JSONResponse
from backend.app.sentiment.simple import is_negative_sentiment_potensdot
from backend.app.utils.chat import get_potensdot_answer, extract_insurance_entities
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

@app.get("/")
def read_root():
    return {"message": "Hyundai Chatbot API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    model_name = req.model or "claude-3.7-sonnet"
    # RAG FAQ 검색 (Top-3)
    rag_faqs = search_faqs(user_msg, top_n=3)
    answer = get_potensdot_answer(user_msg, model_name, rag_faqs)
    # Potensdot 감성분석
    if is_negative_sentiment_potensdot(user_msg):
        answer += "\n\n(감지됨: 부정 감성) 상담사 연결이 필요하신가요? '상담사 연결' 버튼을 눌러주세요."
    # 보험 엔티티 추출
    entities = extract_insurance_entities(user_msg)
    return ChatResponse(answer=answer, entities=entities)

handler = Mangum(app)