# 현대해상 AI 채팅 상담 시스템 (MVP)

## 전체 챗봇 처리 흐름

```mermaid
flowchart TD
    %% 노드 정의 (Nodes Definition)
    A[사용자 질문 입력]
    B(감정 분석)
    C{감정 결과}
    D[상담사 연결 권장 여부 판단]
    E[FAQ 추천(RAG)]
    F[FAQ 임베딩 로딩 및 유사도 기반 Top-N 추출]
    G[프롬프트 생성 (햇살봇 페르소나 + 감정 + FAQ)]
    H[LLM(Potens.AI) 답변 생성]
    I[감정 기반 응답 강화 및 상담사 연결 안내]
    J[챗봇 응답 반환]
    K[대화 히스토리 저장]
    L[프론트엔드에 응답 표시]

    %% 관계 정의 (Links Definition)
    A --> B
    B --> C
    C -- "부정/분노/불만 등" --> D
    C -- "중립/긍정 등" --> E
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
```

## 프로젝트 개요
- 현대해상화재보험의 차세대 AI 기반 채팅 상담 시스템 MVP
- FastAPI(백엔드) + React(프론트엔드) + Sentence Transformers 기반 RAG + Potensdot 감정분석
- 모바일 최적화, FAQ 추천, 감정 분석, 보험 엔터티 추출, 맞춤형 응답 등 핵심 기능 구현

## 기술 스펙
- **백엔드:** Python, FastAPI, Uvicorn, python-dotenv, requests, sentence-transformers, numpy
- **프론트엔드:** React, Vite, react-markdown
- **데이터:** FAQ(로컬 JSON), FAQ 임베딩(pkl), LocalStorage(히스토리)
- **AI/ML:** RAG(FAQ 임베딩+검색), Potensdot 감정분석 API

## 폴더 구조
```
hyundai-chatbot/
├── backend/           # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── rag/         # FAQ 데이터, 임베딩, RAG 검색
│   │   ├── sentiment/   # 감정 분석
│   │   ├── utils/       # 엔터티 추출, 감정 응답 등
│   │   ├── crm/
│   │   └── logging/
│   └── requirements.txt
├── frontend/          # React 프론트엔드
│   ├── src/
│   ├── public/
│   └── package.json
├── data/              # (확장용) 추가 데이터
├── README.md
└── .gitignore
```

## 주요 기능
- **RAG 기반 FAQ 챗봇**: 사용자의 질문에 대해 FAQ Top-N 검색 + 생성형 답변
- **FAQ 추천 자동화**: 관련도 높은 FAQ 추천(카테고리/태그/유사도)
- **감정 분석**: Potensdot API로 9종 감정 및 강도/트렌드 분석, 맞춤형 응답/상담사 연결
- **보험 엔터티 추출**: 메시지에서 보험 관련 정보 자동 추출
- **대화 히스토리**: localStorage 기반 저장/초기화/재시작
- **UI/UX**: 반응형, 마크다운 지원, 감정/FAQ 시각화, 상담사 연결 경고 등

## 실행 방법
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

## API 예시
- `/chat`: POST, { message, model } → { answer, recommended_faqs, emotion, escalation_needed, entities }
- `/emotion-summary`: GET, 감정 트렌드/분포 요약

## FAQ 추천/감정 분석 예시
```json
{
  "answer": "...",
  "recommended_faqs": [
    { "question": "...", "answer": "...", "score": 0.92, "category": "질병/상해", "tags": ["질병/상해"] }
  ],
  "emotion": { "emotion": "불만", "intensity": 4, ... },
  "escalation_needed": true,
  "entities": { ... }
}
```

## 확장 가능성
- FAQ 태그 자동화(키워드 추출), 사용자별 맞춤형 챗봇, 관리자 대시보드 등

---
문의: 담당자에게 연락 바랍니다.
