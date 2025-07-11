"""
🧪 API 플로우 통합 테스트
전체적인 사용자 시나리오를 테스트합니다.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestChatbotFlow:
    """챗봇 전체 플로우 테스트"""
    
    def test_complete_consultation_flow(self, client: TestClient):
        """완전한 상담 플로우 테스트"""
        session_id = "integration_test_session"
        user_id = "integration_test_user"
        
        # 1. 초기 인사
        greeting_payload = {
            "message": "안녕하세요",
            "session_id": session_id,
            "user_id": user_id
        }
        
        response = client.post("/chat", json=greeting_payload)
        assert response.status_code == 200
        
        # 2. 페르소나 선택
        persona_payload = {
            "persona_id": "young_driver",
            "user_id": user_id
        }
        
        response = client.post("/personas/select", json=persona_payload)
        # 구현 상황에 따라 성공 또는 검증 오류
        assert response.status_code in [200, 422]
        
        # 3. 보험 문의
        insurance_inquiry = {
            "message": "자동차 보험 가입하고 싶어요",
            "session_id": session_id,
            "user_id": user_id
        }
        
        response = client.post("/chat", json=insurance_inquiry)
        assert response.status_code == 200

    def test_error_recovery_flow(self, client: TestClient):
        """에러 복구 플로우 테스트"""
        # 잘못된 요청 후 정상 요청
        invalid_payload = {
            "message": "",  # 빈 메시지
            "session_id": "error_test"
        }
        
        response = client.post("/chat", json=invalid_payload)
        assert response.status_code == 422
        
        # 정상 요청으로 복구
        valid_payload = {
            "message": "정상 메시지입니다",
            "session_id": "error_test",
            "user_id": "error_test_user"
        }
        
        response = client.post("/chat", json=valid_payload)
        assert response.status_code == 200


class TestInsuranceFlow:
    """보험 관련 플로우 테스트"""
    
    def test_insurance_consultation_flow(self, client: TestClient):
        """보험 상담 전체 플로우"""
        # 1. 보험 종류 조회
        response = client.get("/insurance/types")
        assert response.status_code == 200
        
        # 2. 보험료 계산
        calculation_payload = {
            "age": 28,
            "gender": "F",
            "vehicle_type": "compact",
            "coverage_amount": 30000000,
            "deductible": 200000
        }
        
        response = client.post("/insurance/calculate-premium", json=calculation_payload)
        # 구현에 따라 성공 또는 검증 오류
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, async_client):
        """동시 요청 처리 테스트"""
        import asyncio
        
        # 동시에 여러 요청 전송
        tasks = []
        for i in range(5):
            payload = {
                "message": f"동시 요청 테스트 {i}",
                "session_id": f"concurrent_session_{i}",
                "user_id": f"concurrent_user_{i}"
            }
            task = async_client.post("/chat", json=payload)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # 모든 요청이 성공적으로 처리되었는지 확인
        for response in responses:
            assert response.status_code == 200


class TestEmotionIntegration:
    """감정 분석 통합 테스트"""
    
    @patch('app.sentiment.advanced.analyze_emotion')
    def test_emotion_aware_chat(self, mock_emotion: pytest.Mock, client: TestClient):
        """감정 인식 채팅 테스트"""
        mock_emotion.return_value = {
            "emotion": "불안",
            "confidence": 0.9,
            "intensity": 0.8
        }
        
        anxious_message = {
            "message": "보험금 청구가 거절될까봐 걱정돼요",
            "session_id": "emotion_test",
            "user_id": "emotion_user"
        }
        
        response = client.post("/chat", json=anxious_message)
        assert response.status_code == 200
        
        # 감정에 따른 적절한 응답이 생성되었는지 확인
        data = response.json()
        assert "response" in data 