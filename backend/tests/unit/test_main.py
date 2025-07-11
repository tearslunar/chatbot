"""
🧪 메인 애플리케이션 단위 테스트
기본 엔드포인트와 앱 설정을 테스트합니다.
"""

import pytest
from fastapi.testclient import TestClient


class TestMainApp:
    """메인 앱 테스트 클래스"""

    def test_root_endpoint(self, client: TestClient):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert "version" in data
        assert "environment" in data
        assert "status" in data
        assert data["status"] == "healthy"
        assert "Hi-Care" in data["service"]

    def test_health_check(self, client: TestClient):
        """헬스 체크 엔드포인트 테스트"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "environment" in data
        assert "timestamp" in data
        assert isinstance(data["timestamp"], float)

    def test_emotion_summary(self, client: TestClient):
        """감정 분석 요약 엔드포인트 테스트"""
        response = client.get("/emotion-summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "available_emotions" in data
        assert "analysis_features" in data
        assert "supported_languages" in data
        assert "model_info" in data
        
        # 기본 감정들이 포함되어 있는지 확인
        emotions = data["available_emotions"]
        expected_emotions = ["기쁨", "슬픔", "분노", "불안", "중립"]
        for emotion in expected_emotions:
            assert emotion in emotions

    def test_404_handler(self, client: TestClient):
        """404 에러 핸들러 테스트"""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        
        assert "error" in data
        assert "message" in data
        assert "path" in data
        assert "suggestion" in data
        assert data["error"] == "Not Found"

    def test_app_metadata(self, client: TestClient):
        """앱 메타데이터 검증"""
        # OpenAPI 스키마 확인
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "info" in schema
        assert "title" in schema["info"]
        assert "version" in schema["info"] 