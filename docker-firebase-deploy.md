# Firebase Hosting + Docker Backend 배포 가이드

## 배포 구조
- **프론트엔드**: Firebase Hosting (https://your-project.web.app)
- **백엔드**: Docker 서버 (http://서버IP:7713)

## 1단계: Docker 안에서 백엔드 실행

### 기본 도구 설치
```bash
# Docker 컨테이너 안에서 실행
apt update && apt install -y git curl python3 python3-pip python3-venv nodejs npm

# Node.js 최신 버전 설치
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
```

### GitHub Repository Clone
```bash
# 작업 디렉토리로 이동
cd /workspace  # 또는 원하는 디렉토리

# GitHub repo clone
git clone https://github.com/your-username/hyundai-chatbot.git
cd hyundai-chatbot
```

### 백엔드 설정 및 실행
```bash
cd backend

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp env.local.example .env

# .env 파일 편집 (중요!)
nano .env
```

### 환경변수 설정 내용
```env
# .env 파일
GOOGLE_API_KEY=your-google-api-key-here
GROQCLOUD_API_KEY=your-groq-api-key-here
POTENSDOT_API_KEY=your-potensdot-api-key-here

ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8888
WORKERS=1

LOG_LEVEL=INFO
# Firebase 도메인 + 서버 IP 모두 허용
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-project.web.app,https://your-project.firebaseapp.com,http://서버IP:7713,http://*

SECRET_KEY=your-secret-key-for-production
```

### 백엔드 실행
```bash
# 포트 8888로 실행 (외부 7713으로 접속)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload

# 백그라운드 실행하려면
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 &
```

## 2단계: Firebase 프로젝트 설정

### Firebase CLI 설치 (Docker 안에서)
```bash
# Firebase CLI 설치
npm install -g firebase-tools

# Firebase 로그인
firebase login --no-localhost
# 표시되는 URL을 복사해서 브라우저에서 인증
```

### Firebase 프로젝트 초기화
```bash
cd frontend

# Firebase 프로젝트 초기화
firebase init hosting

# 설정 옵션:
# ? What do you want to use as your public directory? dist
# ? Configure as a single-page app (rewrite all urls to /index.html)? Yes
# ? Set up automatic builds and deploys with GitHub? No
# ? File dist/index.html already exists. Overwrite? No
```

## 3단계: 프론트엔드 수정 및 배포

### API 엔드포인트 수정
```javascript
// frontend/src/App.jsx 또는 API 설정 파일에서
const API_BASE_URL = 'http://서버IP:7713';  // 실제 서버 IP로 변경

// 또는 환경변수 사용
// const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

### 프론트엔드 빌드 및 배포
```bash
cd frontend

# 의존성 설치
npm install

# 프로덕션 빌드
npm run build

# Firebase에 배포
firebase deploy --only hosting

# 배포 완료 후 제공되는 URL 확인
# https://your-project.web.app
# https://your-project.firebaseapp.com
```

## 4단계: CORS 설정 업데이트

### 백엔드 CORS 설정
```bash
# 배포 완료 후 실제 Firebase URL로 업데이트
cd backend
nano .env

# ALLOWED_ORIGINS에 실제 Firebase URL 추가
ALLOWED_ORIGINS=https://your-actual-project.web.app,https://your-actual-project.firebaseapp.com,http://서버IP:7713
```

### 백엔드 재시작
```bash
# 백엔드 재시작 (환경변수 변경 적용)
# Ctrl+C로 서버 중지 후 재시작
python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

## 5단계: 배포 완료 확인

### 서비스 접속 테스트
```bash
# 백엔드 헬스체크
curl http://서버IP:7713/health

# 프론트엔드 접속
# 브라우저에서 https://your-project.web.app 접속
```

### 배포 완료 체크리스트
- [ ] Docker 컨테이너에서 백엔드 정상 실행 (포트 8888)
- [ ] 외부에서 http://서버IP:7713으로 API 접속 가능
- [ ] Firebase 프로젝트 생성 및 설정 완료
- [ ] 프론트엔드 Firebase Hosting 배포 완료
- [ ] CORS 설정으로 Firebase → Docker API 통신 가능
- [ ] 전체 시스템 정상 작동 확인

## 장점
- **프론트엔드**: Firebase CDN으로 빠른 로딩
- **백엔드**: Docker 서버에서 AI 모델 활용 가능
- **HTTPS**: Firebase에서 자동 SSL 제공
- **확장성**: 각각 독립적으로 스케일링 가능

## 유지보수
```bash
# 프론트엔드 업데이트
cd frontend
npm run build
firebase deploy --only hosting

# 백엔드 업데이트
cd backend
git pull
# 필요시 의존성 재설치
pip install -r requirements.txt
# 서버 재시작
```

이제 단계별로 진행하시면 됩니다! 