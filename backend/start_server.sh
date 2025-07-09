#!/bin/bash

# 현대해상 AI 챗봇 백엔드 서버 시작 스크립트
# 작성자: AI Assistant
# 용도: 로컬 개발 환경에서 백엔드 서버 실행

set -e

echo "🚀 현대해상 AI 챗봇 백엔드 서버 시작 중..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 스크립트가 실행되는 디렉토리로 이동
cd "$(dirname "$0")"

# 1. 가상환경 확인 및 활성화
echo "📦 가상환경 확인 중..."
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 가상환경이 존재하지 않습니다. 새로 생성합니다...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"
fi

# 가상환경 활성화
source venv/bin/activate

# Python 인터프리터 확인
if ! python -c "import sys; print(sys.version)" > /dev/null 2>&1; then
    echo -e "${RED}❌ Python 인터프리터에 문제가 있습니다. 가상환경을 재생성합니다...${NC}"
    deactivate 2>/dev/null || true
    rm -rf venv
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✅ 가상환경 재생성 완료${NC}"
fi

echo -e "${GREEN}✅ 가상환경 활성화 완료${NC}"

# 2. 필요 패키지 설치
echo "📚 패키지 의존성 확인 중..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ 패키지 설치 완료${NC}"
else
    echo -e "${YELLOW}⚠️ requirements.txt 파일을 찾을 수 없습니다${NC}"
fi

# 3. 환경변수 파일 확인
echo "🔧 환경변수 설정 확인 중..."
if [ ! -f ".env" ]; then
    if [ -f "env.local.example" ]; then
        echo -e "${YELLOW}⚠️ .env 파일이 없습니다. env.local.example을 복사합니다...${NC}"
        cp env.local.example .env
        echo -e "${YELLOW}📝 .env 파일을 편집하여 실제 API 키를 설정하세요!${NC}"
    else
        echo -e "${RED}❌ 환경변수 예제 파일을 찾을 수 없습니다${NC}"
        exit 1
    fi
fi

# 4. 데이터 폴더 및 임베딩 파일 확인
echo "📊 데이터 파일 확인 중..."
TERMS_EMBEDDING="../data/terms_embeddings.pkl"
FAQ_EMBEDDING="../data/faq_embeddings.pkl"

if [ ! -f "$TERMS_EMBEDDING" ] || [ ! -f "$FAQ_EMBEDDING" ]; then
    echo -e "${YELLOW}⚠️ 임베딩 파일이 없습니다. 생성 중...${NC}"
    echo "약관 임베딩 생성 중... (시간이 좀 걸립니다)"
    python -m app.rag.terms_rag
    echo "FAQ 임베딩 생성 중..."
    python -m app.rag.faq_rag
    echo -e "${GREEN}✅ 임베딩 파일 생성 완료${NC}"
else
    echo -e "${GREEN}✅ 임베딩 파일 확인 완료${NC}"
fi

# 5. 서버 시작
echo "🌐 FastAPI 서버 시작 중..."
echo -e "${GREEN}서버 URL: http://localhost:8000${NC}"
echo -e "${GREEN}API 문서: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}서버를 중지하려면 Ctrl+C를 누르세요${NC}"
echo ""

# 개발 모드로 서버 시작 (단일 워커)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 