# 현대해상 AI 챗봇 프론트엔드 Dockerfile
FROM node:20-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치를 위한 파일 복사
COPY package*.json ./

# 의존성 설치
RUN npm install

# 소스 코드 복사
COPY . .

# 프로덕션 빌드
RUN npm run build

# 서빙 도구 설치
RUN npm install -g serve

# 포트 노출
EXPOSE 3000

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# 정적 파일 서빙
CMD ["serve", "-s", "dist", "-l", "3000"] 