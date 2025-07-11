"""
🧪 Pytest 설정 및 공통 픽스처
테스트 환경 설정과 재사용 가능한 테스트 데이터를 제공합니다.
"""

import pytest
import asyncio
import os
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient

# 테스트 환경 변수 설정
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app
from app.config.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """세션 스코프 이벤트 루프"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """동기 테스트 클라이언트"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """비동기 테스트 클라이언트"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
def sample_user_message():
    """샘플 사용자 메시지"""
    return {
        "message": "안녕하세요, 자동차 보험에 대해 알고 싶어요.",
        "session_id": "test_session_123",
        "user_id": "test_user_456"
    }


@pytest.fixture
def sample_persona():
    """샘플 페르소나 데이터"""
    return {
        "persona_id": "young_driver",
        "name": "젊은 운전자",
        "age_group": "20-30",
        "characteristics": ["신중함", "경제적", "디지털 네이티브"]
    }


@pytest.fixture
def sample_insurance_data():
    """샘플 보험 데이터"""
    return {
        "insurance_type": "auto",
        "coverage_amount": 50000000,
        "deductible": 200000,
        "premium": 120000,
        "term": "1년"
    }


@pytest.fixture
def mock_emotion_response():
    """모의 감정 분석 응답"""
    return {
        "emotion": "중립",
        "confidence": 0.85,
        "intensity": 0.6,
        "emotions_detected": {
            "중립": 0.85,
            "만족": 0.10,
            "호기심": 0.05
        }
    }


@pytest.fixture
def auth_headers():
    """인증 헤더"""
    return {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """각 테스트 전후에 실행되는 설정"""
    # 테스트 전 설정
    original_settings = settings.copy()
    settings.update({"testing": True})
    
    yield
    
    # 테스트 후 정리
    settings.update(original_settings) 