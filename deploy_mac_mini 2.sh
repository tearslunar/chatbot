#!/bin/bash

# 현대해상 AI 챗봇 맥미니 배포 스크립트
# 작성자: AI Assistant
# 날짜: 2024-12-18

set -e

echo "======================================"
echo "현대해상 AI 챗봇 맥미니 배포 시작"
echo "======================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 시스템 요구사항 확인
check_requirements() {
    log_info "시스템 요구사항 확인 중..."
    
    # macOS 버전 확인
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "macOS에서만 실행 가능합니다."
        exit 1
    fi
    
    # Docker 설치 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        log_info "Docker Desktop for Mac을 설치하세요: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    fi
    
    # Node.js 확인
    if ! command -v node &> /dev/null; then
        log_error "Node.js가 설치되지 않았습니다."
        log_info "Node.js를 설치하세요: https://nodejs.org"
        exit 1
    fi
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3이 설치되지 않았습니다."
        exit 1
    fi
    
    log_info "모든 요구사항이 충족되었습니다."
}

# 환경변수 설정
setup_environment() {
    log_info "환경변수 설정 중..."
    
    cd backend
    
    if [ ! -f ".env" ]; then
        log_info "환경변수 파일 생성 중..."
        cp env.example .env
        
        log_warn "중요: .env 파일에서 다음 값들을 설정하세요:"
        log_warn "- GOOGLE_API_KEY: Google API 키"
        log_warn "- GROGCLOUD_API_KEY: GrogCloud API 키"
        log_warn "- POTENSDOT_API_KEY: PotensAI API 키"
        
        # 맥미니 IP 주소 자동 설정
        LOCAL_IP=$(ipconfig getifaddr en0)
        if [ -n "$LOCAL_IP" ]; then
            sed -i '' "s/ALLOWED_ORIGINS=.*/ALLOWED_ORIGINS=http:\/\/localhost:3000,http:\/\/localhost:5173,http:\/\/$LOCAL_IP:3000,http:\/\/$LOCAL_IP:5173/" .env
            log_info "로컬 IP 주소 ($LOCAL_IP)를 CORS 허용 도메인에 추가했습니다."
        fi
        
        read -p "환경변수 설정을 완료하고 Enter를 눌러주세요..."
    fi
    
    cd ..
}

# 프론트엔드 빌드
build_frontend() {
    log_info "프론트엔드 빌드 중..."
    
    cd frontend
    
    # 의존성 설치
    if [ ! -d "node_modules" ]; then
        log_info "프론트엔드 의존성 설치 중..."
        npm install
    fi
    
    # 프로덕션 빌드
    log_info "프론트엔드 프로덕션 빌드 중..."
    npm run build
    
    if [ -d "dist" ]; then
        log_info "프론트엔드 빌드 완료: dist/ 폴더 생성됨"
    else
        log_error "프론트엔드 빌드 실패"
        exit 1
    fi
    
    cd ..
}

# 가상환경 검증 및 설정
setup_virtual_environment() {
    log_info "가상환경 설정 확인 중..."
    
    cd backend
    
    # 기존 가상환경이 손상되었는지 확인
    if [ -d "venv" ] && [ ! -f "venv/bin/python" ]; then
        log_warn "손상된 가상환경을 발견했습니다. 재생성합니다..."
        rm -rf venv
    fi
    
    # 가상환경이 없으면 생성
    if [ ! -d "venv" ]; then
        log_info "새 가상환경 생성 중..."
        python3 -m venv venv
        
        if [ $? -eq 0 ]; then
            log_info "가상환경 생성 완료"
        else
            log_error "가상환경 생성 실패"
            exit 1
        fi
    fi
    
    # 가상환경 활성화 및 패키지 설치
    source venv/bin/activate
    
    log_info "패키지 설치/업데이트 중..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        log_info "패키지 설치 완료"
    else
        log_error "패키지 설치 실패"
        exit 1
    fi
    
    cd ..
}

# 백엔드 Docker 빌드
build_backend() {
    log_info "백엔드 Docker 이미지 빌드 중..."
    
    cd backend
    
    # Docker 이미지 빌드
    docker build -t hyundai-chatbot-backend .
    
    if [ $? -eq 0 ]; then
        log_info "백엔드 Docker 이미지 빌드 완료"
    else
        log_error "백엔드 Docker 이미지 빌드 실패"
        exit 1
    fi
    
    cd ..
}

# Nginx 설정 파일 생성
create_nginx_config() {
    log_info "Nginx 설정 파일 생성 중..."
    
    cat > backend/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # 로그 설정
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
    
    # 업스트림 백엔드 서버
    upstream backend {
        server backend:8000;
    }
    
    # 프론트엔드 서버
    server {
        listen 80;
        server_name localhost;
        
        # 정적 파일 서빙
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }
        
        # API 프록시
        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # 헬스체크
        location /health {
            proxy_pass http://backend/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF
    
    log_info "Nginx 설정 파일 생성 완료"
}

# Docker Compose 수정
update_docker_compose() {
    log_info "Docker Compose 설정 업데이트 중..."
    
    cd backend
    
    # 프론트엔드 정적 파일을 Nginx에 마운트하도록 수정
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # 백엔드 서비스
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
    env_file:
      - .env
    volumes:
      - ./app:/app/app
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - chatbot-network

  # Nginx 웹 서버
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ../frontend/dist:/usr/share/nginx/html
      - ./logs:/var/log/nginx
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - chatbot-network

networks:
  chatbot-network:
    driver: bridge

volumes:
  app-data:
    driver: local
EOF
    
    cd ..
    log_info "Docker Compose 설정 업데이트 완료"
}

# 서비스 시작
start_services() {
    log_info "서비스 시작 중..."
    
    cd backend
    
    # 기존 컨테이너 정리
    docker-compose down --remove-orphans
    
    # 서비스 시작
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        log_info "서비스 시작 완료"
        
        # 서비스 상태 확인
        sleep 10
        
        if docker-compose ps | grep -q "Up"; then
            log_info "서비스가 정상적으로 실행 중입니다."
            
            # 로컬 IP 주소 표시
            LOCAL_IP=$(ipconfig getifaddr en0)
            if [ -n "$LOCAL_IP" ]; then
                log_info "서비스 접속 주소:"
                log_info "- 로컬: http://localhost"
                log_info "- 네트워크: http://$LOCAL_IP"
            fi
        else
            log_error "서비스 시작 실패"
            docker-compose logs
            exit 1
        fi
    else
        log_error "서비스 시작 실패"
        exit 1
    fi
    
    cd ..
}

# 자동 시작 스크립트 생성
create_launchd_service() {
    log_info "자동 시작 서비스 생성 중..."
    
    CURRENT_DIR=$(pwd)
    PLIST_FILE="$HOME/Library/LaunchAgents/com.hyundai.chatbot.plist"
    
    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hyundai.chatbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd $CURRENT_DIR/backend && docker-compose up -d</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/hyundai-chatbot.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/hyundai-chatbot.error.log</string>
</dict>
</plist>
EOF
    
    # 서비스 등록
    launchctl load "$PLIST_FILE"
    
    log_info "자동 시작 서비스 생성 완료"
    log_info "서비스 관리 명령어:"
    log_info "- 시작: launchctl start com.hyundai.chatbot"
    log_info "- 중지: launchctl stop com.hyundai.chatbot"
    log_info "- 제거: launchctl unload $PLIST_FILE"
}

# 모니터링 스크립트 생성
create_monitoring_script() {
    log_info "모니터링 스크립트 생성 중..."
    
    cat > monitor_chatbot.sh << 'EOF'
#!/bin/bash

# 현대해상 AI 챗봇 모니터링 스크립트

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "======================================"
echo "현대해상 AI 챗봇 상태 모니터링"
echo "======================================"

# Docker 컨테이너 상태 확인
echo -e "\n${YELLOW}Docker 컨테이너 상태:${NC}"
cd backend
docker-compose ps

# 헬스체크
echo -e "\n${YELLOW}백엔드 헬스체크:${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 백엔드 서비스 정상${NC}"
else
    echo -e "${RED}✗ 백엔드 서비스 비정상${NC}"
fi

# 프론트엔드 확인
echo -e "\n${YELLOW}프론트엔드 상태:${NC}"
if curl -f http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 프론트엔드 서비스 정상${NC}"
else
    echo -e "${RED}✗ 프론트엔드 서비스 비정상${NC}"
fi

# 로그 확인
echo -e "\n${YELLOW}최근 로그:${NC}"
docker-compose logs --tail=10

# 시스템 리소스 사용량
echo -e "\n${YELLOW}시스템 리소스:${NC}"
echo "CPU 사용률: $(top -l 1 | grep "CPU usage" | awk '{print $3}' | cut -d% -f1)%"
echo "메모리 사용률: $(memory_pressure | grep "System-wide memory free percentage" | awk '{print 100-$5}')%"
echo "디스크 사용률: $(df -h / | tail -1 | awk '{print $5}')"

cd ..
EOF
    
    chmod +x monitor_chatbot.sh
    log_info "모니터링 스크립트 생성 완료 (./monitor_chatbot.sh)"
}

# 백업 스크립트 생성
create_backup_script() {
    log_info "백업 스크립트 생성 중..."
    
    cat > backup_chatbot.sh << 'EOF'
#!/bin/bash

# 현대해상 AI 챗봇 백업 스크립트

BACKUP_DIR="$HOME/chatbot_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="chatbot_backup_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "백업 시작: $BACKUP_FILE"

# 백업 대상 파일들
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude="node_modules" \
    --exclude="venv" \
    --exclude="__pycache__" \
    --exclude=".git" \
    --exclude="dist" \
    --exclude="*.log" \
    .

if [ $? -eq 0 ]; then
    echo "백업 완료: $BACKUP_DIR/$BACKUP_FILE"
    
    # 7일 이상 된 백업 파일 삭제
    find "$BACKUP_DIR" -name "chatbot_backup_*.tar.gz" -mtime +7 -delete
    
    echo "백업 파일 목록:"
    ls -la "$BACKUP_DIR"
else
    echo "백업 실패"
    exit 1
fi
EOF
    
    chmod +x backup_chatbot.sh
    log_info "백업 스크립트 생성 완료 (./backup_chatbot.sh)"
}

# 메인 실행 함수
main() {
    log_info "배포 시작 시간: $(date)"
    
    check_requirements
    setup_environment
    setup_virtual_environment
    build_frontend
    create_nginx_config
    update_docker_compose
    build_backend
    start_services
    create_launchd_service
    create_monitoring_script
    create_backup_script
    
    log_info "======================================"
    log_info "배포 완료!"
    log_info "======================================"
    
    LOCAL_IP=$(ipconfig getifaddr en0)
    log_info "서비스 접속 주소:"
    log_info "- 로컬: http://localhost"
    if [ -n "$LOCAL_IP" ]; then
        log_info "- 네트워크: http://$LOCAL_IP"
    fi
    
    log_info ""
    log_info "관리 명령어:"
    log_info "- 상태 확인: ./monitor_chatbot.sh"
    log_info "- 백업: ./backup_chatbot.sh"
    log_info "- 서비스 재시작: cd backend && docker-compose restart"
    log_info "- 서비스 중지: cd backend && docker-compose down"
    log_info "- 로그 확인: cd backend && docker-compose logs -f"
    
    log_info ""
    log_info "배포 완료 시간: $(date)"
}

# 스크립트 실행
main "$@" 