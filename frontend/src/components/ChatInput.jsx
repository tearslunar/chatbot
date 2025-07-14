import React, { useEffect, useCallback } from 'react';
import { useChatContext } from '../context/ChatContext';
import SuggestedQuestions from './SuggestedQuestions';
import { useDebounce } from '../hooks/useDebounce';
import { useThrottle } from '../hooks/useThrottle';
import faqData from '../assets/hi_faq.json';

const ChatInput = () => {
  const { state, actions } = useChatContext();
  const { 
    input, 
    isSessionEnded, 
    isComposing,
    sessionId,
    messages,
    model,
    isBotTyping,
    suggestedQuestions,
    autoCompleteFaqs
  } = state;

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // 메시지 전송 핸들러
  const handleSend = useCallback(async () => {
    if (!input.trim() || !model || isBotTyping) return;
    
    // 비활성 타이머 리셋
    actions.updateActivityTime();
    
    // 상담이 종료된 상태에서 새 메시지를 보내면 자동으로 재시작
    if (isSessionEnded) {
      actions.setSessionEnded(false);
      actions.setResolutionResult(null);
    }
    
    const userMsg = input;
    actions.addMessage({ role: 'user', content: userMsg });
    actions.setInput('');
    actions.setBotTyping(true);
    
    try {
      const res = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({ 
          message: userMsg, 
          model,
          session_id: sessionId,
          history: messages.map(msg => ({
            role: msg.role === 'bot' ? 'assistant' : msg.role,
            content: msg.content
          })).slice(-10)
        })
      });
      
      if (!res.ok) throw new Error('서버 오류');
      
      const data = await res.json();
      actions.addMessage({ 
        role: 'bot', 
        content: data.answer,
        emotion: data.emotion,
        escalation_needed: data.escalation_needed,
        recommended_faqs: data.recommended_faqs
      });
      
      // 자동 상담 종료 처리
      if (data.session_ended) {
        console.log('[자동 종료] 감정 강도 지속으로 상담이 자동 종료됩니다.');
        setTimeout(() => {
          actions.setSessionEnded(true);
          actions.setCurrentEmotion(null);
          actions.addMessage({ 
            role: 'bot', 
            content: '⚠️ **상담이 자동으로 종료되었습니다.** 상담사 연결을 위해 고객센터(1588-5656)로 연락해주세요.' 
          });
        }, 2000);
      }
    } catch (error) {
      console.error('API 호출 오류:', error);
      actions.addMessage({ 
        role: 'bot', 
        content: '서버와의 통신에 문제가 발생했습니다.' 
      });
    } finally {
      actions.setBotTyping(false);
    }
  }, [input, model, isBotTyping, isSessionEnded, sessionId, messages, actions, API_URL]);

  // 엔터키 전송
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend, isComposing]);

  // 상담사 연결 버튼
  const handleConnectAgent = useCallback(() => {
    actions.addMessage({ 
      role: 'bot', 
      content: '상담사 연결을 요청하셨습니다. 잠시만 기다려주세요.' 
    });
  }, [actions]);

  // 상담 재시작
  const handleRestartSession = useCallback(() => {
    actions.setSessionEnded(false);
    actions.setMessages([{ role: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }]);
    actions.setCurrentEmotion(null);
    actions.setSelectedPersona(null);
    actions.setResolutionResult(null);
  }, [actions]);

  // 추천 질문 선택 핸들러
  const handleSuggestionSelect = useCallback((question) => {
    actions.setInput(question);
    actions.setSuggestedQuestions([]);
  }, [actions]);

  // 자동완성 FAQ 선택
  const handleAutoCompleteSelect = useCallback((faq) => {
    actions.setInput(faq.question);
    actions.setAutoCompleteFaqs([]);
  }, [actions]);

  // 디바운스된 입력값으로 성능 최적화
  const debouncedInput = useDebounce(input, 300);

  // 스로틀된 검색 함수
  const throttledSearch = useThrottle((searchInput) => {
    if (!searchInput.trim()) {
      actions.setSuggestedQuestions([]);
      actions.setAutoCompleteFaqs([]);
      return;
    }

    const inputNorm = searchInput.toLowerCase().replace(/\s+/g, '');
    const inputWords = inputNorm.split(/\s+/).filter(Boolean);

    // 추천 질문 검색
    const matches = faqData.filter(faq => {
      const qNorm = faq.question.toLowerCase().replace(/\s+/g, '');
      return inputWords.some(word => qNorm.includes(word));
    }).map(faq => faq.question).slice(0, 10);

    actions.setSuggestedQuestions(matches);

    // 자동완성 FAQ 검색
    const autoMatches = faqData.filter(faq => 
      faq.question.includes(searchInput)
    ).slice(0, 5);
    
    actions.setAutoCompleteFaqs(autoMatches);
  }, 100);

  // 디바운스된 입력값 변경에 따른 검색 실행
  useEffect(() => {
    throttledSearch(debouncedInput);
  }, [debouncedInput, throttledSearch]);

  return (
    <div className="chat-input-outer">
      {/* 추천 질문: 입력창 바로 위에만 노출 */}
      {suggestedQuestions.length > 0 && (
        <SuggestedQuestions
          questions={suggestedQuestions}
          onSelect={handleSuggestionSelect}
        />
      )}
      {/* 입력 영역 */}
      <div className="chat-input-row">
        <div className="QuickMenu" onClick={() => actions.setQuickMenuOpen(!state.QuickMenuOpen)}>
          <div className="bar"></div>
          <div className="bar"></div>
          <div className="bar"></div>
        </div>
        
        <input
          type="text"
          placeholder={isSessionEnded ? "상담이 종료되었습니다." : "메시지를 입력하세요..."}
          value={input}
          onChange={e => actions.setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={() => actions.setComposing(true)}
          onCompositionEnd={() => actions.setComposing(false)}
          className="chat-input"
          disabled={isSessionEnded}
        />

        <button 
          onClick={handleSend} 
          className="send-btn" 
          disabled={isSessionEnded || isBotTyping}
        >
          전송
        </button>
        
        <button 
          onClick={handleConnectAgent} 
          className="agent-btn" 
          disabled={isSessionEnded}
        >
          상담사 연결
        </button>
        
        {isSessionEnded && (
          <button onClick={handleRestartSession} className="restart-btn">
            상담 재시작
          </button>
        )}
      </div>
    </div>
  );
};

export default ChatInput;