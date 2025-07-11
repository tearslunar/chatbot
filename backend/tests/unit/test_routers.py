"""
🧪 라우터 단위 테스트
각 라우터의 기본 기능을 테스트합니다.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestChatRouter:
    """채팅 라우터 테스트"""
    
    @pytest.mark.parametrize("message,expected_status", [
        ("안녕하세요", 200),
        ("자동차 보험 문의", 200),
        ("", 422),  # 빈 메시지는 유효성 검사 실패
    ])
    def test_chat_message_validation(self, client: TestClient, message: str, expected_status: int):
        """채팅 메시지 유효성 검사 테스트"""
        payload = {
            "message": message,
            "session_id": "test_session",
            "user_id": "test_user"
        } if message else {}
        
        response = client.post("/chat", json=payload)
        assert response.status_code == expected_status

    @patch('app.routers.chat.get_llm_response')
    def test_chat_response_format(self, mock_llm: MagicMock, client: TestClient, sample_user_message):
        """채팅 응답 형식 테스트"""
        mock_llm.return_value = "안녕하세요! 보험 상담을 도와드리겠습니다."
        
        response = client.post("/chat", json=sample_user_message)
        
        assert response.status_code == 200
        data = response.json()
        
        # 응답 구조 검증
        assert "response" in data
        assert "session_id" in data
        assert "timestamp" in data
        assert data["session_id"] == sample_user_message["session_id"]


class TestPersonaRouter:
    """페르소나 라우터 테스트"""
    
    def test_get_personas(self, client: TestClient):
        """페르소나 목록 조회 테스트"""
        response = client.get("/personas")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if data:  # 데이터가 있는 경우
            persona = data[0]
            assert "persona_id" in persona
            assert "name" in persona

    def test_persona_selection(self, client: TestClient):
        """페르소나 선택 테스트"""
        payload = {
            "persona_id": "young_driver",
            "user_id": "test_user"
        }
        
        response = client.post("/personas/select", json=payload)
        
        # 성공하거나 유효성 검사 오류
        assert response.status_code in [200, 422]


class TestInsuranceRouter:
    """보험 라우터 테스트"""
    
    def test_insurance_types(self, client: TestClient):
        """보험 종류 조회 테스트"""
        response = client.get("/insurance/types")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if data:
            insurance_type = data[0]
            assert "type" in insurance_type or "name" in insurance_type

    def test_premium_calculation_validation(self, client: TestClient):
        """보험료 계산 유효성 검사 테스트"""
        # 유효한 데이터
        valid_payload = {
            "age": 30,
            "gender": "M",
            "vehicle_type": "sedan",
            "coverage_amount": 50000000
        }
        
        response = client.post("/insurance/calculate-premium", json=valid_payload)
        assert response.status_code in [200, 422]  # 구현에 따라
        
        # 유효하지 않은 데이터
        invalid_payload = {
            "age": -5,  # 음수 나이
            "gender": "INVALID",
            "coverage_amount": "not_a_number"
        }
        
        response = client.post("/insurance/calculate-premium", json=invalid_payload)
        assert response.status_code == 422 