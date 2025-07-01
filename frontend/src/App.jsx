import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';
import ChatLoading from './components/ChatLoading';

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
  const [emotionHistory, setEmotionHistory] = useState([]);
  const [expandedFAQ, setExpandedFAQ] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('전체');
  const [selectedTag, setSelectedTag] = useState(null);

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
    setEmotionHistory(emotions);
    
    // 최신 감정 설정
    if (emotions.length > 0) {
      setCurrentEmotion(emotions[emotions.length - 1]);
    }
  }, [messages]);

  // 메시지 전송 핸들러
  const handleSend = async () => {
    if (!input.trim() || !model || isSessionEnded) return;
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsBotTyping(true);
    try {
      const res = await fetch('https://chatbot-5avk.onrender.com/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, model })
      });
      if (!res.ok) throw new Error('서버 오류');
      const data = await res.json();
      setMessages(prev => ([...prev, { 
        role: 'bot', 
        content: data.answer,
        emotion: data.emotion,
        escalation_needed: data.escalation_needed
      }]));
    } catch (err) {
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
  const handleEndChatConfirm = () => {
    setIsSessionEnded(true);
    setIsModalOpen(false);
    setMessages(prev => ([...prev, { role: 'bot', content: '상담이 종료되었습니다. 언제든 다시 찾아주세요 ☀️' }]));
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
    setEmotionHistory([]);
  };

  // 히스토리 삭제(초기화)
  const handleClearHistory = () => {
    setMessages([{ role: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }]);
    setIsSessionEnded(false);
    setCurrentEmotion(null);
    setEmotionHistory([]);
    localStorage.removeItem(HISTORY_KEY);
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

  // 카테고리/태그 목록 추출 (중복 제거)
  const allFaqs = messages.find(msg => msg.role === 'bot' && msg.recommended_faqs)?.recommended_faqs || [];
  const categories = ['전체', ...Array.from(new Set(allFaqs.map(faq => faq.category).filter(Boolean)))];
  const tags = Array.from(new Set(allFaqs.flatMap(faq => faq.tags || []).filter(Boolean)));

  // 필터링된 FAQ
  const filteredFaqs = allFaqs.filter(faq =>
    (selectedCategory === '전체' || faq.category === selectedCategory) &&
    (!selectedTag || (faq.tags && faq.tags.includes(selectedTag)))
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
                <ReactMarkdown>{faq.answer}</ReactMarkdown>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

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
          현대해상 AI 챗봇
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
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <ReactMarkdown>{msg.content}</ReactMarkdown>
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
      <div className="chat-input-row">
        <div class="QuickMenu" onClick={handleQuickMenuToggle}>
          <div class="bar"></div>
          <div class="bar"></div>
          <div class="bar"></div>
          {QuickMenuOpen && (
            <div class="QuickMenuContent" >
              <button className="QuickMenuButton" >임시</button>
              <button className="QuickMenuButton" >임시</button>
              <button className="QuickMenuButton" >임시</button>
            </div>)}
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
        <button onClick={handleSend} className="send-btn" disabled={isSessionEnded}>전송</button>
        <button onClick={handleConnectAgent} className="agent-btn" disabled={isSessionEnded}>상담사 연결</button>
        {isSessionEnded && (
          <button onClick={handleRestartSession} className="restart-btn">상담 재시작</button>
        )}
      </div>
    </div>
  );
}

export default App;
