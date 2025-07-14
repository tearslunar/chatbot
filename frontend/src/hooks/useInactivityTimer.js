import { useEffect, useRef } from 'react';
import { useChatContext } from '../context/ChatContext';

export function useInactivityTimer() {
  const { state, actions } = useChatContext();
  const { isSessionEnded, showInactivityWarning, lastActivityTime } = state;
  const timerRef = useRef(null);
  const countdownRef = useRef(null);

  // 비활성 타이머 종료 처리
  const handleInactivityTimeout = () => {
    console.log('[비활성 타이머] 3분 경과로 상담을 자동 종료합니다.');
    actions.setSessionEnded(true);
    actions.setCurrentEmotion(null);
    actions.addMessage({ 
      role: 'bot', 
      content: '⏰ **3분간 대화가 없어 상담이 자동으로 종료되었습니다.** 서비스 이용 후기를 남겨주시면 더 나은 서비스 제공에 도움이 됩니다.' 
    });
    actions.setInactivityWarning(false);
    actions.setRemainingTime(0);
    
    // 자동 종료 후 바로 평점 입력창 표시
    setTimeout(() => {
      actions.setFeedbackModalOpen(true);
    }, 1000);
  };

  // 메인 비활성 타이머 관리
  useEffect(() => {
    // 상담이 종료된 상태에서는 타이머 작동하지 않음
    if (isSessionEnded) {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      actions.setInactivityWarning(false);
      return;
    }

    // 기존 타이머 정리
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    // 새로운 타이머 시작 (2분 30초 후 경고)
    timerRef.current = setTimeout(() => {
      actions.setInactivityWarning(true);
      actions.setRemainingTime(30); // 30초 경고
      
      // 추가 30초 후 자동 종료
      const finalTimer = setTimeout(() => {
        handleInactivityTimeout();
      }, 30000);
      
      timerRef.current = finalTimer;
    }, 150000); // 2분 30초

    // 컴포넌트 언마운트 시 타이머 정리
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
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