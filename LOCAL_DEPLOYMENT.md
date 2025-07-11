# 🚀 Hi-Care AI 챗봇 로컬 배포 가이드

## 📋 시스템 요구사항

- **Python**: 3.8 이상
- **Node.js**: 16 이상
- **npm**: 7 이상 
- **macOS/Linux**: Bash 셸 지원
- **메모리**: 최소 4GB RAM 권장
- **디스크**: 최소 2GB 여유 공간

## 🚀 빠른 시작 (원클릭 실행)

### 전체 실행 (백엔드 + 프론트엔드)
```bash
./start_local.sh
```

### 개별 실행
```bash
# 백엔드만 실행
./start_local.sh backend

# 프론트엔드만 실행  
./start_local.sh frontend

# 도움말
./start_local.sh help
```

## 📦 단계별 설치 가이드

### 1. 저장소 클론
```bash
git clone https://github.com/tearslunar/chatbot.git
cd chatbot
```

### 2. 백엔드 설정

#### 2.1 환경변수 설정
```bash
cd backend
cp env.local.example .env
```

#### 2.2 .env 파일 편집 (중요!)
```bash
# 실제 API 키로 교체하세요
GOOGLE_API_KEY=실제_구글_API_키
GROQCLOUD_API_KEY=실제_GROQ_API_키
POTENSDOT_API_KEY=실제_POTENSDOT_API_키
```

#### 2.3 백엔드 실행
```bash
./start_server.sh
```

### 3. 프론트엔드 설정 (새 터미널)

#### 3.1 프론트엔드 실행
```bash
cd frontend
./start_frontend.sh
```

## 🌐 접속 정보

- **프론트엔드**: http://localhost:5173
- **백엔드 API**: http://localhost:8000  
- **API 문서**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 세부 설정

### API 키 발급 방법

#### Google API Key
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 또는 선택
3. APIs & Services > Credentials
4. Create Credentials > API Key

#### Groq API Key
1. [Groq Console](https://console.groq.com/) 접속
2. 계정 생성/로그인
3. API Keys 섹션에서 새 키 생성

#### Potensdot API Key
1. Potensdot 서비스 문의 및 계약
2. 제공받은 API 키 사용

### 데이터 폴더 구조
```
data/
├── hi_care_약관_fixed_txt/     # 약관 텍스트 파일들
├── terms_embeddings.pkl        # 약관 임베딩 (자동 생성)
├── faq_embeddings.pkl          # FAQ 임베딩 (자동 생성)
└── customer_persona.csv        # 고객 페르소나 데이터
```

## 🛠️ 문제 해결

### 일반적인 문제들

#### 1. 가상환경 오류
```bash
# 가상환경 재생성
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. 임베딩 파일 없음
```bash
# 임베딩 재생성 (시간 소요)
cd backend
source venv/bin/activate
python -m app.rag.terms_rag    # 약관 임베딩
python -m app.rag.faq_rag      # FAQ 임베딩
```

#### 3. 포트 충돌
- 백엔드 포트 8000 확인: `lsof -i :8000`
- 프론트엔드 포트 5173 확인: `lsof -i :5173`
- 사용 중인 프로세스 종료: `kill -9 PID`

#### 4. Node.js 의존성 오류
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 백엔드 로그 확인
```bash
# 백엔드 로그 실시간 확인
tail -f backend.log

# 백엔드 프로세스 확인
ps aux | grep uvicorn
```

## 🔍 개발 모드 특징

### 백엔드 (FastAPI + Uvicorn)
- **Hot Reload**: 코드 변경 시 자동 재시작
- **API 문서**: `/docs` 경로에서 Swagger UI 제공
- **로깅**: 개발용 상세 로그 출력

### 프론트엔드 (React + Vite)
- **Hot Module Replacement**: 실시간 UI 업데이트
- **개발자 도구**: React DevTools 지원
- **빠른 빌드**: Vite의 고속 번들링

## 📊 성능 모니터링

### 백엔드 성능
- **메모리 사용량**: 임베딩 로딩 시 ~500MB
- **시작 시간**: 초기 실행 시 2-3분 (임베딩 로딩)
- **응답 시간**: 일반 쿼리 1-2초, RAG 검색 3-5초

### 프론트엔드 성능
- **번들 크기**: 개발 모드에서 크기 최적화 안됨
- **렌더링**: React 18의 Concurrent Features 사용

## 🧪 테스트

### API 테스트
```bash
# Health Check
curl http://localhost:8000/health

# Chat API 테스트
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요", "conversation_history": []}'
```

### 프론트엔드 테스트
```bash
cd frontend
npm run test  # Jest 테스트 실행
npm run lint  # ESLint 코드 검사
```

## 🚨 주의사항

1. **API 키 보안**: .env 파일은 절대 git에 커밋하지 마세요
2. **메모리 관리**: 임베딩 파일 로딩으로 인한 높은 메모리 사용
3. **네트워크**: AI API 호출을 위한 안정적인 인터넷 연결 필요
4. **데이터**: data/ 폴더의 민감한 정보 보호

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. **로그 파일**: `backend.log` 확인
2. **포트 사용**: 8000, 5173 포트 충돌 확인  
3. **환경변수**: .env 파일의 API 키 설정 확인
4. **네트워크**: AI API 서비스 연결 상태 확인

---

## 🎯 다음 단계

로컬 배포가 완료되었다면:

1. **기능 테스트**: 챗봇의 주요 기능들 테스트
2. **커스터마이징**: 페르소나, FAQ 데이터 수정
3. **성능 튜닝**: 임베딩 파라미터 조정
4. **프로덕션 배포**: Docker 컨테이너 또는 클라우드 배포 검토 