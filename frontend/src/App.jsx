import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  // 대화 히스토리: {role: 'user'|'bot', content: string} 배열
  const [messages, setMessages] = useState([
    { role: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }
  ]);
  const [input, setInput] = useState('');
  const [isComposing, setIsComposing] = useState(false); // IME 조합 상태
  const [model, setModel] = useState(''); // 선택된 모델
  const [modelOptions, setModelOptions] = useState([]); // 실제 모델 목록
  const messagesEndRef = useRef(null);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 모델 목록 불러오기
  useEffect(() => {
    fetch('http://127.0.0.1:8000/models')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setModelOptions(data);
          setModel(data[0].name);
        } else {
          setModelOptions([]);
        }
      })
      .catch(() => setModelOptions([]));
  }, []);

  // 스크롤 하단 고정
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 메시지 전송 핸들러
  const handleSend = async () => {
    if (!input.trim() || !model) return;
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsBotTyping(true);
    setMessages(prev => [...prev, { role: 'bot', content: '챗봇이 답변을 작성 중입니다...' }]);
    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, model })
      });
      if (!res.ok) throw new Error('서버 오류');
      const data = await res.json();
      setMessages(prev => {
        // 마지막 메시지가 '챗봇이 답변을 작성 중입니다...'이면 교체
        const last = prev[prev.length - 1];
        if (last && last.role === 'bot' && last.content === '챗봇이 답변을 작성 중입니다...') {
          return [...prev.slice(0, -1), { role: 'bot', content: data.answer }];
        }
        return [...prev, { role: 'bot', content: data.answer }];
      });
    } catch (err) {
      setMessages(prev => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'bot' && last.content === '챗봇이 답변을 작성 중입니다...') {
          return [...prev.slice(0, -1), { role: 'bot', content: '서버와의 통신에 문제가 발생했습니다.' }];
        }
        return [...prev, { role: 'bot', content: '서버와의 통신에 문제가 발생했습니다.' }];
      });
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

  return (
    <div className="chat-container">
    <div class="chat-header-row">
      <div class='modal-container'>
        {isModalOpen == true &&
        <>
          <div className="modal-background">
            <div className="modal-content">
              <div className="modal-text">상담을 종료하겠습니까?</div>
              <p>어려움을 겪고 계신가요?<br></br>상담원이 도와드리겠습니다.<br></br>0000-0000</p> 
              <div className="modal-buttons">
                <button className="modal-button yes" onClick={handleEndChatCancel}>네</button>
                <button className="modal-button no" onClick={handleEndChatCancel}>아니오</button>
              </div>
            </div>
          </div>
        </>
        }</div>
      <div class="chat-header">현대해상 AI 챗봇</div>
      <button class="end-button" onClick={handleEndChat}>상담 종료</button>
    </div>
      <div className="model-select-row">
        <label htmlFor="model-select">모델 선택: </label>
        <select
          id="model-select"
          value={model}
          onChange={e => setModel(e.target.value)}
          disabled={modelOptions.length === 0}
        >
          {modelOptions.length === 0 && <option>모델 없음</option>}
          {modelOptions.map(opt => (
            <option key={opt.name} value={opt.name}>{opt.display_name}</option>
          ))}
        </select>
      </div>
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>{msg.content}</div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-row">
        <input
          type="text"
          placeholder="메시지를 입력하세요..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={handleCompositionStart}
          onCompositionEnd={handleCompositionEnd}
          className="chat-input"
        />
        <button onClick={handleSend} className="send-btn">전송</button>
        <button onClick={handleConnectAgent} className="agent-btn">상담사 연결</button>
      </div>
    </div>
  );
}

export default App;
