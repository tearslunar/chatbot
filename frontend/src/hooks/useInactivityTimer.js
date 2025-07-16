import { useEffect, useRef } from 'react';
import { useChatContext } from '../context/ChatContext';

export function useInactivityTimer() {
  const { state, actions } = useChatContext();
  const { isSessionEnded, showInactivityWarning, lastActivityTime } = state;
  const timerRef = useRef(null);
  const countdownRef = useRef(null);

  // 🚨 자동 종료 완전 비활성화 - 비활성 타이머 더 이상 작동하지 않음
  const handleInactivityTimeout = () => {
    // 아무것도 하지 않음 - 자동 종료 비활성화
    console.log('[비활성 타이머] 자동 종료 기능이 비활성화되었습니다.');
  };

  // 메인 비활성 타이머 관리 - 완전 비활성화
  useEffect(() => {
    // 🚨 자동 종료 완전 비활성화 - 타이머 설정하지 않음
    return;
  }, [lastActivityTime, isSessionEnded]);

  // 경고 표시 중 남은 시간 카운트다운
  useEffect(() => {
    if (!showInactivityWarning) {
      if (countdownRef.current) {
        clearInterval(countdownRef.current);
        countdownRef.current = null;
      }
      return;
    }

    countdownRef.current = setInterval(() => {
      actions.setRemainingTime(prev => {
        if (prev <= 1) {
          clearInterval(countdownRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (countdownRef.current) {
        clearInterval(countdownRef.current);
      }
    };
  }, [showInactivityWarning]);

  // 타이머 정리
  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, []);
}