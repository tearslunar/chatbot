import React from 'react';
import { useChatContext } from '../context/ChatContext';
import EmotionIndicator from './EmotionIndicator';

const ChatHeader = () => {
  const { state, actions } = useChatContext();
  const { currentEmotion, isSessionEnded } = state;

  const handleDevMode = () => {
    actions.setDevMode(!state.DevMode);
  }

  const handleEndChat = () => {
    actions.setModalOpen(true);
  };

  const handleClearHistory = async () => {
    actions.resetChat();
    
    // 백엔드 감정 기록도 초기화
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    try {
      await fetch(`${API_URL}/emotion-history-reset`, { 
        method: 'POST',
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      });
    } catch (e) {
      console.warn('감정 기록 초기화 실패:', e);
    }
  };

  return (
    <div className="chat-header-row">
      <div className="chat-header">
        Hi-Care AI 챗봇
        {currentEmotion && <EmotionIndicator emotion={currentEmotion} />}
      </div>
      <button className='DevMode' onClick={handleDevMode}>Dev</button>
      <div style={{ display: 'flex', gap: '8px' }}>
        {!isSessionEnded && (
          <button className="end-button" onClick={handleEndChat}>
            상담 종료
          </button>
        )}
        <button className="end-button" onClick={handleClearHistory}>
          히스토리 삭제
        </button>
      </div>
    </div>
  );
};

export default ChatHeader;