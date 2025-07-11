#!/bin/bash

# Hi-Care AI 챗봇 - Firebase + Docker 빠른 배포 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Hi-Care AI 챗봇 배포 시작 ===${NC}"

# 1. 환경변수 체크
echo -e "${YELLOW}1. 환경변수 확인 중...${NC}"
if [ ! -f "frontend/.env.production" ]; then
    echo -e "${RED}frontend/.env.production 파일이 없습니다.${NC}"
    echo -e "${YELLOW}실제 서버 IP로 설정하세요.${NC}"
    exit 1
fi

# 2. 프론트엔드 빌드
echo -e "${YELLOW}2. 프론트엔드 빌드 중...${NC}"
cd frontend

# 의존성 설치
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}의존성 설치 중...${NC}"
    npm install
fi

# 프로덕션 빌드
echo -e "${BLUE}프로덕션 빌드 중...${NC}"
npm run build

# 3. Firebase 배포
echo -e "${YELLOW}3. Firebase 배포 중...${NC}"
if ! command -v firebase &> /dev/null; then
    echo -e "${RED}Firebase CLI가 설치되지 않았습니다.${NC}"
    echo -e "${BLUE}설치 중...${NC}"
    npm install -g firebase-tools
fi

# Firebase 배포
firebase deploy --only hosting

# 4. 배포 완료 메시지
echo -e "${GREEN}=== 배포 완료! ===${NC}"
echo -e "${BLUE}프론트엔드:${NC} Firebase Hosting URL 확인"
echo -e "${BLUE}백엔드:${NC} Docker 서버에서 실행 중"
echo ""
echo -e "${YELLOW}다음 단계:${NC}"
echo -e "1. .env.production에서 실제 서버 IP 확인"
echo -e "2. Docker 서버에서 백엔드 실행"
echo -e "3. CORS 설정 업데이트"
echo ""
echo -e "${GREEN}배포 성공! 🎉${NC}" 