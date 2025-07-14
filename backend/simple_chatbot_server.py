#!/usr/bin/env python3
"""
간단한 챗봇 테스트 서버
핵심 의존성만 사용하여 챗봇 기능 테스트
"""

import sys
import os
sys.path.insert(0, '/data/chatbot/backend')

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List
import uvicorn
import time

# 간단한 챗봇 앱 생성
app = FastAPI(title="Simple Chatbot Server")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청/응답 모델
class ChatRequest(BaseModel):
    message: str
    model: str = "test-model"
    history: list = []
    session_id: str = "test-session"

class ChatResponse(BaseModel):
    answer: str
    emotion: dict = {}
    escalation_needed: bool = False
    recommended_faqs: list = []
    processing_time: float = 0.0

# 간단한 챗봇 로직
class SimpleChatbot:
    def __init__(self):
        self.responses = {
            "안녕": "안녕하세요! 현대해상 햇살봇입니다 😊 무엇을 도와드릴까요?",
            "자동차보험": """네, 자동차보험 상담을 도와드리겠습니다! 🚗

**기본 보장**:
• 대인배상: 무제한 권장
• 대물배상: 2억원 이상
• 자기신체사고: 1.5억원
• 자기차량손해: 차량가액 기준

더 자세한 상담이 필요하시면 말씀해 주세요! ☀️""",
            "보험료": """보험료는 다음 요인들에 따라 결정됩니다:

**주요 요인**:
• 운전자 연령과 경력
• 차량 종류와 연식  
• 보장 범위와 자기부담금
• 각종 할인 특약

정확한 견적을 위해 차량 정보를 알려주세요! 💰""",
            "사고": """사고 발생 시 즉시 다음 절차를 따라주세요:

**긴급 대응**:
1. 안전 확보 후 119 신고
2. 현대해상 사고접수: 1588-5656
3. 사고 현장 사진 촬영
4. 상대방 정보 확인

24시간 사고접수 서비스로 신속하게 도와드립니다! 🚨""",
            "감사": "도움이 되었다니 기쁩니다! 😊 언제든 궁금한 점이 있으시면 찾아주세요. 안전한 하루 되세요! ☀️"
        }
    
    def get_response(self, message: str) -> str:
        """간단한 키워드 기반 응답 생성"""
        message_lower = message.lower()
        
        for keyword, response in self.responses.items():
            if keyword in message_lower:
                return response
        
        # 기본 응답
        return """죄송해요, 좀 더 구체적으로 말씀해 주시면 더 정확한 답변을 드릴 수 있어요! 😊

**문의 가능한 주제**:
• 자동차보험 가입 및 상담
• 보험료 견적 문의
• 사고 처리 절차
• 기타 보험 관련 질문

무엇을 도와드릴까요?"""

# 챗봇 인스턴스 생성
chatbot = SimpleChatbot()

@app.get("/")
def read_root():
    return {"message": "Simple Chatbot Server is running", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    start_time = time.time()
    
    print(f"[Chat] 받은 메시지: {req.message}")
    
    # 간단한 응답 생성
    response = chatbot.get_response(req.message)
    
    # 간단한 감정 분석 (키워드 기반)
    emotion = {"emotion": "중립", "intensity": 3}
    if any(word in req.message.lower() for word in ["화", "짜증", "분노"]):
        emotion = {"emotion": "분노", "intensity": 4}
    elif any(word in req.message.lower() for word in ["좋", "감사", "만족"]):
        emotion = {"emotion": "긍정", "intensity": 4}
    elif any(word in req.message.lower() for word in ["걱정", "불안", "무서"]):
        emotion = {"emotion": "불안", "intensity": 4}
    
    processing_time = time.time() - start_time
    
    print(f"[Chat] 응답 생성 완료: {processing_time:.3f}초")
    
    return ChatResponse(
        answer=response,
        emotion=emotion,
        escalation_needed=False,
        recommended_faqs=[],
        processing_time=round(processing_time, 3)
    )

@app.post("/test-chat")
def test_chat(data: dict):
    """간단한 테스트 엔드포인트"""
    return {
        "message": "테스트 성공! 챗봇 서버가 정상 작동합니다.",
        "received": data,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    print("🚀 간단한 챗봇 테스트 서버 시작...")
    print("📍 서버 주소: http://localhost:8890")
    print("🔧 핵심 챗봇 기능만 제공됩니다")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8890,
        log_level="info"
    ) 