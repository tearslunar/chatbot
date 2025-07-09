# 🛠 가상환경 정리 가이드

## 현재 상황
- **상위 폴더 venv** (`./venv`): 8.2M, Python 3.13, 거의 빈 환경
- **backend venv** (`./backend/venv`): 522M, Python 3.12.10, 실제 개발 환경

## 🎯 권장 정리 방법

### 옵션 1: 상위 폴더 venv 제거 (권장)
```bash
# 1. 상위 폴더 venv 제거
rm -rf ./venv

# 2. backend venv만 사용
cd backend
source venv/bin/activate
python --version  # Python 3.12.10 확인
```

### 옵션 2: backend로 표준화
```bash
# 1. 모든 Python 작업은 backend 폴더에서 수행
cd backend

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 패키지 설치/업데이트
pip install -r requirements.txt
```

## 🚀 권장 워크플로우

### 백엔드 개발 시
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### 프론트엔드 개발 시
```bash
cd frontend
npm run dev
```

## 📁 표준 프로젝트 구조
```
hyundai-chatbot/
├── frontend/          # React 앱
│   ├── node_modules/
│   └── package.json
├── backend/           # FastAPI 서버
│   ├── venv/         # Python 가상환경 (유일)
│   ├── requirements.txt
│   └── app/
└── README.md
```

## ⚠️ 주의사항
- 상위 폴더 venv는 사용되지 않으므로 제거 안전
- backend/venv는 실제 개발 환경이므로 보존 필수
- .gitignore에 venv 폴더들이 제외되어 있어 git에는 영향 없음

## ✅ 실행 명령어
```bash
# 불필요한 venv 제거
rm -rf ./venv

# .gitignore 업데이트 (선택사항)
echo "# 상위 폴더 venv 제거됨" >> .gitignore
``` 