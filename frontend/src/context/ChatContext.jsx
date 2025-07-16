import React, { createContext, useContext, useReducer, useCallback } from 'react';

const ChatContext = createContext();

const initialState = {
  messages: [{ role: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }],
  input: '',
  model: 'claude-3.7-sonnet',
  isBotTyping: false,
  isSessionEnded: false,
  currentEmotion: null,
  selectedPersona: null,
  sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  
  // UI 상태
  DevMode: false,
  isModalOpen: false,
  isFeedbackModalOpen: false,
  QuickMenuOpen: false,
  expandedFAQ: null,
  selectedCategory: '전체',
  selectedTag: null,
  
  // 피드백 관련
  feedback: '',
  rating: 0,
  hoveredRating: 0,
  
  // 추천 및 자동완성
  suggestedQuestions: [],
  autoCompleteFaqs: [],
  
  // 비활성 타이머
  showInactivityWarning: false,
  remainingTime: 180,
  lastActivityTime: Date.now(),
  
  // 기타
  resolutionResult: null,
  isComposing: false
};

function chatReducer(state, action) {
  switch (action.type) {
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload };
    
    case 'ADD_MESSAGE':
      const newMessages = [...state.messages, action.payload];
      // localStorage에 저장
      localStorage.setItem('chat_history', JSON.stringify(newMessages));
      return { ...state, messages: newMessages };
    
    case 'SET_INPUT':
      return { ...state, input: action.payload };
    
    case 'SET_MODEL':
      return { ...state, model: action.payload };
    
    case 'SET_BOT_TYPING':
      return { ...state, isBotTyping: action.payload };
    
    case 'SET_SESSION_ENDED':
      return { ...state, isSessionEnded: action.payload };
    
    case 'SET_CURRENT_EMOTION':
      return { ...state, currentEmotion: action.payload };
    
    case 'SET_SELECTED_PERSONA':
      return { ...state, selectedPersona: action.payload };
    
    case 'SET_MODAL_OPEN':
      return { ...state, isModalOpen: action.payload };
    
    case 'SET_FEEDBACK_MODAL_OPEN':
      return { ...state, isFeedbackModalOpen: action.payload };
    
    case 'SET_QUICK_MENU_OPEN':
      return { ...state, QuickMenuOpen: action.payload };
    
    case 'SET_EXPANDED_FAQ':
      return { ...state, expandedFAQ: action.payload };
    
    case 'SET_SELECTED_CATEGORY':
      return { ...state, selectedCategory: action.payload, selectedTag: null };
    
    case 'SET_SELECTED_TAG':
      return { ...state, selectedTag: action.payload };
    
    case 'SET_FEEDBACK':
      return { ...state, feedback: action.payload };
    
    case 'SET_RATING':
      return { ...state, rating: action.payload };
    
    case 'SET_HOVERED_RATING':
      return { ...state, hoveredRating: action.payload };
    
    case 'SET_SUGGESTED_QUESTIONS':
      return { ...state, suggestedQuestions: action.payload };
    
    case 'SET_AUTOCOMPLETE_FAQS':
      return { ...state, autoCompleteFaqs: action.payload };
    
    case 'SET_INACTIVITY_WARNING':
      return { ...state, showInactivityWarning: action.payload };
    
    case 'SET_REMAINING_TIME':
      return { ...state, remainingTime: action.payload };
    
    case 'UPDATE_ACTIVITY_TIME':
      return { 
        ...state, 
        lastActivityTime: Date.now(),
        showInactivityWarning: false,
        remainingTime: 180
      };
    
    case 'SET_RESOLUTION_RESULT':
      return { ...state, resolutionResult: action.payload };
    
    case 'SET_COMPOSING':
      return { ...state, isComposing: action.payload };
    
    case 'RESET_CHAT':
      const resetState = {
        ...initialState,
        sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      };
      localStorage.removeItem('chat_history');
      return resetState;
    
    case 'RESET_FEEDBACK':
      return {
        ...state,
        feedback: '',
        rating: 0,
        hoveredRating: 0,
        isFeedbackModalOpen: false
      };
      case 'SET_DEV_MODE':
        return { ...state, DevMode: action.payload };
    
    default:
      return state;
  }
}

export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(chatReducer, initialState, (initial) => {
    // localStorage에서 초기 메시지 로드
    const saved = localStorage.getItem('chat_history');
    if (saved) {
      try {
        const parsedMessages = JSON.parse(saved);
        return { ...initial, messages: parsedMessages };
      } catch {
        return initial;
      }
    }
    return initial;
  });

  const actions = {
    setDevMode: useCallback((devMode) => dispatch({ type: 'SET_DEV_MODE', payload: devMode }), []),
    setMessages: useCallback((messages) => dispatch({ type: 'SET_MESSAGES', payload: messages }), []),
    addMessage: useCallback((message) => dispatch({ type: 'ADD_MESSAGE', payload: message }), []),
    setInput: useCallback((input) => dispatch({ type: 'SET_INPUT', payload: input }), []),
    setModel: useCallback((model) => dispatch({ type: 'SET_MODEL', payload: model }), []),
    setBotTyping: useCallback((typing) => dispatch({ type: 'SET_BOT_TYPING', payload: typing }), []),
    setSessionEnded: useCallback((ended) => dispatch({ type: 'SET_SESSION_ENDED', payload: ended }), []),
    setCurrentEmotion: useCallback((emotion) => dispatch({ type: 'SET_CURRENT_EMOTION', payload: emotion }), []),
    setSelectedPersona: useCallback((persona) => dispatch({ type: 'SET_SELECTED_PERSONA', payload: persona }), []),
    setModalOpen: useCallback((open) => dispatch({ type: 'SET_MODAL_OPEN', payload: open }), []),
    setFeedbackModalOpen: useCallback((open) => dispatch({ type: 'SET_FEEDBACK_MODAL_OPEN', payload: open }), []),
    setQuickMenuOpen: useCallback((open) => dispatch({ type: 'SET_QUICK_MENU_OPEN', payload: open }), []),
    setExpandedFAQ: useCallback((faq) => dispatch({ type: 'SET_EXPANDED_FAQ', payload: faq }), []),
    setSelectedCategory: useCallback((category) => dispatch({ type: 'SET_SELECTED_CATEGORY', payload: category }), []),
    setSelectedTag: useCallback((tag) => dispatch({ type: 'SET_SELECTED_TAG', payload: tag }), []),
    setFeedback: useCallback((feedback) => dispatch({ type: 'SET_FEEDBACK', payload: feedback }), []),
    setRating: useCallback((rating) => dispatch({ type: 'SET_RATING', payload: rating }), []),
    setHoveredRating: useCallback((rating) => dispatch({ type: 'SET_HOVERED_RATING', payload: rating }), []),
    setSuggestedQuestions: useCallback((questions) => dispatch({ type: 'SET_SUGGESTED_QUESTIONS', payload: questions }), []),
    setAutoCompleteFaqs: useCallback((faqs) => dispatch({ type: 'SET_AUTOCOMPLETE_FAQS', payload: faqs }), []),
    setInactivityWarning: useCallback((warning) => dispatch({ type: 'SET_INACTIVITY_WARNING', payload: warning }), []),
    setRemainingTime: useCallback((time) => dispatch({ type: 'SET_REMAINING_TIME', payload: time }), []),
    updateActivityTime: useCallback(() => dispatch({ type: 'UPDATE_ACTIVITY_TIME' }), []),
    setResolutionResult: useCallback((result) => dispatch({ type: 'SET_RESOLUTION_RESULT', payload: result }), []),
    setComposing: useCallback((composing) => dispatch({ type: 'SET_COMPOSING', payload: composing }), []),
    resetChat: useCallback(() => dispatch({ type: 'RESET_CHAT' }), []),
    resetFeedback: useCallback(() => dispatch({ type: 'RESET_FEEDBACK' }), [])
  };

  return (
    <ChatContext.Provider value={{ state, actions }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
}