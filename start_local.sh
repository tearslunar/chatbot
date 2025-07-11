#!/bin/bash

# Hi-Care AI 챗봇 로컬 개발 환경 시작 스크립트
# 작성자: AI Assistant
# 용도: 백엔드와 프론트엔드를 동시에 또는 개별적으로 실행

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 로고 출력
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  🚀 Hi-Care AI 챗봇                        ║"
echo "║                   로컬 개발 환경 시작                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 사용법 함수
show_usage() {
    echo -e "${YELLOW}사용법:${NC}"
    echo "  $0 [옵션]"
    echo ""
    echo -e "${YELLOW}옵션:${NC}"
    echo -e "  ${GREEN}all${NC}        - 백엔드와 프론트엔드 모두 시작 (기본값)"
    echo -e "  ${GREEN}backend${NC}    - 백엔드만 시작"
    echo -e "  ${GREEN}frontend${NC}   - 프론트엔드만 시작"
    echo -e "  ${GREEN}help${NC}       - 이 도움말 표시"
    echo ""
    echo -e "${YELLOW}예시:${NC}"
    echo "  $0              # 전체 시작"
    echo "  $0 all          # 전체 시작"
    echo "  $0 backend      # 백엔드만 시작"
    echo "  $0 frontend     # 프론트엔드만 시작"
    echo ""
}

# 시스템 요구사항 확인
check_requirements() {
    echo -e "${BLUE}📋 시스템 요구사항 확인 중...${NC}"
    
    # Python 확인
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✅ Python $(python3 --version) 설치됨${NC}"
    else
        echo -e "${RED}❌ Python 3이 설치되지 않았습니다${NC}"
        exit 1
    fi
    
    # Node.js 확인
    if command -v node &> /dev/null; then
        echo -e "${GREEN}✅ Node.js $(node --version) 설치됨${NC}"
    else
        echo -e "${RED}❌ Node.js가 설치되지 않았습니다${NC}"
        echo "Node.js를 설치하세요: https://nodejs.org/"
        exit 1
    fi
    
    echo ""
}

# 백엔드 시작 함수
start_backend() {
    echo -e "${PURPLE}🔧 백엔드 서버 시작 중...${NC}"
    if [ -f "backend/start_server.sh" ]; then
        cd backend
        ./start_server.sh
    else
        echo -e "${RED}❌ backend/start_server.sh 파일을 찾을 수 없습니다${NC}"
        exit 1
    fi
}

# 프론트엔드 시작 함수
start_frontend() {
    echo -e "${PURPLE}🎨 프론트엔드 서버 시작 중...${NC}"
    if [ -f "frontend/start_frontend.sh" ]; then
        cd frontend
        ./start_frontend.sh
    else
        echo -e "${RED}❌ frontend/start_frontend.sh 파일을 찾을 수 없습니다${NC}"
        exit 1
    fi
}

# 백그라운드에서 백엔드 시작
start_backend_background() {
    echo -e "${PURPLE}🔧 백엔드 서버를 백그라운드에서 시작 중...${NC}"
    (
        cd backend
        ./start_server.sh > ../backend.log 2>&1 &
        echo $! > ../backend.pid
    )
    
    # 백엔드 서버가 시작될 때까지 대기
    echo "백엔드 서버 시작 대기 중..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 백엔드 서버가 시작되었습니다 (http://localhost:8000)${NC}"
            break
        fi
        sleep 2
        echo -n "."
    done
    echo ""
}

# 정리 함수
cleanup() {
    echo -e "\n${YELLOW}🧹 정리 중...${NC}"
    if [ -f "backend.pid" ]; then
        PID=$(cat backend.pid)
        if kill -0 $PID 2>/dev/null; then
            echo "백엔드 서버 종료 중..."
            kill $PID
        fi
        rm -f backend.pid
    fi
    rm -f backend.log
    exit 0
}

# 종료 시그널 처리
trap cleanup SIGINT SIGTERM

# 메인 로직
MODE="${1:-all}"

case $MODE in
    "help"|"-h"|"--help")
        show_usage
        exit 0
        ;;
    "backend")
        check_requirements
        start_backend
        ;;
    "frontend")
        check_requirements
        start_frontend
        ;;
    "all"|"")
        check_requirements
        echo -e "${CYAN}🚀 백엔드와 프론트엔드를 모두 시작합니다...${NC}"
        echo ""
        
        # 백엔드를 백그라운드에서 시작
        start_backend_background
        
        # 잠시 대기
        sleep 3
        
        # 프론트엔드 시작 (포그라운드)
        echo -e "${CYAN}🎨 프론트엔드 서버를 시작합니다...${NC}"
        start_frontend
        ;;
    *)
        echo -e "${RED}❌ 알 수 없는 옵션: $MODE${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac 