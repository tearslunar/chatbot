import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';
import ChatLoading from './components/ChatLoading';
import SuggestedQuestions from './components/SuggestedQuestions';
import PersonaSelector from './components/PersonaSelector';
import faqData from './assets/hi_faq.json';

// Vite 환경변수로 API URL 관리
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const MODEL_OPTIONS = [
  { label: 'Claude 3.7 sonnet', value: 'claude-3.7-sonnet' },
  { label: 'Claude 4.0 sonnet', value: 'claude-4.0-sonnet' },
  { label: 'Claude 3.5 Haiku', value: 'claude-3.5-haiku' },
  { label: 'Claude 3.7 Sonnet Extended Thinking', value: 'claude-3.7-sonnet-extended' },
];

const HISTORY_KEY = 'chat_history';

// 감정별 이모지와 색상
const EMOTION_CONFIG = {
  '긍정': { emoji: '😊', color: '#4CAF50', bgColor: '#E8F5E8' },
  '부정': { emoji: '😔', color: '#FF9800', bgColor: '#FFF3E0' },
  '불만': { emoji: '😤', color: '#F44336', bgColor: '#FFEBEE' },
  '분노': { emoji: '😠', color: '#D32F2F', bgColor: '#FFCDD2' },
  '불안': { emoji: '😰', color: '#9C27B0', bgColor: '#F3E5F5' },
  '중립': { emoji: '😐', color: '#607D8B', bgColor: '#ECEFF1' },
  '기쁨': { emoji: '😄', color: '#4CAF50', bgColor: '#E8F5E8' },
  '슬픔': { emoji: '😢', color: '#2196F3', bgColor: '#E3F2FD' },
  '놀람': { emoji: '😲', color: '#FF9800', bgColor: '#FFF3E0' }
};

function App() {
  // 대화 히스토리: {role: 'user'|'bot', content: string, emotion?: object} 배열
  const [messages, setMessages] = useState(() => {
    // localStorage에서 불러오기
    const saved = localStorage.getItem(HISTORY_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return [{ role: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }];
      }
    }
    return [{ role: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }];
  });
  const [input, setInput] = useState('');
  const [isComposing, setIsComposing] = useState(false); // IME 조합 상태
  const [model, setModel] = useState(MODEL_OPTIONS[0].value);
  const messagesEndRef = useRef(null);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [isSessionEnded, setIsSessionEnded] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [QuickMenuOpen, setQuickMenuOpen] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState(null);
  // const [emotionHistory, setEmotionHistory] = useState([]); // 미사용 state 주석 처리
  const [expandedFAQ, setExpandedFAQ] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('전체');
  const [selectedTag, setSelectedTag] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
  // 🌟 평점 시스템 상태 추가
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [resolutionResult, setResolutionResult] = useState(null);
  // const [fromSuggestion, setFromSuggestion] = useState(false); // 미사용 state 주석 처리
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  // 🚨 3분 비활성 타이머 상태 추가
  const [inactivityTimer, setInactivityTimer] = useState(null);
  const [lastActivityTime, setLastActivityTime] = useState(Date.now());
  const [showInactivityWarning, setShowInactivityWarning] = useState(false);
  const [remainingTime, setRemainingTime] = useState(180); // 3분 = 180초

  // 대화가 바뀔 때마다 localStorage에 저장
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
    
    // 최신 감정 설정
    if (emotions.length > 0) {
      setCurrentEmotion(emotions[emotions.length - 1]);
    }
  }, [messages]);

  // 🚨 3분 비활성 타이머 관리
  useEffect(() => {
    // 상담이 종료된 상태에서는 타이머 작동하지 않음
    if (isSessionEnded) {
      if (inactivityTimer) {
        clearTimeout(inactivityTimer);
        setInactivityTimer(null);
      }
      setShowInactivityWarning(false);
      return;
    }

    // 기존 타이머 정리
    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
    }

    // 새로운 타이머 시작
    const timer = setTimeout(() => {
      // 2분 30초 후 경고 표시 (30초 전 경고)
      setShowInactivityWarning(true);
      
      // 추가 30초 후 자동 종료
      const finalTimer = setTimeout(() => {
        handleInactivityTimeout();
      }, 30000); // 30초 추가 대기
      
      setInactivityTimer(finalTimer);
    }, 150000); // 2분 30초 (150초)

    setInactivityTimer(timer);
    setLastActivityTime(Date.now());

    // 컴포넌트 언마운트 시 타이머 정리
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [lastActivityTime, isSessionEnded]);

  // 경고 표시 중 남은 시간 카운트다운
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

  // 메시지 전송 핸들러
  const handleSend = async () => {
    if (!input.trim() || !model) return;
    
    // 🚨 비활성 타이머 리셋
    setLastActivityTime(Date.now());
    setShowInactivityWarning(false);
    setRemainingTime(180); // 3분으로 리셋
    
    // 상담이 종료된 상태에서 새 메시지를 보내면 자동으로 재시작
    if (isSessionEnded) {
      setIsSessionEnded(false);
      setResolutionResult(null); // 해소 분석 결과 초기화
    }
    
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsBotTyping(true);
    try {
      const res = await fetch(`${API_URL}/chat`, {
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
      if (!res.ok) throw new Error('서버 오류');
      const data = await res.json();
      setMessages(prev => ([...prev, { 
        role: 'bot', 
        content: data.answer,
        emotion: data.emotion,
        escalation_needed: data.escalation_needed
      }]));
      
      // 🚨 자동 상담 종료 처리
      if (data.session_ended) {
        console.log('[자동 종료] 감정 강도 지속으로 상담이 자동 종료됩니다.');
        setTimeout(() => {
          setIsSessionEnded(true);
          setCurrentEmotion(null);
          // 종료 후 상담사 연결 안내 강조
          setMessages(prev => [...prev, { 
            role: 'bot', 
            content: '⚠️ **상담이 자동으로 종료되었습니다.** 상담사 연결을 위해 고객센터(1588-5656)로 연락해주세요.' 
          }]);
        }, 2000); // 2초 후 종료 처리
      }
    } catch (error) {
      console.error('API 호출 오류:', error);
      setMessages(prev => ([...prev, { role: 'bot', content: '서버와의 통신에 문제가 발생했습니다.' }]));
    } finally {
      setIsBotTyping(false);
    }
  };

  // 엔터키 전송 (Shift+Enter는 줄바꿈, IME 조합 중에는 전송 X)
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSend();
    }
  };

  //상담 종료 핸들러
  const handleEndChat = () => {
    setIsModalOpen(true);
  };

  const handleEndChatCancel = () => {
    setIsModalOpen(false);
  };

  // IME 조합 시작/끝 감지
  const handleCompositionStart = () => setIsComposing(true);
  const handleCompositionEnd = () => setIsComposing(false);

  // 상담사 연결 버튼 클릭
  const handleConnectAgent = () => {
    setMessages(prev => [...prev, { role: 'bot', content: '상담사 연결을 요청하셨습니다. 잠시만 기다려주세요.' }]);
  };

  // 상담 종료 버튼 클릭 시 모달 오픈
  const handleEndChatConfirm = async () => {
    setIsSessionEnded(true);
    setIsModalOpen(false);
    setIsFeedbackModalOpen(true);
    setMessages(prev => ([...prev, { role: 'bot', content: '상담이 종료되었습니다. 언제든 다시 찾아주세요 ☀️' }]));
    // 상담 종료 시점에 해소 분석 API 호출
    try {
      const res = await fetch(`${API_URL}/end-session`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setResolutionResult(data);
        console.log('해소 분석 결과:', data);
      }
    } catch (e) {
      console.warn('해소 분석 API 호출 실패:', e);
    }
  };

  // 피드백 제출 핸들러
  const handleFeedbackSubmit = async () => {
    console.log('상담 종료 피드백:', feedback);
    console.log('상담 평점:', rating);
    
    // 🌟 평점과 피드백을 백엔드에 전송
    try {
      const res = await fetch(`${API_URL}/submit-rating`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          session_id: sessionId,
          rating: rating,
          feedback: feedback,
          timestamp: new Date().toISOString()
        })
      });
      
      if (res.ok) {
        console.log('평점 제출 성공');
        // 성공 메시지 표시 (선택적)
        setMessages(prev => [...prev, { 
          role: 'bot', 
          content: '소중한 평가를 해주셔서 감사합니다! 더 나은 서비스로 보답하겠습니다. 😊' 
        }]);
      } else {
        console.warn('평점 제출 실패:', res.status);
      }
    } catch (e) {
      console.warn('평점 제출 API 호출 실패:', e);
    }
    
    setIsFeedbackModalOpen(false);
    setFeedback('');
    setRating(0);
    setHoveredRating(0);
  };

  //빠른메뉴
  const handleQuickMenuToggle = () => {
    setQuickMenuOpen(!QuickMenuOpen);
  };

  // 상담 재시작
  const handleRestartSession = () => {
    setIsSessionEnded(false);
    setMessages([{ role: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }]);
    setCurrentEmotion(null);
    // setEmotionHistory([]); // 미사용 setter 주석 처리
    setSelectedPersona(null);
    setResolutionResult(null); // 감정 해소 분석 결과 초기화
  };

  // 히스토리 삭제(초기화)
  const handleClearHistory = async () => {
    setMessages([{ role: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }]);
    setIsSessionEnded(false);
    setCurrentEmotion(null);
    // setEmotionHistory([]); // 미사용 setter 주석 처리
    setSelectedPersona(null);
    setResolutionResult(null); // 감정 해소 분석 결과 초기화
    localStorage.removeItem(HISTORY_KEY);
    // 백엔드 감정 기록도 같이 초기화
    try {
      await fetch(`${API_URL}/emotion-history-reset`, { 
        method: 'POST',
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      });
    } catch (e) {
      // 네트워크 오류 등 무시
      console.warn('감정 기록 초기화 실패:', e);
    }
  };

  // 감정 표시 컴포넌트
  const EmotionIndicator = ({ emotion }) => {
    if (!emotion) return null;
    
    const config = EMOTION_CONFIG[emotion.emotion] || EMOTION_CONFIG['중립'];
    
    return (
      <div className="emotion-indicator" style={{ 
        backgroundColor: config.bgColor, 
        color: config.color,
        border: `1px solid ${config.color}`
      }}>
        <span className="emotion-emoji">{config.emoji}</span>
        <span className="emotion-text">{emotion.emotion}</span>
        <span className="emotion-intensity">강도: {emotion.intensity}/5</span>
      </div>
    );
  };

  // FAQ 토글 핸들러
  const handleToggleFAQ = idx => {
    setExpandedFAQ(expandedFAQ === idx ? null : idx);
  };

  // 카테고리/태그 목록 추출 (중복 제거) - useMemo로 메모화
  const allFaqs = useMemo(() => {
    return messages.find(msg => msg.role === 'bot' && msg.recommended_faqs)?.recommended_faqs || [];
  }, [messages]);

  const categories = useMemo(() => 
    ['전체', ...Array.from(new Set(allFaqs.map(faq => faq.category).filter(Boolean)))],
    [allFaqs]
  );

  const tags = useMemo(() => 
    Array.from(new Set(allFaqs.flatMap(faq => faq.tags || []).filter(Boolean))),
    [allFaqs]
  );

  // 필터링된 FAQ
  const filteredFaqs = useMemo(() => 
    allFaqs.filter(faq =>
      (selectedCategory === '전체' || faq.category === selectedCategory) &&
      (!selectedTag || (faq.tags && faq.tags.includes(selectedTag)))
    ),
    [allFaqs, selectedCategory, selectedTag]
  );

  // 추천 FAQ 렌더링 컴포넌트 수정
  const RecommendedFAQs = ({ faqs }) => {
    if (!faqs || faqs.length === 0) return null;
    return (
      <div className="recommended-faqs">
        <div className="faq-title">🔎 추천 FAQ</div>
        {/* 카테고리 탭 */}
        <div className="faq-category-tabs">
          {categories.map(cat => (
            <button
              key={cat}
              className={`faq-category-tab${selectedCategory === cat ? ' active' : ''}`}
              onClick={() => { setSelectedCategory(cat); setSelectedTag(null); }}
            >
              {cat}
            </button>
          ))}
        </div>
        {/* 태그 필터 */}
        <div className="faq-tag-filter-row">
          {tags.map(tag => (
            <span
              key={tag}
              className={`faq-tag-filter${selectedTag === tag ? ' active' : ''}`}
              onClick={() => setSelectedTag(selectedTag === tag ? null : tag)}
            >
              #{tag}
            </span>
          ))}
          {(selectedTag || selectedCategory !== '전체') && (
            <button className="faq-filter-reset" onClick={() => { setSelectedCategory('전체'); setSelectedTag(null); }}>
              필터 해제
            </button>
          )}
        </div>
        {/* 필터링된 FAQ 리스트 */}
        {filteredFaqs.length === 0 ? (
          <div className="faq-empty">해당 조건의 FAQ가 없습니다.</div>
        ) : filteredFaqs.map((faq, idx) => (
          <div key={idx} className="faq-item">
            <div className="faq-meta-row">
              <span className="faq-category">{faq.category}</span>
              <span className="faq-tags">
                {faq.tags && faq.tags.map((tag, i) => (
                  <span key={i} className="faq-tag">#{tag}</span>
                ))}
              </span>
            </div>
            <div className="faq-question" onClick={() => handleToggleFAQ(idx)}>
              <span>{faq.question}</span>
              <span className="faq-score">(유사도: {faq.score})</span>
              <span className="faq-toggle">{expandedFAQ === idx ? '▲' : '▼'}</span>
            </div>
            {expandedFAQ === idx && (
              <div className="faq-answer">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{faq.answer}</ReactMarkdown>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  // 입력창 위에 추천 질문 노출 (상위 3개)
  // const quickQuestions = allFaqs.slice(0, 3); // 미사용 변수 주석 처리

  // 입력값과 유사한 FAQ 질문 실시간 추천
  const [autoCompleteFaqs, setAutoCompleteFaqs] = useState([]);

  useEffect(() => {
    if (!input.trim()) {
      setAutoCompleteFaqs([]);
      return;
    }
    // 간단한 포함 검색 (실제 서비스는 백엔드에 실시간 요청 권장)
    const matches = allFaqs.filter(faq => faq.question.includes(input)).slice(0, 5);
    setAutoCompleteFaqs(matches);
  }, [input, allFaqs]);

  function normalize(str) {
    return str.toLowerCase().replace(/\s+/g, '');
  }

  const handleSuggestionSelect = (q) => {
    setInput(q);
    setSuggestedQuestions([]);
    // setFromSuggestion(true); // 미사용 setter 주석 처리
  };

  // 페르소나 선택 핸들러
  const handlePersonaSelect = async (persona) => {
    setSelectedPersona(persona);
    
    if (persona) {
      try {
        // 1. 페르소나 설정 API 호출
        const res = await fetch(`${API_URL}/set-persona`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
          },
          body: JSON.stringify({
            session_id: sessionId,
            persona_id: persona.ID
          })
        });
        
        if (res.ok) {
          console.log('페르소나 설정 완료:', persona);
          
          // 2. 페르소나 기반 인사말 생성 및 채팅에 추가
          const greetingRes = await fetch(`${API_URL}/get-persona-greeting`, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'ngrok-skip-browser-warning': 'true'
            },
            body: JSON.stringify({
              session_id: sessionId
            })
          });
          
          if (greetingRes.ok) {
            const greetingData = await greetingRes.json();
            if (greetingData.success) {
              // 기존 메시지에 페르소나 맞춤형 인사말 추가
              setMessages(prev => [...prev, { 
                role: 'bot', 
                content: greetingData.greeting 
              }]);
            }
          } else {
            console.error('페르소나 인사말 생성 실패');
          }
        } else {
          console.error('페르소나 설정 실패');
        }
      } catch (e) {
        console.error('페르소나 설정 실패:', e);
      }
    } else {
      // 페르소나 선택 해제 시 기본 메시지 추가
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: '페르소나 선택이 해제되었습니다. 일반적인 상담 모드로 전환됩니다. 😊\n\n무엇을 도와드릴까요?' 
      }]);
    }
  };

  useEffect(() => {
    // if (fromSuggestion) {
    //   setFromSuggestion(false);
    //   return;
    // } // 미사용 로직 주석 처리
    if (!input.trim()) {
      setSuggestedQuestions([]);
      return;
    }
    const inputNorm = normalize(input);
    const inputWords = inputNorm.split(/\s+/).filter(Boolean);
    const matches = faqData.filter(faq => {
      const qNorm = normalize(faq.question);
      return inputWords.some(word => qNorm.includes(word));
    }).map(faq => faq.question).slice(0, 10);
    setSuggestedQuestions(matches);
  }, [input]);

  // 비활성 타이머 종료 시 처리 (useCallback으로 메모화)
  const handleInactivityTimeout = useCallback(() => {
    console.log('[비활성 타이머] 3분 경과로 상담을 자동 종료합니다.');
    setIsSessionEnded(true);
    setCurrentEmotion(null);
    setMessages(prev => [...prev, { 
      role: 'bot', 
      content: '⏰ **3분간 대화가 없어 상담이 자동으로 종료되었습니다.** 서비스 이용 후기를 남겨주시면 더 나은 서비스 제공에 도움이 됩니다.' 
    }]);
    // 타이머 정리
    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
      setInactivityTimer(null);
    }
    setShowInactivityWarning(false);
    setRemainingTime(0);
    
    // 🌟 자동 종료 후 바로 평점 입력창 표시
    setTimeout(() => {
      setIsFeedbackModalOpen(true);
    }, 1000); // 1초 후 피드백 모달 표시
  }, [inactivityTimer]);

  return (
    <div className="chat-container">
      <div className="chat-header-row">
        <div className="modal-container">
          {isModalOpen && (
            <div className="modal-background">
              <div className="modal-content">
                <div className="modal-text">상담을 종료하겠습니까?</div>
                <p>어려움을 겪고 계신가요?<br />상담원이 도와드리겠습니다.<br />0000-0000</p>
                <div className="modal-buttons">
                  <button className="modal-button yes" onClick={handleEndChatConfirm}>네</button>
                  <button className="modal-button no" onClick={handleEndChatCancel}>아니오</button>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="chat-header">
          Hi-Care AI 챗봇
          {currentEmotion && <EmotionIndicator emotion={currentEmotion} />}
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {!isSessionEnded && <button className="end-button" onClick={handleEndChat}>상담 종료</button>}
          <button className="end-button" onClick={handleClearHistory}>히스토리 삭제</button>
        </div>
      </div>
      <div className="model-select-row">
        <label htmlFor="model-select">모델 선택: </label>
        <select
          id="model-select"
          value={model}
          onChange={e => setModel(e.target.value)}
        >
          {MODEL_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>
      
      <div style={{ padding: '0 20px' }}>
        <PersonaSelector 
          onPersonaSelect={handlePersonaSelect}
          selectedPersona={selectedPersona}
        />
      </div>
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
            {/* 사용자 메시지에만 감정 표시 */}
            {msg.role === 'user' && msg.emotion && <EmotionIndicator emotion={msg.emotion} />}
            {msg.escalation_needed && (
              <div className="escalation-warning">
                ⚠️ 상담사 연결이 권장됩니다
              </div>
            )}
            {/* 추천 FAQ는 마지막 bot 메시지에만 노출 */}
            {msg.role === 'bot' && idx === messages.length - 1 && msg.recommended_faqs && (
              <RecommendedFAQs faqs={msg.recommended_faqs} />
            )}
          </div>
        ))}
        {isBotTyping && <ChatLoading />}
        <div ref={messagesEndRef} />
      </div>
      {/* 입력창 위에 추천 질문 리스트 노출 */}
      <SuggestedQuestions
        questions={suggestedQuestions}
        onSelect={handleSuggestionSelect}
      />
      <div className="chat-input-row">
        <div className="QuickMenu" onClick={handleQuickMenuToggle}>
          {/* 햄버거 메뉴 아이콘 또는 닫기 아이콘으로 변경될 수 있는 부분 */}
          <div className="bar"></div>
          <div className="bar"></div>
          <div className="bar"></div>
        </div>
        <input
          type="text"
          placeholder={isSessionEnded ? "상담이 종료되었습니다." : "메시지를 입력하세요..."}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={handleCompositionStart}
          onCompositionEnd={handleCompositionEnd}
          className="chat-input"
          disabled={isSessionEnded}
        />
        {/* 입력창 아래에 자동완성 추천 질문 노출 */}
        {autoCompleteFaqs.length > 0 && (
          <div className="autocomplete-faqs" style={{ position: 'absolute', background: '#fff', border: '1px solid #eee', borderRadius: '8px', marginTop: '4px', zIndex: 10, width: '80%' }}>
            {autoCompleteFaqs.map((faq, idx) => (
              <div
                key={idx}
                className="autocomplete-faq-item"
                style={{ padding: '8px', cursor: 'pointer', borderBottom: '1px solid #f0f0f0' }}
                onClick={() => setInput(faq.question)}
              >
                {faq.question}
              </div>
            ))}
          </div>
        )}
        <button onClick={handleSend} className="send-btn" disabled={isSessionEnded}>전송</button>
        <button onClick={handleConnectAgent} className="agent-btn" disabled={isSessionEnded}>상담사 연결</button>
        {isSessionEnded && (
          <button onClick={handleRestartSession} className="restart-btn">상담 재시작</button>
        )}
      </div>
          {QuickMenuOpen && (
            <div className="QuickMenuContent">
              <button className="QuickMenuButton">
                <span className="quick-menu-icon">📋</span>
                <span>다이렉트<br />보험상품</span>
              </button>
              <button className="QuickMenuButton">
                <span className="quick-menu-icon">💬</span>
                <span>장기보험<br />채팅상담</span>
              </button>
              <button className="QuickMenuButton">
                <span className="quick-menu-icon">👤</span>
                <span>가입후기</span>
              </button>
              <button className="QuickMenuButton">
                <span className="quick-menu-icon">🏢</span>
                <span>손해보험<br />다이렉트 홈페이지</span>
              </button>
              <button className="QuickMenuButton">
                <span className="quick-menu-icon">🏠</span>
                <span>손해보험<br />홈페이지</span>
              </button>
              <button className="QuickMenuButton">
                <span className="quick-menu-icon">❓</span>
                <span>자주 묻는<br />질문</span>
              </button>
            </div>
    )}
      {/* 피드백 입력 모달 */}
      {isFeedbackModalOpen && (
        <div className="modal-background">
          <div className="modal-content" style={{ minWidth: 380, maxWidth: 450, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: 280 }}>
            <div className="modal-text" style={{ color: '#d2691e', marginBottom: 20, fontSize: '18px', fontWeight: 'bold' }}>상담은 어떠셨나요?</div>
            
            {/* 🌟 별점 입력 섹션 */}
            <div style={{ marginBottom: 20 }}>
              <div style={{ textAlign: 'center', marginBottom: 12, fontSize: '14px', color: '#666' }}>서비스 만족도를 평가해주세요</div>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    style={{
                      background: 'none',
                      border: 'none',
                      fontSize: '36px',
                      cursor: 'pointer',
                      color: (hoveredRating >= star || rating >= star) ? '#ffc107' : '#e0e0e0',
                      transition: 'color 0.2s ease',
                      padding: '4px'
                    }}
                    onMouseEnter={() => setHoveredRating(star)}
                    onMouseLeave={() => setHoveredRating(0)}
                    onClick={() => setRating(star)}
                  >
                    ★
                  </button>
                ))}
              </div>
              {rating > 0 && (
                <div style={{ textAlign: 'center', marginTop: '8px', fontSize: '14px', color: '#666' }}>
                  {rating === 1 && '매우 불만족'}
                  {rating === 2 && '불만족'}
                  {rating === 3 && '보통'}
                  {rating === 4 && '만족'}
                  {rating === 5 && '매우 만족'}
                </div>
              )}
            </div>

            {/* 텍스트 피드백 입력 */}
            <textarea
              value={feedback}
              onChange={e => setFeedback(e.target.value)}
              placeholder="개선점이나 의견을 자유롭게 입력해 주세요 (선택사항)"
              rows={4}
              style={{ width: '100%', minHeight: 80, marginBottom: 24, borderRadius: 8, border: '1px solid #ddd', padding: 12, fontSize: 15, background: '#fafafa', color: '#222', resize: 'none' }}
            />
            
            <div className="modal-buttons" style={{ justifyContent: 'center', width: '100%' }}>
              <button 
                className="modal-button yes" 
                onClick={handleFeedbackSubmit}
                disabled={rating === 0}
                style={{ 
                  opacity: rating === 0 ? 0.5 : 1,
                  cursor: rating === 0 ? 'not-allowed' : 'pointer'
                }}
              >
                제출하기
              </button>
              <button className="modal-button no" onClick={() => { 
                setIsFeedbackModalOpen(false); 
                setFeedback(''); 
                setRating(0);
                setHoveredRating(0);
              }}>건너뛰기</button>
            </div>
          </div>
        </div>
      )}
      {/* 상담 종료 시 해소 결과 알림 */}
      {resolutionResult && (
        <div style={{ background: resolutionResult.resolved ? '#e3fcec' : '#ffeaea', color: '#333', padding: '8px', borderRadius: '8px', margin: '12px 0', textAlign: 'center' }}>
          {resolutionResult.resolved ? '상담 종료 시점에 고객 감정이 해소된 것으로 분석되었습니다.' : '상담 종료 시점에도 고객 감정이 해소되지 않은 것으로 분석되었습니다.'}
        </div>
      )}

      {/* 🚨 비활성 경고 모달 */}
      {showInactivityWarning && (
        <div className="modal-background">
          <div className="modal-content" style={{ minWidth: 320, maxWidth: 400, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: 200, background: '#fff3cd', border: '2px solid #ffc107' }}>
            <div style={{ fontSize: '48px', marginBottom: 16 }}>⏰</div>
            <div className="modal-text" style={{ color: '#856404', marginBottom: 16, textAlign: 'center', fontWeight: 'bold' }}>
              비활성 상태 감지
            </div>
            <div style={{ color: '#856404', marginBottom: 20, textAlign: 'center', lineHeight: 1.5 }}>
              {remainingTime}초 후 상담이 자동으로 종료됩니다.<br/>
              메시지를 입력하시면 상담이 계속됩니다.
            </div>
            <div className="modal-buttons" style={{ justifyContent: 'center', width: '100%' }}>
              <button 
                className="modal-button yes" 
                onClick={() => {
                  setLastActivityTime(Date.now());
                  setShowInactivityWarning(false);
                  setRemainingTime(180);
                }}
                style={{ background: '#ffc107', border: 'none', color: '#000' }}
              >
                상담 계속하기
              </button>
              <button 
                className="modal-button no" 
                onClick={() => {
                  handleInactivityTimeout();
                }}
              >
                상담 종료
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
