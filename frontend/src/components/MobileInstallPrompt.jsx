import React, { useState, useEffect } from 'react';
import './MobileInstallPrompt.css';

function MobileInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isInStandaloneMode, setIsInStandaloneMode] = useState(false);

  useEffect(() => {
    // iOS 기기 감지
    const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    setIsIOS(iOS);

    // 스탠드얼론 모드 감지 (이미 설치된 상태)
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                        window.navigator.standalone === true;
    setIsInStandaloneMode(isStandalone);

    // 로컬 스토리지에서 설치 프롬프트 표시 여부 확인
    const installPromptDismissed = localStorage.getItem('installPromptDismissed');
    
    // PWA 설치 이벤트 리스너
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      
      // 조건에 따라 설치 프롬프트 표시
      if (!installPromptDismissed && !isStandalone) {
        setShowInstallPrompt(true);
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // iOS에서는 수동으로 프롬프트 표시
    if (iOS && !isStandalone && !installPromptDismissed) {
      setTimeout(() => {
        setShowInstallPrompt(true);
      }, 3000); // 3초 후 표시
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('PWA 설치 승인됨');
      } else {
        console.log('PWA 설치 거부됨');
      }
      
      setDeferredPrompt(null);
      setShowInstallPrompt(false);
    }
  };

  const handleDismiss = () => {
    setShowInstallPrompt(false);
    localStorage.setItem('installPromptDismissed', 'true');
  };

  const handleNotNow = () => {
    setShowInstallPrompt(false);
    // 24시간 후 다시 표시
    localStorage.setItem('installPromptDismissed', Date.now() + 24 * 60 * 60 * 1000);
  };

  if (isInStandaloneMode || !showInstallPrompt) {
    return null;
  }

  return (
    <div className="install-prompt-overlay">
      <div className="install-prompt">
        <div className="install-prompt-header">
          <div className="install-prompt-icon">📱</div>
          <h3>앱으로 설치하기</h3>
          <button className="install-prompt-close" onClick={handleDismiss}>
            ✕
          </button>
        </div>
        
        <div className="install-prompt-content">
          <p>HiCare를 홈 화면에 추가하여 더 빠르고 편리하게 이용하세요!</p>
          
          <div className="install-benefits">
            <div className="install-benefit">
              <span className="benefit-icon">⚡</span>
              <span>빠른 실행</span>
            </div>
            <div className="install-benefit">
              <span className="benefit-icon">📱</span>
              <span>앱처럼 사용</span>
            </div>
            <div className="install-benefit">
              <span className="benefit-icon">🔔</span>
              <span>알림 수신</span>
            </div>
          </div>

          {isIOS ? (
            <div className="ios-install-guide">
              <p>설치 방법:</p>
              <ol>
                <li>하단의 <strong>공유</strong> 버튼 탭</li>
                <li><strong>"홈 화면에 추가"</strong> 선택</li>
                <li><strong>"추가"</strong> 버튼 탭</li>
              </ol>
            </div>
          ) : (
            <div className="install-prompt-actions">
              <button className="install-button" onClick={handleInstallClick}>
                설치하기
              </button>
              <button className="install-later-button" onClick={handleNotNow}>
                나중에
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MobileInstallPrompt; 