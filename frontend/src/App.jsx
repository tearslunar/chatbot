/**
 * Hi-Care AI 챗봇 메인 애플리케이션
 * 모듈화된 컴포넌트들을 통합하는 메인 앱
 */

import React, { useEffect } from 'react';
import ChatPage from './pages/ChatPage';
import './App.css';

/**
 * 메인 애플리케이션 컴포넌트
 */
function App() {
  // 전역 키보드 단축키 등록
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl + K: 빠른 메뉴 토글
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        // 이벤트 디스패치로 ChatPage에 메뉴 토글 요청
        window.dispatchEvent(new CustomEvent('toggle-quick-menu'));
      }
      
      // Ctrl + L: 대화 기록 삭제
      if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('clear-chat-history'));
      }
      
      // Esc: 모든 모달 닫기
      if (e.key === 'Escape') {
        window.dispatchEvent(new CustomEvent('close-all-modals'));
      }
    };

    // PWA 설치 프롬프트 처리
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      // PWA 설치 프롬프트를 나중에 표시하기 위해 저장
      window.deferredPrompt = e;
      console.log('[PWA] 설치 프롬프트 저장됨');
    };

    // 오프라인/온라인 상태 처리
    const handleOnline = () => {
      console.log('[네트워크] 온라인 상태');
      window.dispatchEvent(new CustomEvent('network-status-change', { 
        detail: { online: true } 
      }));
    };

    const handleOffline = () => {
      console.log('[네트워크] 오프라인 상태');
      window.dispatchEvent(new CustomEvent('network-status-change', { 
        detail: { online: false } 
      }));
    };

    // 이벤트 리스너 등록
    document.addEventListener('keydown', handleKeyDown);
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // 초기 네트워크 상태 확인
    if (!navigator.onLine) {
      handleOffline();
    }

    // 컴포넌트 언마운트 시 정리
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // 에러 바운더리 역할
  useEffect(() => {
    const handleError = (error) => {
      console.error('[앱] 전역 에러:', error);
      // 에러 로깅 (실제 서비스에서는 에러 추적 서비스로 전송)
    };

    const handleUnhandledRejection = (event) => {
      console.error('[앱] 처리되지 않은 Promise 거부:', event.reason);
      // Promise 거부 로깅
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  return (
    <div className="App">
      {/* 오프라인 인디케이터 */}
      <OfflineIndicator />
      
      {/* PWA 설치 프롬프트 */}
      <PWAInstallPrompt />
      
      {/* 메인 채팅 페이지 */}
      <ChatPage />
      
      {/* 전역 네트워크 상태 핸들러 */}
      <NetworkStatusHandler />
    </div>
  );
}

/**
 * 오프라인 상태 표시 컴포넌트
 */
function OfflineIndicator() {
  const [isOnline, setIsOnline] = React.useState(navigator.onLine);

  React.useEffect(() => {
    const handleNetworkChange = (e) => {
      setIsOnline(e.detail.online);
    };

    window.addEventListener('network-status-change', handleNetworkChange);
    return () => window.removeEventListener('network-status-change', handleNetworkChange);
  }, []);

  if (isOnline) return null;

  return (
    <div className="offline-indicator">
      <div className="offline-content">
        <span className="offline-icon">📡</span>
        <span className="offline-text">오프라인 모드</span>
        <span className="offline-description">인터넷 연결을 확인해주세요</span>
      </div>
    </div>
  );
}

/**
 * PWA 설치 프롬프트 컴포넌트
 */
function PWAInstallPrompt() {
  const [showInstallPrompt, setShowInstallPrompt] = React.useState(false);
  const [deferredPrompt, setDeferredPrompt] = React.useState(null);

  React.useEffect(() => {
    const handleBeforeInstallPrompt = (e) => {
      setDeferredPrompt(e);
      setShowInstallPrompt(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    
    // 이미 설치된 경우 프롬프트 숨기기
    if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
      setShowInstallPrompt(false);
    }

    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    console.log(`[PWA] 사용자 선택: ${outcome}`);
    setDeferredPrompt(null);
    setShowInstallPrompt(false);
  };

  const handleDismiss = () => {
    setShowInstallPrompt(false);
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
  };

  // 이미 거부한 경우 24시간 후에 다시 표시
  const dismissed = localStorage.getItem('pwa-install-dismissed');
  if (dismissed && Date.now() - parseInt(dismissed) < 24 * 60 * 60 * 1000) {
    return null;
  }

  if (!showInstallPrompt) return null;

  return (
    <div className="pwa-install-prompt">
      <div className="install-content">
        <span className="install-icon">📱</span>
        <div className="install-text">
          <strong>Hi-Care 앱 설치</strong>
          <p>홈 화면에 추가하여 더 편리하게 이용하세요</p>
        </div>
        <div className="install-actions">
          <button onClick={handleDismiss} className="dismiss-btn">
            나중에
          </button>
          <button onClick={handleInstall} className="install-btn">
            설치
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * 네트워크 상태 핸들러 컴포넌트
 */
function NetworkStatusHandler() {
  React.useEffect(() => {
    const handleNetworkChange = (e) => {
      const { online } = e.detail;
      
      if (online) {
        // 온라인 복구 시 알림
        showNotification('인터넷 연결이 복구되었습니다', 'success');
        // 대기 중인 요청들 재시도
        retryPendingRequests();
      } else {
        // 오프라인 시 알림
        showNotification('인터넷 연결이 끊어졌습니다', 'warning');
      }
    };

    window.addEventListener('network-status-change', handleNetworkChange);
    return () => window.removeEventListener('network-status-change', handleNetworkChange);
  }, []);

  return null;
}

/**
 * 알림 표시 함수
 */
function showNotification(message, type = 'info') {
  // 간단한 토스트 알림 (실제로는 전용 알림 라이브러리 사용 권장)
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 16px;
    border-radius: 8px;
    background: ${type === 'success' ? '#4CAF50' : type === 'warning' ? '#FF9800' : '#2196F3'};
    color: white;
    z-index: 10000;
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
  `;
  
  document.body.appendChild(notification);
  
  // 3초 후 자동 제거
  setTimeout(() => {
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 3000);
}

/**
 * 대기 중인 요청 재시도 함수
 */
function retryPendingRequests() {
  // Service Worker와 통신하여 대기 중인 요청들 재시도
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage({
      type: 'RETRY_PENDING_REQUESTS'
    });
  }
}

export default App; 