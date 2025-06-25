from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from app.sentiment.simple import is_negative_sentiment, is_negative_sentiment_llm
from app.utils.gemini import get_gemini_answer

load_dotenv()

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
    model: str = "gemini-1.0-pro"

class ChatResponse(BaseModel):
    answer: str

@app.get("/")
def read_root():
    return {"message": "Hyundai Chatbot API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    model_name = req.model or "gemini-1.0-pro"
    answer = get_gemini_answer(user_msg, model_name)
    # 프롬프트 기반 감성분석
    if is_negative_sentiment_llm(user_msg, model_name):
        answer += "\n\n(감지됨: 부정 감성) 상담사 연결이 필요하신가요? '상담사 연결' 버튼을 눌러주세요."
    return ChatResponse(answer=answer)

@app.get("/models")
def list_gemini_models():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return JSONResponse([])
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        result = []
        for m in models:
            # generateContent 지원 모델만 필터링
            if hasattr(m, "supported_generation_methods") and "generateContent" in m.supported_generation_methods:
                result.append({
                    "name": m.name,
                    "display_name": getattr(m, "display_name", m.name)
                })
        return result
    except Exception as e:
        return JSONResponse([{"name": "error", "display_name": str(e)}])
