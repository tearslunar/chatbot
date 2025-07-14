import React, { useEffect, useRef, memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useChatContext } from '../context/ChatContext';
import ChatLoading from './ChatLoading';
import EmotionIndicator from './EmotionIndicator';
import RecommendedFAQs from './RecommendedFAQs';

// 개별 메시지 컴포넌트 메모화
const MessageItem = memo(({ msg, idx, isLast }) => {
  return (
    <div className={`chat-message ${msg.role}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {msg.content}
      </ReactMarkdown>
      
      {/* 사용자 메시지에만 감정 표시 */}
      {msg.role === 'user' && msg.emotion && (
        <EmotionIndicator emotion={msg.emotion} />
      )}
      
      {msg.escalation_needed && (
        <div className="escalation-warning">
          ⚠️ 상담사 연결이 권장됩니다
        </div>
      )}
      
      {/* 감정 격화 상태별 알림 */}
      {msg.requires_human_support && (
        <div className="session-termination-warning">
          🚨 고객님의 상황을 위해 전문 상담사 연결을 권장드립니다
          <div className="contact-info">
            <div>📞 전화 상담: 1588-5656 (평일 9시-18시)</div>
            <div>💬 채팅 상담: 고객센터 → 채팅 상담 신청</div>
          </div>
        </div>
      )}
      
      {msg.intervention_type && msg.intervention_type !== 'none' && !msg.requires_human_support && (
        <div className={`intervention-notice ${msg.intervention_type}`}>
          {msg.intervention_type === 'cooling_down' && '😌 잠시 시간을 두고 차근차근 해결해보겠습니다'}
          {msg.intervention_type === 'de_escalation' && '🤝 상황을 정확히 파악하여 도움을 드리겠습니다'}
          {msg.intervention_type === 'empathy_boost' && '💙 고객님의 마음을 이해하며 최선을 다하겠습니다'}
        </div>
      )}
      
      {/* 추천 FAQ는 마지막 bot 메시지에만 노출 */}
      {msg.role === 'bot' && 
       isLast && 
       msg.recommended_faqs && (
        <RecommendedFAQs faqs={msg.recommended_faqs} />
      )}
    </div>
  );
});

const MessageList = () => {
  const { state } = useChatContext();
  const { messages, isBotTyping } = state;
  const messagesEndRef = useRef(null);

  // 스크롤 하단 고정
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isBotTyping]);

  return (
    <div className="chat-messages">
      {messages.map((msg, idx) => (
        <MessageItem 
          key={`${msg.role}-${idx}-${msg.content?.substring(0, 50)}`}
          msg={msg} 
          idx={idx} 
          isLast={idx === messages.length - 1}
        />
      ))}
      
      {isBotTyping && <ChatLoading />}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;