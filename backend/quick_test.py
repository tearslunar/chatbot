#!/usr/bin/env python3
"""
Quick CORS header test - 빠른 헤더 테스트
"""
import sys
import os
sys.path.insert(0, '/data/chatbot')
os.chdir('/data/chatbot/backend')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import uvicorn

# 간단한 테스트 앱 생성
test_app = FastAPI(title="CORS Test Server")

# CORS 설정
test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 헤더 미들웨어
@test_app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    
    # 모든 필요한 헤더 추가
    response.headers["ngrok-skip-browser-warning"] = "true"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "3600"
    
    return response

@test_app.get("/")
def read_root():
    return {"message": "✅ CORS 헤더 테스트 서버", "status": "정상 동작"}

@test_app.get("/health")
def health():
    return {"status": "ok", "cors": "enabled", "ngrok": "bypassed"}

@test_app.post("/test-chat")
def test_chat(data: dict):
    return {
        "message": "헤더가 올바르게 설정되었습니다!",
        "received": data,
        "cors_enabled": True,
        "ngrok_bypassed": True
    }

@test_app.options("/test-chat")
def test_chat_options():
    return {"message": "OPTIONS 요청 성공"}

if __name__ == "__main__":
    print("🚀 CORS 헤더 테스트 서버 시작...")
    print("📍 서버 주소: http://localhost:8890")
    print("🔧 모든 CORS 헤더가 활성화됩니다")
    print("🌐 ngrok-skip-browser-warning 헤더 포함")
    
    uvicorn.run(
        test_app,
        host="0.0.0.0",
        port=8890,
        log_level="info"
    ) 