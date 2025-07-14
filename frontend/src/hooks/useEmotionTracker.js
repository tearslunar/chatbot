import { useEffect } from 'react';
import { useChatContext } from '../context/ChatContext';

export function useEmotionTracker() {
  const { state, actions } = useChatContext();
  const { messages } = state;

  // 감정 추적 및 업데이트
  useEffect(() => {
    const emotions = messages
      .filter(msg => msg.emotion)
      .map(msg => msg.emotion);
    
    // 최신 감정 설정
    if (emotions.length > 0) {
      const latestEmotion = emotions[emotions.length - 1];
      actions.setCurrentEmotion(latestEmotion);
    }
  }, [messages, actions]);
}