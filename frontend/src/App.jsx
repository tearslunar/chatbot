import { useState, useRef, useEffect } from 'react';
import './App.css';
import ChatLoading from './components/ChatLoading';

const MODEL_OPTIONS = [
  { label: 'Claude 3.7 sonnet', value: 'claude-3.7-sonnet' },
  { label: 'Claude 4.0 sonnet', value: 'claude-4.0-sonnet' },
  { label: 'Claude 3.5 Haiku', value: 'claude-3.5-haiku' },
  { label: 'Claude 3.7 Sonnet Extended Thinking', value: 'claude-3.7-sonnet-extended' },
];

const HISTORY_KEY = 'chat_history';

function App() {
  // 대화 히스토리: {role: 'user'|'bot', content: string} 배열
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

  // 대화가 바뀔 때마다 localStorage에 저장
  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(messages));
  }, [messages]);

  // 스크롤 하단 고정
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isBotTyping]);

  // 메시지 전송 핸들러
  const handleSend = async () => {
    if (!input.trim() || !model || isSessionEnded) return;
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsBotTyping(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, model })
      });
      if (!res.ok) throw new Error('서버 오류');
      const data = await res.json();
      setMessages(prev => ([...prev, { role: 'bot', content: data.answer }]));
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
  };

  // 히스토리 삭제(초기화)
  const handleClearHistory = () => {
    setMessages([{ role: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }]);
    setIsSessionEnded(false);
    localStorage.removeItem(HISTORY_KEY);
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
        <div className="chat-header">현대해상 AI 챗봇</div>
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
          <div key={idx} className={`chat-message ${msg.role}`}>{msg.content}</div>
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
