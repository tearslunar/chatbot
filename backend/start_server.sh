#!/bin/bash

# Hi-Care AI 챗봇 백엔드 서버 시작 스크립트
# 작성자: AI Assistant
# 용도: 로컬 개발 환경에서 백엔드 서버 실행

set -e

echo "🚀 Hi-Care AI 챗봇 백엔드 서버 시작 중..."

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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "📦 패키지 설치 중... ($REQUIREMENTS_FILE)"
    pip install -r "$REQUIREMENTS_FILE"
    
    # 개발용 의존성도 설치 (선택사항)
    DEV_REQUIREMENTS="$SCRIPT_DIR/requirements-dev.txt"
    if [ -f "$DEV_REQUIREMENTS" ]; then
        echo "🛠️ 개발용 의존성 설치 중..."
        pip install -r "$DEV_REQUIREMENTS"
    fi
    
    echo -e "${GREEN}✅ 패키지 설치 완료${NC}"
    
    # 2-1. 핵심 의존성 검증
    echo "🔍 핵심 의존성 검증 중..."
    python -c "import faiss; print('✅ FAISS 로드 성공')" 2>/dev/null || {
        echo -e "${RED}❌ FAISS 모듈 로드 실패${NC}"
        echo -e "${YELLOW}💡 해결 방법: pip install faiss-cpu==1.7.4${NC}"
        exit 1
    }
    python -c "import torch; print('✅ PyTorch 로드 성공')" 2>/dev/null || {
        echo -e "${RED}❌ PyTorch 모듈 로드 실패${NC}"
        echo -e "${YELLOW}💡 해결 방법: pip install torch${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ 핵심 의존성 검증 완료${NC}"
else
    echo -e "${RED}❌ requirements.txt 파일을 찾을 수 없습니다${NC}"
    echo "   찾은 경로: $REQUIREMENTS_FILE"
    echo "   현재 디렉토리: $(pwd)"
    echo "   디렉토리 내용:"
    ls -la "$SCRIPT_DIR" | head -10
    exit 1
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
echo -e "${GREEN}서버 URL: http://localhost:8888${NC}"
echo -e "${GREEN}API 문서: http://localhost:8888/docs${NC}"
echo -e "${YELLOW}서버를 중지하려면 Ctrl+C를 누르세요${NC}"
echo ""

# 현재 디렉토리 확인 및 Python 경로 설정
echo "📁 현재 디렉토리: $(pwd)"
echo "🐍 Python 경로: $(which python)"

# 개발 모드로 서버 시작 (단일 워커)
# PYTHONPATH 설정으로 app 모듈 인식 보장
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload --workers 4 