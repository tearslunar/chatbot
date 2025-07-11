"""
Hi-Care AI 챗봇 메인 애플리케이션
모듈화된 라우터와 미들웨어를 사용하는 깔끔한 FastAPI 앱
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mangum import Mangum
import logging
import sys
import os

# 로컬 모듈 import
from .config.settings import settings
from .middleware.security import setup_middleware
from .routers import chat, persona, insurance
from .sentiment.advanced import emotion_router
from .utils.chat import llm_router

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        *(logging.FileHandler(settings.log_file) if settings.log_file else [])
    ]
)

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    description="AI 기반 보험 상담 챗봇 시스템",
    version=settings.version,
    debug=settings.debug,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None
)

# 미들웨어 설정
setup_middleware(app)

# 라우터 등록
app.include_router(chat.router)
app.include_router(persona.router)
app.include_router(insurance.router)
app.include_router(emotion_router)
app.include_router(llm_router)

# AWS Lambda 핸들러 (서버리스 배포용)
handler = Mangum(app)


@app.get("/")
def read_root():
    """루트 엔드포인트"""
    return {
        "service": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "status": "healthy",
        "message": "Hi-Care AI 챗봇 서비스가 정상 동작 중입니다. 😊"
    }


@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "debug": settings.debug,
        "timestamp": __import__('time').time()
    }


@app.get("/emotion-summary")
def get_emotion_summary():
    """감정 분석 요약 정보"""
    return {
        "available_emotions": [
            "기쁨", "슬픔", "분노", "불안", "놀람", "혐오", "공포", "중립", "만족"
        ],
        "analysis_features": [
            "실시간 감정 분석",
            "감정 강도 측정",
            "감정 트렌드 추적",
            "맞춤형 응답 생성"
        ],
        "supported_languages": ["한국어"],
        "model_info": {
            "provider": "Potensdot",
            "accuracy": "95%+",
            "response_time": "< 100ms"
        }
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 에러 핸들러"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "요청하신 페이지를 찾을 수 없습니다.",
            "path": str(request.url.path),
            "suggestion": "API 문서를 확인해주세요: /docs"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """500 에러 핸들러"""
    logger.error(f"Internal server error: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "서버 내부 오류가 발생했습니다.",
            "support": "문제가 지속되면 고객센터(1588-1234)로 연락주세요."
        }
    )


@app.on_event("startup")
async def startup_event():
    """앱 시작 시 실행되는 이벤트"""
    logger.info(f"🚀 {settings.app_name} 시작됨")
    logger.info(f"   버전: {settings.version}")
    logger.info(f"   환경: {settings.environment}")
    logger.info(f"   디버그: {settings.debug}")
    logger.info(f"   포트: {settings.port}")
    
    # API 키 검증
    if not settings.validate_api_keys():
        logger.warning("⚠️ 일부 API 키가 설정되지 않았습니다.")
    else:
        logger.info("✅ 모든 API 키가 정상적으로 설정되었습니다.")


@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 실행되는 이벤트"""
    logger.info(f"🛑 {settings.app_name} 종료됨")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.is_development,
        log_level=settings.log_level.lower()
    ) 