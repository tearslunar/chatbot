#!/bin/bash
# 🧪 Hi-Care AI 챗봇 테스트 실행 스크립트

set -e  # 에러 발생 시 중단

echo "🧪 Hi-Care AI 챗봇 테스트 실행 시작"
echo "======================================"

# 환경 변수 설정
export ENVIRONMENT=test
export DEBUG=true

# 가상 환경 활성화 (존재하는 경우)
if [ -d "venv" ]; then
    echo "📦 가상 환경 활성화 중..."
    source venv/bin/activate
fi

# 의존성 설치
echo "📦 테스트 의존성 설치 중..."
pip install -r requirements-dev.txt

# 코드 품질 검사
echo "🔍 코드 품질 검사 실행 중..."
echo "--------------------------------------"

# 코드 포맷팅 검사
echo "🎨 코드 포맷팅 검사 (Black)..."
black --check --diff app/ tests/ || {
    echo "❌ 코드 포맷팅 문제 발견. 'black app/ tests/' 실행하여 수정하세요."
}

# Import 정렬 검사
echo "📦 Import 정렬 검사 (isort)..."
isort --check-only --diff app/ tests/ || {
    echo "❌ Import 정렬 문제 발견. 'isort app/ tests/' 실행하여 수정하세요."
}

# 린팅 검사
echo "🔍 린팅 검사 (flake8)..."
flake8 app/ tests/ || echo "⚠️ 린팅 경고 발견"

# 타입 검사
echo "🔤 타입 검사 (mypy)..."
mypy app/ || echo "⚠️ 타입 체크 경고 발견"

# 보안 검사
echo "🔒 보안 검사 (bandit)..."
bandit -r app/ -f json -o bandit-report.json || echo "⚠️ 보안 경고 발견"

# 취약점 스캐닝
echo "🛡️ 취약점 스캐닝 (safety)..."
safety check || echo "⚠️ 취약점 경고 발견"

# 테스트 실행
echo ""
echo "🧪 테스트 실행 중..."
echo "--------------------------------------"

# 단위 테스트
echo "🔬 단위 테스트 실행..."
pytest tests/unit/ -m unit --no-cov -v

# 통합 테스트
echo "🔗 통합 테스트 실행..."
pytest tests/integration/ -m integration --no-cov -v

# 전체 테스트 (커버리지 포함)
echo "📊 전체 테스트 및 커버리지 분석..."
pytest tests/ --cov=app --cov-report=html --cov-report=term

# 테스트 결과 요약
echo ""
echo "✅ 테스트 완료!"
echo "======================================"
echo "📊 커버리지 리포트: htmlcov/index.html"
echo "🔒 보안 리포트: bandit-report.json"

# 커버리지 임계값 확인
COVERAGE_THRESHOLD=80
COVERAGE_RESULT=$(coverage report --show-missing | tail -n 1 | grep -oE '[0-9]+%' | tr -d '%')

if [ "$COVERAGE_RESULT" -lt "$COVERAGE_THRESHOLD" ]; then
    echo "❌ 커버리지 $COVERAGE_RESULT%가 임계값 $COVERAGE_THRESHOLD% 미만입니다."
    exit 1
else
    echo "✅ 커버리지 $COVERAGE_RESULT%가 임계값을 만족합니다."
fi

echo "🎉 모든 테스트가 성공적으로 완료되었습니다!" 