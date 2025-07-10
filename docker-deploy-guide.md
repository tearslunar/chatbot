# Docker 환경에서 현대해상 AI 챗봇 배포 가이드

## 1. 사전 준비사항

### 필수 도구 설치
```bash
# Docker 및 Docker Compose 설치 확인
docker --version
docker-compose --version

# Git 설치 확인
git --version
```

### 환경 요구사항
- Docker Engine 20.10 이상
- Docker Compose 2.0 이상
- Git 2.30 이상
- 최소 4GB RAM, 10GB 디스크 공간

## 2. Docker 컨테이너 생성 및 기본 설정

### 개발 환경 컨테이너 생성
```bash
# Ubuntu 기반 개발 환경 컨테이너 실행
docker run -it --name hyundai-chatbot-dev \
  -p 8000:8000 \
  -p 3000:3000 \
  -p 5173:5173 \
  -v $(pwd):/workspace \
  ubuntu:22.04 bash

# 컨테이너 내부에서 기본 도구 설치
apt update && apt install -y \
  git \
  curl \
  wget \
  python3 \
  python3-pip \
  python3-venv \
  nodejs \
  npm \
  build-essential \
  vim \
  nano
```

### Node.js 최신 버전 설치
```bash
# Node.js 20.x 설치
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# 버전 확인
node --version
npm --version
```

## 3. GitHub Repository Clone

### Repository Clone
```bash
# 작업 디렉토리 생성
mkdir -p /app && cd /app

# GitHub repository clone
git clone https://github.com/your-username/hyundai-chatbot.git
cd hyundai-chatbot

# 브랜치 확인
git branch -a
git checkout main
```

### 권한 설정
```bash
# 실행 권한 부여
chmod +x backend/start_server.sh
chmod +x frontend/start_frontend.sh
chmod +x start_local.sh

# 소유권 설정
chown -R root:root .
```

## 4. 환경변수 설정

### 백엔드 환경변수 생성
```bash
cd backend

# 환경변수 파일 생성
cp env.local.example .env

# 환경변수 편집 (nano 또는 vim 사용)
nano .env
```

### 필수 환경변수 설정
```env
# .env 파일 내용
GOOGLE_API_KEY=your-google-api-key-here
GROQCLOUD_API_KEY=your-groq-api-key-here
POTENSDOT_API_KEY=your-potensdot-api-key-here

ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=1

LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

SECRET_KEY=your-secret-key-for-production
```

## 5. 백엔드 배포

### Python 가상환경 설정
```bash
cd /app/hyundai-chatbot/backend

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt
```

### 백엔드 서버 실행 (개발 모드)
```bash
# 개발 서버 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 백그라운드 실행
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

### Docker 컨테이너로 백엔드 배포
```bash
# Dockerfile 수정 (필요시)
cp "Dockerfile 2" Dockerfile
cp "docker-compose 2.yml" docker-compose.yml

# Docker 이미지 빌드
docker build -t hyundai-chatbot-backend .

# Docker Compose로 실행
docker-compose up -d backend
```

## 6. 프론트엔드 배포

### 의존성 설치 및 빌드
```bash
cd /app/hyundai-chatbot/frontend

# 의존성 설치
npm install

# 개발 서버 실행 (테스트용)
npm run dev

# 프로덕션 빌드
npm run build
```

### 정적 파일 서빙
```bash
# 글로벌 serve 설치
npm install -g serve

# 빌드된 파일 서빙
serve -s dist -l 3000

# 백그라운드 실행
nohup serve -s dist -l 3000 &
```

## 7. 전체 시스템 Docker Compose 배포

### Docker Compose 설정 수정
```yaml
# docker-compose.yml 수정
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
    env_file:
      - ./backend/.env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

networks:
  default:
    driver: bridge
```

### 프론트엔드 Dockerfile 생성
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm install

# 소스 코드 복사
COPY . .

# 프로덕션 빌드
RUN npm run build

# 서빙 도구 설치
RUN npm install -g serve

# 포트 노출
EXPOSE 3000

# 정적 파일 서빙
CMD ["serve", "-s", "dist", "-l", "3000"]
```

### 전체 시스템 실행
```bash
# 모든 서비스 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 상태 확인
docker-compose ps
```

## 8. 서비스 상태 확인

### 헬스체크
```bash
# 백엔드 상태 확인
curl http://localhost:8000/health

# 프론트엔드 접속 확인
curl http://localhost:3000

# 컨테이너 상태 확인
docker ps
```

### 로그 모니터링
```bash
# 실시간 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend

# 개별 컨테이너 로그
docker logs hyundai-chatbot-backend
docker logs hyundai-chatbot-frontend
```

## 9. 문제 해결

### 일반적인 문제들
1. **포트 충돌 해결**
```bash
# 포트 사용 중인 프로세스 확인
netstat -tulpn | grep :8000
kill -9 <PID>
```

2. **환경변수 미설정**
```bash
# 환경변수 확인
docker exec -it hyundai-chatbot-backend env | grep API_KEY
```

3. **의존성 설치 실패**
```bash
# 캐시 정리 후 재설치
pip cache purge
pip install -r requirements.txt --force-reinstall
```

4. **Docker 컨테이너 재시작**
```bash
# 컨테이너 재시작
docker-compose restart

# 강제 재빌드
docker-compose up --build -d
```

## 10. 배포 완료 체크리스트

- [ ] Docker 컨테이너 정상 실행
- [ ] GitHub repository clone 성공
- [ ] 환경변수 올바르게 설정
- [ ] 백엔드 서버 8000 포트 접근 가능
- [ ] 프론트엔드 3000 포트 접근 가능
- [ ] API 통신 정상 작동
- [ ] 헬스체크 통과
- [ ] 로그 모니터링 설정 완료

## 11. 운영 관리

### 컨테이너 관리 명령어
```bash
# 서비스 중지
docker-compose stop

# 서비스 재시작
docker-compose restart

# 컨테이너 삭제
docker-compose down

# 이미지 정리
docker system prune -a
```

### 백업 및 복원
```bash
# 코드 백업
tar -czf hyundai-chatbot-$(date +%Y%m%d).tar.gz /app/hyundai-chatbot

# 데이터베이스 백업 (필요시)
# docker exec -it backend-db mysqldump -u root -p dbname > backup.sql
```

이 가이드를 따라 Docker 환경에서 현대해상 AI 챗봇을 성공적으로 배포할 수 있습니다. 