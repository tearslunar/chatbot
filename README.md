# 현대해상 AI 채팅 상담 시스템 (MVP)

## 프로젝트 개요
- 현대해상화재보험의 차세대 AI 기반 채팅 상담 시스템 MVP
- FastAPI(백엔드) + React(프론트엔드) + OpenAI API + FAISS 기반 RAG
- 모바일 최적화, FAQ 기반 답변, 감성분석, 모의 CRM, 데이터 로깅 등 핵심 기능 구현

## 기술 스택
- **백엔드:** Python, FastAPI, Uvicorn, OpenAI, FAISS
- **프론트엔드:** React, Vite, Tailwind CSS(예정)
- **데이터:** FAQ(로컬), 모의 CRM(로컬), 벡터DB(FAISS)

## 폴더 구조
```
hyundai-chatbot/
├── backend/           # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── rag/
│   │   ├── sentiment/
│   │   ├── crm/
│   │   └── logging/
│   └── requirements.txt
├── frontend/          # React 프론트엔드
│   ├── src/
│   ├── public/
│   └── package.json
├── data/              # FAQ, 임베딩, 모의 CRM 등 데이터
├── README.md
└── .gitignore
```

## 실행 방법 (MVP)
### 백엔드
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
### 프론트엔드
```bash
cd frontend
npm install
npm run dev
```
