# 🧪 Hi-Care AI 챗봇 테스트 가이드

## 📋 목차

1. [테스트 개요](#테스트-개요)
2. [테스트 환경 설정](#테스트-환경-설정)
3. [테스트 실행](#테스트-실행)
4. [테스트 유형](#테스트-유형)
5. [코드 품질 검사](#코드-품질-검사)
6. [CI/CD 파이프라인](#cicd-파이프라인)
7. [보안 테스트](#보안-테스트)

## 🎯 테스트 개요

Hi-Care AI 챗봇 프로젝트는 견고하고 안정적인 시스템을 보장하기 위해 포괄적인 테스트 전략을 사용합니다.

### 테스트 커버리지 목표
- **단위 테스트**: 80% 이상
- **통합 테스트**: 주요 API 엔드포인트 100%
- **E2E 테스트**: 핵심 사용자 플로우 100%

## 🔧 테스트 환경 설정

### 1. 백엔드 테스트 환경

```bash
cd backend

# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements-dev.txt
```

### 2. 환경 변수 설정

```bash
# 테스트용 환경 변수
export ENVIRONMENT=test
export DEBUG=true
export DATABASE_URL=sqlite:///./test.db
```

## 🚀 테스트 실행

### 빠른 시작

```bash
# 백엔드 테스트 자동 실행
cd backend
./scripts/run_tests.sh
```

### 개별 테스트 실행

```bash
# 단위 테스트만 실행
pytest tests/unit/ -v

# 통합 테스트만 실행
pytest tests/integration/ -v

# 특정 파일 테스트
pytest tests/unit/test_main.py -v

# 특정 테스트 함수 실행
pytest tests/unit/test_main.py::TestMainApp::test_root_endpoint -v
```

### 커버리지 포함 테스트

```bash
# 커버리지 측정
pytest --cov=app --cov-report=html --cov-report=term

# 커버리지 리포트 확인
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
```

## 🧩 테스트 유형

### 1. 단위 테스트 (Unit Tests)

**위치**: `backend/tests/unit/`

개별 함수와 클래스의 동작을 검증합니다.

```python
# 예시: API 엔드포인트 테스트
def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 2. 통합 테스트 (Integration Tests)

**위치**: `backend/tests/integration/`

여러 컴포넌트 간의 상호작용을 검증합니다.

```python
# 예시: 전체 채팅 플로우 테스트
def test_complete_chat_flow(client: TestClient):
    # 1. 인사말
    response = client.post("/chat", json={"message": "안녕하세요"})
    # 2. 보험 문의
    response = client.post("/chat", json={"message": "자동차 보험 문의"})
    # 3. 응답 검증
    assert response.status_code == 200
```

### 3. API 테스트

각 라우터의 엔드포인트를 테스트합니다:

- **채팅 라우터**: `/chat` 엔드포인트
- **페르소나 라우터**: `/personas` 엔드포인트  
- **보험 라우터**: `/insurance` 엔드포인트

### 4. 모킹 (Mocking)

외부 의존성을 모킹하여 격리된 테스트를 수행합니다:

```python
@patch('app.routers.chat.get_llm_response')
def test_chat_response(mock_llm, client):
    mock_llm.return_value = "테스트 응답"
    # 테스트 코드...
```

## 🔍 코드 품질 검사

### 1. 코드 포맷팅

```bash
# Black으로 코드 포맷팅
black app/ tests/

# 포맷팅 검사만 수행
black --check --diff app/ tests/
```

### 2. Import 정렬

```bash
# isort로 import 정렬
isort app/ tests/

# 정렬 검사만 수행
isort --check-only --diff app/ tests/
```

### 3. 린팅

```bash
# flake8 린팅
flake8 app/ tests/

# Ruff 빠른 린팅
ruff check app/ tests/
```

### 4. 타입 검사

```bash
# mypy 타입 검사
mypy app/
```

## 🔄 CI/CD 파이프라인

### GitHub Actions 워크플로우

1. **코드 품질 검사** (`quality-check`)
   - Black, isort, flake8, mypy, ruff 실행

2. **보안 검사** (`security-check`)
   - Bandit, Safety, detect-secrets 실행

3. **백엔드 테스트** (`backend-test`)
   - 다중 Python 버전 테스트 (3.10, 3.11, 3.12)
   - 단위 테스트 및 통합 테스트
   - 커버리지 측정

4. **프론트엔드 테스트** (`frontend-test`)
   - ESLint, Prettier 검사
   - 단위 테스트 및 빌드 테스트

5. **Docker 빌드** (`docker-test`)
   - 컨테이너 이미지 빌드 검증

### 로컬에서 CI 환경 재현

```bash
# 전체 CI 파이프라인 시뮬레이션
cd backend
export ENVIRONMENT=test
./scripts/run_tests.sh
```

## 🛡️ 보안 테스트

### 1. 정적 보안 분석

```bash
# Bandit 보안 검사
bandit -r app/ -f json -o bandit-report.json

# 취약점 스캐닝
safety check

# 시크릿 스캐닝
detect-secrets scan --all-files
```

### 2. 의존성 보안 검사

```bash
# 보안 전용 의존성 설치
pip install -r requirements-security.txt

# 종합 보안 검사 실행
pip-audit
semgrep --config=auto app/
```

## 📊 테스트 마커

pytest 마커를 사용하여 특정 종류의 테스트만 실행할 수 있습니다:

```bash
# 단위 테스트만 실행
pytest -m unit

# 통합 테스트만 실행  
pytest -m integration

# 느린 테스트 제외
pytest -m "not slow"

# 보안 테스트만 실행
pytest -m security
```

## 🎯 테스트 모범 사례

### 1. 테스트 작성 원칙

- **Given-When-Then** 패턴 사용
- **AAA (Arrange-Act-Assert)** 패턴 준수
- 테스트는 독립적이고 격리되어야 함
- 명확하고 의미있는 테스트 이름 사용

### 2. 테스트 데이터

- `conftest.py`의 픽스처 활용
- 테스트 데이터는 현실적이고 다양해야 함
- 민감한 데이터는 모킹 사용

### 3. 성능 고려사항

- 테스트 실행 시간 최적화
- 병렬 테스트 실행 활용 (`pytest-xdist`)
- 불필요한 외부 호출 제거

## 🆘 문제 해결

### 자주 발생하는 문제

1. **모듈 import 오류**
   ```bash
   # PYTHONPATH 설정
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **의존성 충돌**
   ```bash
   # 가상 환경 재생성
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-dev.txt
   ```

3. **포트 충돌**
   ```bash
   # 테스트용 포트 설정
   export TEST_PORT=8001
   ```

## 📚 추가 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [FastAPI 테스트 가이드](https://fastapi.tiangolo.com/tutorial/testing/)
- [GitHub Actions 워크플로우 구문](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

✅ **테스트는 코드의 품질과 안정성을 보장하는 핵심 요소입니다. 새로운 기능 개발 시 반드시 해당 테스트도 함께 작성해주세요!** 