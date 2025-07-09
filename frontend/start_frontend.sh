#!/bin/bash

# 현대해상 AI 챗봇 프론트엔드 개발 서버 시작 스크립트
# 작성자: AI Assistant
# 용도: 로컬 개발 환경에서 프론트엔드 서버 실행

set -e

echo "🎨 현대해상 AI 챗봇 프론트엔드 서버 시작 중..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 스크립트가 실행되는 디렉토리로 이동
cd "$(dirname "$0")"

# 1. Node.js 및 npm 확인
echo "📦 Node.js 환경 확인 중..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js가 설치되지 않았습니다.${NC}"
    echo "Node.js를 설치하세요: https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm이 설치되지 않았습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node --version) 확인${NC}"
echo -e "${GREEN}✅ npm $(npm --version) 확인${NC}"

# 2. package.json 확인
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json 파일을 찾을 수 없습니다${NC}"
    exit 1
fi

# 3. 의존성 설치
echo "📚 의존성 패키지 설치 중..."
if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
    echo "npm 패키지 설치 중..."
    npm install
    echo -e "${GREEN}✅ 패키지 설치 완료${NC}"
else
    echo "npm 패키지 업데이트 확인 중..."
    npm ci
    echo -e "${GREEN}✅ 패키지 업데이트 완료${NC}"
fi

# 4. 환경 확인
echo "🔧 개발 환경 설정 확인 중..."

# 백엔드 서버 상태 확인
echo "🔍 백엔드 서버 연결 상태 확인 중..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 백엔드 서버가 실행 중입니다 (http://localhost:8000)${NC}"
else
    echo -e "${YELLOW}⚠️ 백엔드 서버가 실행되지 않았습니다${NC}"
    echo -e "${YELLOW}   백엔드 서버를 먼저 시작하세요: ./backend/start_server.sh${NC}"
    echo -e "${BLUE}   계속 진행하겠습니다...${NC}"
fi

# 5. 개발 서버 시작
echo "🌐 Vite 개발 서버 시작 중..."
echo ""
echo -e "${GREEN}프론트엔드 URL: http://localhost:5173${NC}"
echo -e "${GREEN}백엔드 API: http://localhost:8000${NC}"
echo -e "${YELLOW}서버를 중지하려면 Ctrl+C를 누르세요${NC}"
echo ""

# Vite 개발 서버 실행
npm run dev 