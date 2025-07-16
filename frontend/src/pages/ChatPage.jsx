/**
 * 메인 채팅 페이지 컴포넌트
 * 채팅 인터페이스와 주요 기능들을 담당
 */

import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import ChatLoading from '../components/ChatLoading';
import SuggestedQuestions from '../components/SuggestedQuestions';
import PersonaSelector from '../components/PersonaSelector';
import EmotionIndicator from '../components/EmotionIndicator';
import RecommendedFAQs from '../components/RecommendedFAQs';
import SessionManager from '../components/SessionManager';
import FeedbackModal from '../components/FeedbackModal';
import QuickMenu from '../components/QuickMenu';

// import faqData from '../assets/hi_faq.json'; // 미사용 import 주석 처리

// 설정 상수
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const HISTORY_KEY = 'chat_history';

const MODEL_OPTIONS = [
  { label: 'Claude 3.7 sonnet', value: 'claude-3.7-sonnet' },
  { label: 'Claude 4.0 sonnet', value: 'claude-4.0-sonnet' },
  { label: 'Claude 3.5 Haiku', value: 'claude-3.5-haiku' },
  { label: 'Claude 3.7 Sonnet Extended Thinking', value: 'claude-3.7-sonnet-extended' },
];

/**
 * 채팅 페이지 메인 컴포넌트
 */
function ChatPage() {
  // 상태 관리
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem(HISTORY_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return [{ role: 'bot', content: '안녕하세요! Hi-Care 상담봇입니다. 무엇을 도와드릴까요? 😊' }];
      }
    }
    return [{ role: 'bot', content: '안녕하세요! Hi-Care 상담봇입니다. 무엇을 도와드릴까요? 😊' }];
  });

  const [input, setInput] = useState('');
  const [model, setModel] = useState(MODEL_OPTIONS[0].value);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [isComposing, setIsComposing] = useState(false);
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  // 모달 및 UI 상태
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [QuickMenuOpen, setQuickMenuOpen] = useState(false);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);

  // 감정 및 FAQ 상태
  const [currentEmotion, setCurrentEmotion] = useState(null);
  // const [emotionHistory, setEmotionHistory] = useState([]); // 미사용 state 주석 처리
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);

  // 세션 관리 상태
  const [isSessionEnded, setIsSessionEnded] = useState(false);
  // const [resolutionResult, setResolutionResult] = useState(null); // 미사용 state 주석 처리

  // Refs
  const messagesEndRef = useRef(null);

  // 대화 히스토리 저장
  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(messages));
  }, [messages]);

  // 스크롤 하단 고정
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isBotTyping]);

  // 감정 히스토리 업데이트
  useEffect(() => {
    const emotions = messages
      .filter(msg => msg.emotion)
      .map(msg => msg.emotion);
    // setEmotionHistory(emotions); // 미사용 setter 주석 처리
    
    if (emotions.length > 0) {
      setCurrentEmotion(emotions[emotions.length - 1]);
    }
  }, [messages]);

  /**
   * 메시지 전송 핸들러
   */
  const handleSend = async () => {
    if (!input.trim() || !model || isBotTyping) return;
    
    // 상담이 종료된 상태에서 새 메시지를 보내면 자동으로 재시작
    if (isSessionEnded) {
      setIsSessionEnded(false);
      // setResolutionResult(null); // 미사용 setter 주석 처리
    }
    
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsBotTyping(true);

    try {
      const response = await fetch(`${API_URL}/chat/message`, {
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
          })).slice(-10) // 최근 10개 메시지만 전송
        })
      });

      if (!response.ok) {
        throw new Error(`서버 오류: ${response.status}`);
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: data.answer,
        emotion: data.emotion,
        entities: data.entities,
        recommended_faqs: data.recommended_faqs
      }]);

      // 추천 질문 업데이트
      if (data.recommended_faqs && data.recommended_faqs.length > 0) {
        setSuggestedQuestions(data.recommended_faqs.slice(0, 3));
      }

      // 🚨 자동 세션 종료 비활성화 - session_ended 무시
      // if (data.session_ended) {
      //   setIsSessionEnded(true);
      //   setIsFeedbackModalOpen(true);
      // }

    } catch (error) {
      console.error('[채팅] 메시지 전송 오류:', error);
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: '죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요. 🙏',
        error: true
      }]);
    } finally {
      setIsBotTyping(false);
    }
  };

  /**
   * 키보드 입력 핸들러
   */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSend();
    }
  };

  /**
   * 상담 종료 핸들러
   */
  const handleEndChat = () => {
    setIsModalOpen(true);
  };

  /**
   * 상담 종료 취소
   */
  const handleEndChatCancel = () => {
    setIsModalOpen(false);
  };

  /**
   * 상담 종료 확인
   */
  const handleEndChatConfirm = async () => {
    try {
      await fetch(`${API_URL}/chat/end-session`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({ session_id: sessionId })
      });

      setIsSessionEnded(true);
      setIsModalOpen(false);
      setIsFeedbackModalOpen(true);
      
      // 종료 메시지 추가
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: '상담이 종료되었습니다. 이용해주셔서 감사합니다! 😊 궁금한 점이 더 있으시면 언제든 다시 문의해주세요.',
        isSystemMessage: true
      }]);

    } catch (error) {
      console.error('[세션] 종료 오류:', error);
    }
  };

  /**
   * 세션 재시작
   */
  const handleRestartSession = () => {
    setIsSessionEnded(false);
    // setResolutionResult(null); // 미사용 setter 주석 처리
    setIsFeedbackModalOpen(false);
    setMessages(prev => [...prev, { 
      role: 'bot', 
      content: '새로운 상담을 시작합니다. 무엇을 도와드릴까요? 😊'
    }]);
  };

  /**
   * 히스토리 삭제
   */
  const handleClearHistory = async () => {
    try {
      setMessages([{ role: 'bot', content: '대화 기록이 삭제되었습니다. 새로운 상담을 시작해주세요! 😊' }]);
      setCurrentEmotion(null);
      // setEmotionHistory([]); // 미사용 setter 주석 처리
      setSuggestedQuestions([]);
      setIsSessionEnded(false);
      // setResolutionResult(null); // 미사용 setter 주석 처리
      localStorage.removeItem(HISTORY_KEY);
    } catch (error) {
      console.error('[히스토리] 삭제 오류:', error);
    }
  };

  /**
   * 추천 질문 선택 핸들러
   */
  const handleSuggestionSelect = (question) => {
    setInput(question);
    setSuggestedQuestions([]);
  };

  /**
   * 페르소나 선택 핸들러
   */
  const handlePersonaSelect = async (persona) => {
    try {
      setSelectedPersona(persona);
      
      // 페르소나 설정 API 호출
      await fetch(`${API_URL}/persona/set`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          session_id: sessionId,
          persona_id: persona.id
        })
      });

      // 페르소나 기반 인사말 요청
      const greetingResponse = await fetch(`${API_URL}/persona/greeting`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          session_id: sessionId
        })
      });

      if (greetingResponse.ok) {
        const greetingData = await greetingResponse.json();
        if (greetingData.success && greetingData.greeting) {
          setMessages(prev => [...prev, { 
            role: 'bot', 
            content: greetingData.greeting,
            isPersonaGreeting: true
          }]);
        }
      }

    } catch (error) {
      console.error('[페르소나] 선택 오류:', error);
    }
  };

  // IME 입력 핸들러
  const handleCompositionStart = () => setIsComposing(true);
  const handleCompositionEnd = () => setIsComposing(false);

  return (
    <div className="chat-container">
      {/* 헤더 */}
      <div className="chat-header">
        <div className="header-left">
          <h1>💬 Hi-Care AI 상담봇</h1>
          {selectedPersona && (
            <div className="selected-persona">
              <span>👤 {selectedPersona.name}님으로 상담 중</span>
            </div>
          )}
        </div>
        <div className="header-right">
          <select 
            value={model} 
            onChange={(e) => setModel(e.target.value)}
            className="model-selector"
            disabled={isBotTyping}
          >
            {MODEL_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <button 
            onClick={() => setQuickMenuOpen(!QuickMenuOpen)}
            className="quick-menu-btn"
            title="빠른 메뉴"
          >
            ⚙️
          </button>
        </div>
      </div>

      {/* 감정 표시기 */}
      {currentEmotion && (
        <EmotionIndicator emotion={currentEmotion} />
      )}

      {/* 빠른 메뉴 */}
      {QuickMenuOpen && (
        <QuickMenu
          onEndChat={handleEndChat}
          onClearHistory={handleClearHistory}
          onRestartSession={handleRestartSession}
          onClose={() => setQuickMenuOpen(false)}
          isSessionEnded={isSessionEnded}
        />
      )}

      {/* 메시지 영역 */}
      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.role === 'bot' ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              ) : (
                <span>{msg.content}</span>
              )}
            </div>
            
            {msg.emotion && (
              <div className="message-emotion">
                <EmotionIndicator emotion={msg.emotion} compact />
              </div>
            )}

            {msg.recommended_faqs && msg.recommended_faqs.length > 0 && (
              <RecommendedFAQs 
                faqs={msg.recommended_faqs}
                onQuestionSelect={handleSuggestionSelect}
              />
            )}
          </div>
        ))}

        {isBotTyping && <ChatLoading />}
        <div ref={messagesEndRef} />
      </div>

      {/* 페르소나 선택기 */}
      {!selectedPersona && !isSessionEnded && (
        <PersonaSelector onPersonaSelect={handlePersonaSelect} />
      )}

      {/* 입력 영역 */}
      <div className={`input-container ${isSessionEnded ? 'disabled' : ''}`}>
        <div className="input-wrapper">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onCompositionStart={handleCompositionStart}
            onCompositionEnd={handleCompositionEnd}
            placeholder={isSessionEnded ? "상담이 종료되었습니다." : "메시지를 입력하세요..."}
            disabled={isSessionEnded || isBotTyping}
            rows={1}
            style={{ 
              resize: 'none',
              minHeight: '40px',
              maxHeight: '120px'
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isBotTyping || isSessionEnded}
            className="send-button"
            title="전송 (Enter)"
          >
            {isBotTyping ? '⏳' : '📤'}
          </button>
        </div>
      </div>

      {/* 세션 관리 */}
      <SessionManager
        sessionId={sessionId}
        isSessionEnded={isSessionEnded}
        onSessionEnd={handleEndChat}
        onSessionRestart={handleRestartSession}
      />

      {/* 모달들 */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>상담 종료</h3>
            <p>정말로 상담을 종료하시겠습니까?</p>
            <div className="modal-actions">
              <button onClick={handleEndChatCancel} className="cancel-btn">
                취소
              </button>
              <button onClick={handleEndChatConfirm} className="confirm-btn">
                종료
              </button>
            </div>
          </div>
        </div>
      )}

      {isFeedbackModalOpen && (
        <FeedbackModal
          sessionId={sessionId}
          onClose={() => setIsFeedbackModalOpen(false)}
          onRestart={handleRestartSession}
        />
      )}
    </div>
  );
}

export default ChatPage; 