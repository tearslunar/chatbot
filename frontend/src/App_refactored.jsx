import React, { useEffect } from 'react';
import './App.css';

// Context
import { ChatProvider, useChatContext } from './context/ChatContext';

// Components
import ChatHeader from './components/ChatHeader';
import ModelSelector from './components/ModelSelector';
import PersonaSelector from './components/PersonaSelector';
import MessageList from './components/MessageList';
import ChatInput from './components/ChatInput';
import ModalManager from './components/ModalManager';
import QuickMenu from './components/QuickMenu';

// Hooks
import { useInactivityTimer } from './hooks/useInactivityTimer';
import { useEmotionTracker } from './hooks/useEmotionTracker';

// 메인 채팅 앱 컴포넌트
function ChatApp() {
  const { state, actions } = useChatContext();
  const { 
    QuickMenuOpen,
    resolutionResult,
    selectedPersona,
    sessionId
  } = state;

  // 비활성 타이머 훅
  useInactivityTimer();
  
  // 감정 추적 훅
  useEmotionTracker();

  // 페르소나 선택 핸들러
  const handlePersonaSelect = async (persona) => {
    actions.setSelectedPersona(persona);
    
    if (persona) {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      try {
        // 페르소나 설정 API 호출
        const res = await fetch(`${API_URL}/persona/set-persona`, {
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
          
          // 페르소나 기반 인사말 생성
          const greetingRes = await fetch(`${API_URL}/persona/get-persona-greeting`, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'ngrok-skip-browser-warning': 'true'
            },
            body: JSON.stringify({ session_id: sessionId })
          });
          
          if (greetingRes.ok) {
            const greetingData = await greetingRes.json();
            if (greetingData.success) {
              actions.addMessage({ 
                role: 'bot', 
                content: greetingData.greeting 
              });
            }
          }
        }
      } catch (e) {
        console.error('페르소나 설정 실패:', e);
      }
    } else {
      // 페르소나 선택 해제
      actions.addMessage({ 
        role: 'bot', 
        content: '페르소나 선택이 해제되었습니다. 일반적인 상담 모드로 전환됩니다. 😊\n\n무엇을 도와드릴까요?' 
      });
    }
  };

  return (
    <div className="chat-container">
      {/* 채팅 헤더 */}
      <ChatHeader />
      
      {/* 모델 선택 */}
      <ModelSelector />
      
      {/* 페르소나 선택 */}
      <div style={{ padding: '0 20px' }}>
        <PersonaSelector 
          onPersonaSelect={handlePersonaSelect}
          selectedPersona={selectedPersona}
        />
      </div>
      
      {/* 메시지 목록 */}
      <MessageList />
      
      {/* 입력 영역 */}
      <ChatInput />
      
      {/* 빠른 메뉴 */}
      {QuickMenuOpen && <QuickMenu />}
      
      {/* 모달 관리자 */}
      <ModalManager />
      
      {/* 상담 종료 시 해소 결과 알림 */}
      {resolutionResult && (
        <div style={{ 
          background: resolutionResult.resolved ? '#e3fcec' : '#ffeaea', 
          color: '#333', 
          padding: '8px', 
          borderRadius: '8px', 
          margin: '12px 0', 
          textAlign: 'center' 
        }}>
          {resolutionResult.resolved 
            ? '상담 종료 시점에 고객 감정이 해소된 것으로 분석되었습니다.' 
            : '상담 종료 시점에도 고객 감정이 해소되지 않은 것으로 분석되었습니다.'
          }
        </div>
      )}
    </div>
  );
}

// 최상위 앱 컴포넌트 (Provider 래핑)
function App() {
  return (
    <ChatProvider>
      <ChatApp />
    </ChatProvider>
  );
}

export default App;