/**
 * 세션 관리 컴포넌트
 * 세션 상태, 비활성 타이머, 자동 종료 등을 관리
 */

import React, { useState, useEffect, useCallback } from 'react';

/**
 * 세션 관리자 컴포넌트
 * @param {string} sessionId - 세션 ID
 * @param {boolean} isSessionEnded - 세션 종료 여부
 * @param {Function} onSessionEnd - 세션 종료 핸들러
 * @param {Function} onSessionRestart - 세션 재시작 핸들러
 * @param {number} inactivityTimeout - 비활성 타임아웃 (초, 기본: 180)
 */
function SessionManager({ 
  sessionId, 
  isSessionEnded, 
  onSessionEnd, 
  onSessionRestart,
  inactivityTimeout = 180 // 3분
}) {
  const [lastActivity, setLastActivity] = useState(Date.now());
  const [showInactivityWarning, setShowInactivityWarning] = useState(false);
  const [remainingTime, setRemainingTime] = useState(inactivityTimeout);
  const [sessionStartTime] = useState(Date.now());

  // 활동 감지 이벤트들 (메모화)
  const activityEvents = React.useMemo(() => 
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'], 
    []
  );

  // 활동 감지 및 타이머 리셋
  const resetInactivityTimer = useCallback(() => {
    setLastActivity(Date.now());
    setShowInactivityWarning(false);
    setRemainingTime(inactivityTimeout);
  }, [inactivityTimeout]);

  // 비활성 타이머 관리
  useEffect(() => {
    if (isSessionEnded) {
      return;
    }

    // 활동 이벤트 리스너 등록
    const handleActivity = () => resetInactivityTimer();
    
    activityEvents.forEach(event => {
      document.addEventListener(event, handleActivity, true);
    });

    // 타이머 설정
    const warningTime = inactivityTimeout - 30; // 30초 전 경고
    
    const warningTimer = setTimeout(() => {
      setShowInactivityWarning(true);
    }, warningTime * 1000);

    const endTimer = setTimeout(() => {
      if (onSessionEnd) {
        onSessionEnd();
      }
    }, inactivityTimeout * 1000);

    // 정리 함수
    return () => {
      activityEvents.forEach(event => {
        document.removeEventListener(event, handleActivity, true);
      });
      clearTimeout(warningTimer);
      clearTimeout(endTimer);
    };
  }, [lastActivity, isSessionEnded, inactivityTimeout, onSessionEnd, activityEvents, resetInactivityTimer]);

  // 경고 표시 중 카운트다운
  useEffect(() => {
    if (!showInactivityWarning) return;

    const countdown = setInterval(() => {
      setRemainingTime(prev => {
        if (prev <= 1) {
          clearInterval(countdown);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(countdown);
  }, [showInactivityWarning]);

  /**
   * 세션 통계 계산
   */
  const getSessionStats = () => {
    const duration = Math.floor((Date.now() - sessionStartTime) / 1000);
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    
    return {
      duration: `${minutes}분 ${seconds}초`,
      durationMinutes: minutes,
      sessionId: sessionId.slice(-8) // 마지막 8자리만
    };
  };

  const stats = getSessionStats();

  return (
    <div className="session-manager">
      {/* 세션 정보 표시 */}
      <div className="session-info">
        <div className="session-status">
          <span className={`status-indicator ${isSessionEnded ? 'ended' : 'active'}`}>
            {isSessionEnded ? '⭕' : '🟢'}
          </span>
          <span className="session-text">
            {isSessionEnded ? '세션 종료' : '상담 중'}
          </span>
        </div>
        
        <div className="session-details">
          <span className="session-duration">⏱️ {stats.duration}</span>
          <span className="session-id">📋 {stats.sessionId}</span>
        </div>
      </div>

      {/* 비활성 경고 모달 */}
      {showInactivityWarning && !isSessionEnded && (
        <InactivityWarning
          remainingTime={remainingTime}
          onContinue={resetInactivityTimer}
          onEnd={onSessionEnd}
        />
      )}

      {/* 세션 종료 후 액션 */}
      {isSessionEnded && (
        <SessionEndActions
          stats={stats}
          onRestart={onSessionRestart}
        />
      )}
    </div>
  );
}

/**
 * 비활성 경고 컴포넌트
 * @param {number} remainingTime - 남은 시간 (초)
 * @param {Function} onContinue - 계속하기 핸들러
 * @param {Function} onEnd - 종료 핸들러
 */
function InactivityWarning({ remainingTime, onContinue, onEnd }) {
  return (
    <div className="inactivity-warning-overlay">
      <div className="inactivity-warning">
        <div className="warning-icon">⚠️</div>
        <h3>세션 만료 경고</h3>
        <p>
          장시간 활동이 없어 <strong>{remainingTime}초</strong> 후 
          자동으로 상담이 종료됩니다.
        </p>
        <div className="warning-actions">
          <button 
            onClick={onContinue}
            className="continue-btn"
          >
            계속하기
          </button>
          <button 
            onClick={onEnd}
            className="end-btn"
          >
            종료하기
          </button>
        </div>
        <div className="countdown-bar">
          <div 
            className="countdown-fill"
            style={{
              width: `${(remainingTime / 30) * 100}%`,
              transition: 'width 1s linear'
            }}
          />
        </div>
      </div>
    </div>
  );
}

/**
 * 세션 종료 후 액션 컴포넌트
 * @param {Object} stats - 세션 통계
 * @param {Function} onRestart - 재시작 핸들러
 */
function SessionEndActions({ stats, onRestart }) {
  return (
    <div className="session-end-actions">
      <div className="session-summary">
        <h4>상담 요약</h4>
        <div className="summary-stats">
          <div className="stat">
            <span className="stat-label">상담 시간:</span>
            <span className="stat-value">{stats.duration}</span>
          </div>
          <div className="stat">
            <span className="stat-label">세션 ID:</span>
            <span className="stat-value">{stats.sessionId}</span>
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button 
          onClick={onRestart}
          className="restart-btn"
        >
          🔄 새 상담 시작
        </button>
      </div>

      <div className="session-tips">
        <p>💡 상담이 도움이 되셨나요? 피드백을 남겨주세요!</p>
      </div>
    </div>
  );
}

/**
 * 세션 상태 표시기 컴포넌트 (간단한 버전)
 * @param {boolean} isActive - 활성 상태
 * @param {number} duration - 지속 시간 (초)
 */
export function SessionStatus({ isActive, duration }) {
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`session-status-simple ${isActive ? 'active' : 'inactive'}`}>
      <span className="status-dot"></span>
      <span className="status-text">
        {isActive ? '상담 중' : '종료됨'}
      </span>
      <span className="status-duration">
        {formatDuration(duration)}
      </span>
    </div>
  );
}

export default SessionManager; 