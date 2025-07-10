#!/bin/bash

# 현대해상 AI 챗봇 백엔드 서버 시작 스크립트
# 사용법: ./start_server.sh

set -e

echo "======================================"
echo "현대해상 AI 챗봇 백엔드 서버 시작"
echo "======================================"

# 현재 디렉토리가 프로젝트 루트인지 확인
if [ ! -f "backend/app/main.py" ]; then
    echo "❌ 오류: 프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# 가상환경 존재 확인
if [ ! -d "backend/venv" ]; then
    echo "❌ 오류: 가상환경이 없습니다. 다음 명령으로 생성하세요:"
    echo "cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 가상환경 Python 인터프리터 확인
if [ ! -f "backend/venv/bin/python" ]; then
    echo "❌ 오류: 가상환경이 손상되었습니다. 다시 생성하세요:"
    echo "cd backend && rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

echo "✅ 가상환경 확인 완료"

# 가상환경 활성화 및 서버 시작
echo "🚀 서버 시작 중..."
source backend/venv/bin/activate
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

echo "서버가 http://localhost:8000 에서 실행 중입니다."
echo "종료하려면 Ctrl+C를 누르세요." 