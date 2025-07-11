/**
 * 빠른 메뉴 컴포넌트
 * 상담 중 자주 사용하는 기능들에 빠르게 접근할 수 있는 메뉴
 */

import React, { useState } from 'react';

/**
 * 빠른 메뉴 컴포넌트
 * @param {Function} onEndChat - 상담 종료 핸들러
 * @param {Function} onClearHistory - 히스토리 삭제 핸들러
 * @param {Function} onRestartSession - 세션 재시작 핸들러
 * @param {Function} onClose - 메뉴 닫기 핸들러
 * @param {boolean} isSessionEnded - 세션 종료 여부
 */
function QuickMenu({ 
  onEndChat, 
  onClearHistory, 
  onRestartSession, 
  onClose, 
  isSessionEnded 
}) {
  const [showConfirm, setShowConfirm] = useState(null);

  const menuItems = [
    {
      id: 'restart',
      icon: '🔄',
      label: '새 상담 시작',
      description: '현재 세션을 초기화하고 새로 시작',
      action: onRestartSession,
      visible: isSessionEnded,
      confirmMessage: '새 상담을 시작하시겠습니까?'
    },
    {
      id: 'end',
      icon: '🔚',
      label: '상담 종료',
      description: '현재 상담을 종료하고 피드백 작성',
      action: onEndChat,
      visible: !isSessionEnded,
      confirmMessage: '상담을 종료하시겠습니까?',
      className: 'danger'
    },
    {
      id: 'clear',
      icon: '🧹',
      label: '대화 기록 삭제',
      description: '모든 대화 내용을 삭제',
      action: onClearHistory,
      visible: true,
      confirmMessage: '모든 대화 기록을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.',
      className: 'warning'
    },
    {
      id: 'download',
      icon: '💾',
      label: '대화 기록 저장',
      description: '현재까지의 대화를 텍스트 파일로 저장',
      action: () => downloadChatHistory(),
      visible: true
    },
    {
      id: 'shortcuts',
      icon: '⚡',
      label: '단축키 보기',
      description: '키보드 단축키 안내',
      action: () => showShortcuts(),
      visible: true
    },
    {
      id: 'help',
      icon: '❓',
      label: '도움말',
      description: '사용법 및 FAQ',
      action: () => showHelp(),
      visible: true
    }
  ];

  /**
   * 메뉴 아이템 클릭 핸들러
   */
  const handleMenuClick = (item) => {
    if (item.confirmMessage) {
      setShowConfirm(item);
    } else {
      item.action();
      onClose();
    }
  };

  /**
   * 확인 다이얼로그 핸들러
   */
  const handleConfirm = () => {
    if (showConfirm && showConfirm.action) {
      showConfirm.action();
    }
    setShowConfirm(null);
    onClose();
  };

  /**
   * 대화 기록 다운로드
   */
  const downloadChatHistory = () => {
    try {
      const history = JSON.parse(localStorage.getItem('chat_history') || '[]');
      const text = history
        .map(msg => `[${msg.role.toUpperCase()}] ${msg.content}`)
        .join('\n\n');
      
      const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `hi-care-chat-${new Date().toISOString().slice(0, 10)}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('[메뉴] 대화 기록 다운로드 완료');
    } catch (error) {
      console.error('[메뉴] 다운로드 오류:', error);
      alert('다운로드 중 오류가 발생했습니다.');
    }
  };

  /**
   * 단축키 안내 표시
   */
  const showShortcuts = () => {
    const shortcuts = [
      'Enter: 메시지 전송',
      'Shift + Enter: 줄바꿈',
      'Ctrl + K: 메뉴 열기/닫기',
      'Ctrl + L: 대화 기록 삭제',
      'Esc: 모달 닫기'
    ];
    
    alert('🔧 키보드 단축키\n\n' + shortcuts.join('\n'));
  };

  /**
   * 도움말 표시
   */
  const showHelp = () => {
    const help = [
      '💬 Hi-Care AI 상담봇 사용법',
      '',
      '1. 질문을 입력창에 작성하세요',
      '2. Enter 키로 전송하거나 📤 버튼을 클릭하세요',
      '3. 추천 질문을 클릭하여 빠르게 입력할 수 있습니다',
      '4. 감정 분석 결과를 통해 맞춤형 답변을 받습니다',
      '',
      '📞 고객센터: 1588-1234',
      '⏰ 운영시간: 평일 9:00-18:00'
    ];
    
    alert(help.join('\n'));
  };

  return (
    <>
      <div className="quick-menu-overlay" onClick={onClose}>
        <div className="quick-menu" onClick={(e) => e.stopPropagation()}>
          <div className="menu-header">
            <h3>빠른 메뉴</h3>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
          
          <div className="menu-items">
            {menuItems
              .filter(item => item.visible)
              .map((item) => (
                <MenuItem
                  key={item.id}
                  item={item}
                  onClick={() => handleMenuClick(item)}
                />
              ))}
          </div>

          <div className="menu-footer">
            <small>상담 중 언제든 메뉴를 이용하세요</small>
          </div>
        </div>
      </div>

      {/* 확인 다이얼로그 */}
      {showConfirm && (
        <ConfirmDialog
          message={showConfirm.confirmMessage}
          onConfirm={handleConfirm}
          onCancel={() => setShowConfirm(null)}
          type={showConfirm.className}
        />
      )}
    </>
  );
}

/**
 * 메뉴 아이템 컴포넌트
 * @param {Object} item - 메뉴 아이템 객체
 * @param {Function} onClick - 클릭 핸들러
 */
function MenuItem({ item, onClick }) {
  return (
    <button
      className={`menu-item ${item.className || ''}`}
      onClick={onClick}
      title={item.description}
    >
      <span className="menu-icon">{item.icon}</span>
      <div className="menu-content">
        <span className="menu-label">{item.label}</span>
        <span className="menu-description">{item.description}</span>
      </div>
    </button>
  );
}

/**
 * 확인 다이얼로그 컴포넌트
 * @param {string} message - 확인 메시지
 * @param {Function} onConfirm - 확인 핸들러
 * @param {Function} onCancel - 취소 핸들러
 * @param {string} type - 다이얼로그 타입 (danger, warning)
 */
function ConfirmDialog({ message, onConfirm, onCancel, type = 'default' }) {
  return (
    <div className="confirm-dialog-overlay">
      <div className={`confirm-dialog ${type}`}>
        <div className="dialog-icon">
          {type === 'danger' ? '⚠️' : type === 'warning' ? '🔔' : '❓'}
        </div>
        <div className="dialog-message">
          {message.split('\n').map((line, index) => (
            <div key={index}>{line}</div>
          ))}
        </div>
        <div className="dialog-actions">
          <button onClick={onCancel} className="cancel-btn">
            취소
          </button>
          <button onClick={onConfirm} className={`confirm-btn ${type}`}>
            {type === 'danger' ? '종료' : type === 'warning' ? '삭제' : '확인'}
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * 플로팅 퀵 메뉴 버튼 (항상 표시)
 * @param {Function} onOpen - 메뉴 열기 핸들러
 */
export function FloatingQuickMenuButton({ onOpen }) {
  return (
    <button
      className="floating-quick-menu-btn"
      onClick={onOpen}
      title="빠른 메뉴 (Ctrl+K)"
    >
      ⚙️
    </button>
  );
}

export default QuickMenu; 