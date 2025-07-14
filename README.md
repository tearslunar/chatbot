# 현대해상 AI 챗봇 시스템 (Hi-Care AI Chatbot)

## 프로젝트 개요
- **백엔드:** Python 3.9+, FastAPI, Uvicorn, Potensdot AI API
- **프론트엔드:** React (Vite), TypeScript
- **주요 기능:** 보험 상담 챗봇, 감정 분석, FAQ/RAG 검색, 페르소나 기반 응답
- **배포:** Docker, Firebase Hosting, 로컬/운영 환경 모두 지원

---

## 폴더 구조
```
hyundai-chatbot/
├── backend/           # FastAPI 백엔드
│   ├── app/           # 주요 백엔드 코드
│   ├── requirements.txt
│   └── ...
├── frontend/          # React 프론트엔드
│   ├── src/
│   ├── public/
│   └── package.json
├── data/              # (FAQ/약관 임베딩 등)
├── README.md
└── ...
```

---

## 빠른 시작 (로컬 개발)

### 1. 저장소 클론
```bash
git clone <이 저장소 주소>
cd hyundai-chatbot
```

### 2. 백엔드 실행
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.local.example .env  # 환경변수 세팅
# .env 파일에서 POTENSDOT_API_KEY 등 필수값 입력
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- 기본 API 포트: **8000**
- API 문서: http://localhost:8000/docs

### 3. 프론트엔드 실행
```bash
cd ../frontend
npm install
npm run dev  # 기본 포트: 5173
```
- 개발 중 API 호출 주소: http://localhost:8000
- 환경변수로 VITE_API_URL 지정 가능

---

## 운영/배포
- **Docker:** docker-compose.yml 참고 (8000:8000, 3000:3000 등)
- **Firebase Hosting:** 프론트엔드 정적 배포, API는 별도 서버 필요
- **Nginx/리버스 프록시:** 운영 환경에서 포트/도메인 매핑 가능

---

## 환경 변수 예시 (backend/.env)
```
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
POTENSDOT_API_KEY=실제키
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 주요 API 예시
- POST /chat/message : 챗봇 대화
- POST /persona/set : 페르소나 설정
- 기타 엔드포인트는 Swagger 문서 참고 (http://localhost:8000/docs)

---

## 자주 묻는 질문/문제 해결
- **포트 충돌:**
  - 8000(백엔드), 5173(프론트엔드) 사용 중인지 확인, 필요시 프로세스 종료 후 재실행
- **CORS 오류:**
  - backend/.env의 ALLOWED_ORIGINS에 프론트엔드 주소 추가
- **임베딩 파일 없음:**
  - backend/data/terms_embeddings.pkl, faq_embeddings.pkl 없으면 자동 생성됨(최초 실행시 수분 소요)
- **API 키 미설정:**
  - .env에서 필수 키 입력

---

## 개발/운영 팁
- **로컬 개발:** 프론트엔드(5173) ↔ 백엔드(8000) CORS 허용 필요
- **운영 배포:** Docker, Nginx, Firebase Hosting 등 환경에 맞게 포트/도메인 매핑
- **문서:** backend/app/main.py, frontend/src/config/settings.js 등 참고

---

## 문의/연락처
- 기술 문의: backend@hyundai-marine.co.kr
- 운영 문의: business@hyundai-marine.co.kr
- 지원 센터: 1588-5656

---

## 라이선스
MIT
