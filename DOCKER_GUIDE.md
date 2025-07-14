# 🐳 현대해상 Hi-Care AI 챗봇 Docker 가이드

## 📋 개요

이 프로젝트는 Docker를 사용하여 프론트엔드(React + Nginx), 백엔드(FastAPI), Redis로 구성된 마이크로서비스 아키텍처로 구성되어 있습니다.

## 🚀 빠른 시작

### 프로덕션 환경 실행

```bash
# 전체 서비스 빌드 및 실행
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f
```

### 개발 환경 실행

```bash
# 개발 환경 실행 (핫 리로드 지원)
docker-compose -f docker-compose.dev.yml up -d

# 개발 서버 로그 확인
docker-compose -f docker-compose.dev.yml logs -f frontend backend
```

## 🏗️ 서비스 구성

### 프론트엔드 (frontend)
- **포트**: 3000 (프로덕션), 5173 (개발)
- **기술스택**: React + Vite + Nginx
- **URL**: http://localhost:3000

### 백엔드 (backend)
- **포트**: 8000
- **기술스택**: FastAPI + Python 3.11
- **API 문서**: http://localhost:8000/docs

### Redis (redis)
- **포트**: 6379
- **용도**: 캐싱 및 세션 관리

## 🔧 개별 서비스 관리

### 특정 서비스만 재시작
```bash
docker-compose restart backend
docker-compose restart frontend
```

### 특정 서비스 로그 확인
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 특정 서비스 쉘 접속
```bash
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🛠️ 빌드 및 배포

### 이미지 새로 빌드
```bash
# 캐시 무시하고 전체 재빌드
docker-compose build --no-cache

# 특정 서비스만 재빌드
docker-compose build backend
```

### 프로덕션 배포
```bash
# 백그라운드에서 실행
docker-compose up -d

# 서비스 업데이트 (무중단)
docker-compose up -d --no-deps backend
```

## 🔍 트러블슈팅

### 포트 충돌 해결
```bash
# 사용 중인 포트 확인
lsof -i :3000
lsof -i :8000

# 컨테이너 완전 제거
docker-compose down -v
```

### 데이터베이스/캐시 초기화
```bash
# 볼륨 포함 전체 제거
docker-compose down -v

# Redis 데이터만 초기화
docker volume rm $(docker volume ls -q | grep redis)
```

### 로그 및 디버깅
```bash
# 전체 로그 확인
docker-compose logs

# 실시간 로그 추적
docker-compose logs -f --tail=100

# 컨테이너 상태 확인
docker-compose ps
docker stats
```

## 🔐 환경 변수 설정

### 백엔드 환경 변수 (.env 파일)
```env
# API 키
POTENSDOT_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here

# 데이터베이스
DATABASE_URL=sqlite:///./data/app.db

# Redis
REDIS_URL=redis://redis:6379/0

# 로깅
LOG_LEVEL=INFO
```

### 프론트엔드 환경 변수
```env
VITE_API_URL=http://localhost:8000
```

## 📊 모니터링

### 헬스체크 확인
```bash
# 모든 서비스 헬스체크
curl http://localhost:3000/health
curl http://localhost:8000/health

# Redis 상태 확인
docker-compose exec redis redis-cli ping
```

### 리소스 사용량 확인
```bash
# 컨테이너별 리소스 사용량
docker stats

# 디스크 사용량
docker system df
```

## 🧹 정리 명령어

### 컨테이너 정리
```bash
# 서비스 중지 및 컨테이너 제거
docker-compose down

# 볼륨 포함 완전 제거
docker-compose down -v

# 이미지까지 제거
docker-compose down --rmi all
```

### 시스템 정리
```bash
# 사용하지 않는 컨테이너/이미지 정리
docker system prune -a

# 볼륨 정리
docker volume prune
```

## 🔄 업데이트 절차

1. **코드 업데이트**
```bash
git pull origin main
```

2. **이미지 재빌드**
```bash
docker-compose build --no-cache
```

3. **서비스 재시작**
```bash
docker-compose up -d
```

4. **헬스체크 확인**
```bash
docker-compose ps
```

## 📝 추가 정보

- **개발 환경**: `docker-compose.dev.yml` 사용
- **프로덕션 환경**: `docker-compose.yml` 사용
- **로그 위치**: Docker 볼륨 `app-logs`
- **데이터 지속성**: `redis-data` 볼륨 사용

## 🆘 문제 해결

문제가 발생하면 다음 순서로 확인하세요:

1. `docker-compose ps`로 서비스 상태 확인
2. `docker-compose logs`로 오류 로그 확인
3. `docker-compose down && docker-compose up -d`로 재시작
4. 여전히 문제가 있으면 `docker-compose down -v && docker-compose up -d`로 완전 초기화