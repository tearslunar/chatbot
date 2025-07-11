# Hi-Care AI 챗봇 백엔드 문제 해결 가이드

## 가상환경 관련 문제

### 문제: uvicorn 실행 시 "No such file or directory" 에러

```bash
/Users/.../venv/bin/uvicorn: line 2: /Users/.../python3.13: No such file or directory
```

**원인:** 
- 가상환경이 생성된 후 시스템의 Python 버전이 업데이트됨
- 가상환경이 다른 위치에서 생성되어 경로가 손상됨
- 가상환경 파일이 손상됨

**해결 방법:**

1. **손상된 가상환경 제거:**
   ```bash
   cd backend
   rm -rf venv
   ```

2. **새 가상환경 생성:**
   ```bash
   python3 -m venv venv
   ```

3. **가상환경 활성화:**
   ```bash
   source venv/bin/activate
   ```

4. **패키지 설치:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **서버 실행:**
   ```bash
   cd ..  # 프로젝트 루트로 이동
   source backend/venv/bin/activate
   python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 간편한 서버 시작

프로젝트 루트에서 다음 스크립트 사용:
```bash
./backend/start_server.sh
```

이 스크립트는 자동으로:
- 가상환경 상태 확인
- 문제 발생 시 해결 방법 안내
- 서버 실행

### 예방 방법

1. **Python 버전 고정:**
   - `pyenv` 사용하여 특정 Python 버전 관리
   - 프로젝트별 Python 버전 설정

2. **가상환경 백업:**
   - `pip freeze > requirements.txt` 정기적 실행
   - 패키지 의존성 정보 최신 상태 유지

3. **Docker 사용 고려:**
   - 환경 일관성 보장
   - `backend/Dockerfile` 및 `backend/docker-compose.yml` 활용

## 기타 문제

### 포트 충돌
서버가 시작되지 않는 경우:
```bash
lsof -i :8000  # 포트 사용 중인 프로세스 확인
kill -9 <PID>  # 프로세스 종료
```

### 메모리 부족
AI 모델 로딩 시 메모리 부족:
- 시스템 메모리 16GB 이상 권장
- 다른 메모리 사용량이 높은 앱 종료

### 환경변수 설정
`.env` 파일 설정:
```bash
cp backend/env.example backend/.env
# 필요한 API 키들 설정
```

## 연락처
문제가 지속되는 경우 개발팀에 문의하세요. 