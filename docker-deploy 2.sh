#!/bin/bash

# Docker 환경에서 현대해상 AI 챗봇 배포 스크립트
# 사용법: ./docker-deploy.sh [options]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 도움말 표시
show_help() {
    echo "현대해상 AI 챗봇 Docker 배포 스크립트"
    echo ""
    echo "사용법: $0 [options]"
    echo ""
    echo "옵션:"
    echo "  -h, --help     도움말 표시"
    echo "  -b, --build    Docker 이미지 강제 재빌드"
    echo "  -d, --dev      개발 모드로 실행"
    echo "  -p, --prod     프로덕션 모드로 실행"
    echo "  -s, --stop     서비스 중지"
    echo "  -r, --restart  서비스 재시작"
    echo "  -l, --logs     로그 확인"
    echo "  -c, --clean    Docker 리소스 정리"
    echo ""
    echo "예시:"
    echo "  $0 -p          # 프로덕션 배포"
    echo "  $0 -b -d       # 개발 모드 재빌드 배포"
    echo "  $0 -s          # 서비스 중지"
    echo "  $0 -l          # 로그 확인"
}

# 사전 준비사항 확인
check_prerequisites() {
    log_info "사전 준비사항 확인 중..."
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    fi
    
    # 환경변수 파일 확인
    if [ ! -f "backend/.env" ]; then
        log_warn "backend/.env 파일이 없습니다."
        if [ -f "backend/env.local.example" ]; then
            log_info "env.local.example에서 .env 파일을 생성합니다."
            cp backend/env.local.example backend/.env
            log_warn "backend/.env 파일을 편집하여 API 키를 설정하세요."
        else
            log_error "환경변수 파일이 존재하지 않습니다."
            exit 1
        fi
    fi
    
    log_info "사전 준비사항 확인 완료"
}

# Docker 이미지 빌드
build_images() {
    log_info "Docker 이미지 빌드 중..."
    
    if [ "$FORCE_BUILD" = true ]; then
        log_info "강제 재빌드 모드"
        docker-compose build --no-cache
    else
        docker-compose build
    fi
    
    log_info "Docker 이미지 빌드 완료"
}

# 서비스 시작
start_services() {
    log_info "서비스 시작 중..."
    
    if [ "$DEV_MODE" = true ]; then
        log_info "개발 모드로 실행"
        docker-compose up -d
    else
        log_info "프로덕션 모드로 실행"
        docker-compose up -d
    fi
    
    log_info "서비스 시작 완료"
}

# 서비스 중지
stop_services() {
    log_info "서비스 중지 중..."
    docker-compose down
    log_info "서비스 중지 완료"
}

# 서비스 재시작
restart_services() {
    log_info "서비스 재시작 중..."
    docker-compose restart
    log_info "서비스 재시작 완료"
}

# 로그 확인
show_logs() {
    log_info "서비스 로그 확인"
    docker-compose logs -f
}

# 서비스 상태 확인
check_health() {
    log_info "서비스 상태 확인 중..."
    
    # 컨테이너 상태 확인
    docker-compose ps
    
    # 헬스체크 확인
    log_info "백엔드 헬스체크..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ 백엔드 서비스 정상"
    else
        log_error "❌ 백엔드 서비스 비정상"
    fi
    
    log_info "프론트엔드 헬스체크..."
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_info "✅ 프론트엔드 서비스 정상"
    else
        log_error "❌ 프론트엔드 서비스 비정상"
    fi
}

# Docker 리소스 정리
clean_resources() {
    log_info "Docker 리소스 정리 중..."
    
    # 중지된 컨테이너 정리
    docker container prune -f
    
    # 사용하지 않는 이미지 정리
    docker image prune -f
    
    # 사용하지 않는 볼륨 정리
    docker volume prune -f
    
    # 사용하지 않는 네트워크 정리
    docker network prune -f
    
    log_info "Docker 리소스 정리 완료"
}

# 메인 함수
main() {
    # 변수 초기화
    FORCE_BUILD=false
    DEV_MODE=false
    PROD_MODE=false
    STOP_SERVICES=false
    RESTART_SERVICES=false
    SHOW_LOGS=false
    CLEAN_RESOURCES=false
    
    # 인자 파싱
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -b|--build)
                FORCE_BUILD=true
                shift
                ;;
            -d|--dev)
                DEV_MODE=true
                shift
                ;;
            -p|--prod)
                PROD_MODE=true
                shift
                ;;
            -s|--stop)
                STOP_SERVICES=true
                shift
                ;;
            -r|--restart)
                RESTART_SERVICES=true
                shift
                ;;
            -l|--logs)
                SHOW_LOGS=true
                shift
                ;;
            -c|--clean)
                CLEAN_RESOURCES=true
                shift
                ;;
            *)
                log_error "알 수 없는 옵션: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 작업 디렉토리 확인
    if [ ! -f "docker-compose.yml" ]; then
        log_error "docker-compose.yml 파일이 없습니다. 프로젝트 루트 디렉토리에서 실행하세요."
        exit 1
    fi
    
    # 액션 실행
    if [ "$STOP_SERVICES" = true ]; then
        stop_services
    elif [ "$RESTART_SERVICES" = true ]; then
        restart_services
    elif [ "$SHOW_LOGS" = true ]; then
        show_logs
    elif [ "$CLEAN_RESOURCES" = true ]; then
        clean_resources
    else
        # 기본 배포 프로세스
        log_info "현대해상 AI 챗봇 Docker 배포 시작"
        check_prerequisites
        build_images
        start_services
        
        sleep 10  # 서비스 시작 대기
        check_health
        
        log_info "배포 완료!"
        log_info "백엔드: http://localhost:8000"
        log_info "프론트엔드: http://localhost:3000"
    fi
}

# 스크립트 실행
main "$@" 