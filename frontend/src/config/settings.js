/**
 * Hi-Care AI 챗봇 프론트엔드 설정
 * 모든 설정값을 중앙화하여 관리
 */

// 환경별 설정
const ENVIRONMENTS = {
  development: {
    API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    DEBUG: true,
    LOG_LEVEL: 'debug'
  },
  production: {
    API_URL: import.meta.env.VITE_API_URL || 'https://api.hi-care.app',
    DEBUG: false,
    LOG_LEVEL: 'error'
  },
  staging: {
    API_URL: import.meta.env.VITE_API_URL || 'https://staging-api.hi-care.app',
    DEBUG: true,
    LOG_LEVEL: 'info'
  }
};

// 현재 환경 결정
const getCurrentEnvironment = () => {
  const env = import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE || 'development';
  return ENVIRONMENTS[env] || ENVIRONMENTS.development;
};

// 현재 환경 설정
const ENV_CONFIG = getCurrentEnvironment();

// 앱 기본 설정
export const APP_CONFIG = {
  // 기본 정보
  name: 'Hi-Care AI 챗봇',
  version: '2.0.0',
  description: 'AI 기반 고객 상담 시스템',
  
  // API 설정
  api: {
    baseURL: ENV_CONFIG.API_URL,
    timeout: 30000, // 30초
    retryAttempts: 3,
    retryDelay: 1000, // 1초
  },
  
  // 채팅 설정
  chat: {
    maxMessageLength: 1000,
    maxHistorySize: 50,
    typingDelay: 100,
    autoScrollDelay: 300,
    sessionTimeout: 30 * 60 * 1000, // 30분
    inactivityWarning: 3 * 60 * 1000, // 3분
  },
  
  // UI 설정
  ui: {
    theme: 'light',
    language: 'ko',
    animations: true,
    autoSave: true,
    quickMenuShortcut: 'Ctrl+K',
    clearHistoryShortcut: 'Ctrl+L',
  },
  
  // 로깅 설정
  logging: {
    enabled: ENV_CONFIG.DEBUG,
    level: ENV_CONFIG.LOG_LEVEL,
    console: ENV_CONFIG.DEBUG,
    remote: !ENV_CONFIG.DEBUG,
  },
  
  // 오프라인 설정
  offline: {
    enabled: true,
    cacheSize: 50 * 1024 * 1024, // 50MB
    syncOnReconnect: true,
  },
  
  // PWA 설정
  pwa: {
    installPromptDelay: 3000, // 3초 후 표시
    installPromptCooldown: 24 * 60 * 60 * 1000, // 24시간
  },
  
  // 보안 설정
  security: {
    encryptLocalStorage: true,
    sanitizeInput: true,
    maxFileUploadSize: 10 * 1024 * 1024, // 10MB
  },
  
  // 성능 설정
  performance: {
    lazyLoading: true,
    imageCaching: true,
    bundleSize: 'medium',
  }
};

// 모델 설정
export const MODEL_CONFIG = {
  default: 'claude-3.7-sonnet',
  options: [
    {
      id: 'claude-3.7-sonnet',
      name: 'Claude 3.7 Sonnet',
      description: '균형잡힌 성능과 품질',
      maxTokens: 8192,
      temperature: 0.7,
    },
    {
      id: 'claude-4.0-sonnet',
      name: 'Claude 4.0 Sonnet',
      description: '최신 고성능 모델',
      maxTokens: 8192,
      temperature: 0.7,
    },
    {
      id: 'claude-3.5-haiku',
      name: 'Claude 3.5 Haiku',
      description: '빠른 응답 속도',
      maxTokens: 4096,
      temperature: 0.5,
    },
    {
      id: 'claude-3.7-sonnet-extended',
      name: 'Claude 3.7 Sonnet Extended Thinking',
      description: '깊은 사고가 필요한 복잡한 질문',
      maxTokens: 16384,
      temperature: 0.8,
    }
  ]
};

// 감정 설정
export const EMOTION_CONFIG = {
  colors: {
    '긍정': { primary: '#4CAF50', background: '#E8F5E8' },
    '부정': { primary: '#FF9800', background: '#FFF3E0' },
    '불만': { primary: '#F44336', background: '#FFEBEE' },
    '분노': { primary: '#D32F2F', background: '#FFCDD2' },
    '불안': { primary: '#9C27B0', background: '#F3E5F5' },
    '중립': { primary: '#607D8B', background: '#ECEFF1' },
    '기쁨': { primary: '#4CAF50', background: '#E8F5E8' },
    '슬픔': { primary: '#2196F3', background: '#E3F2FD' },
    '놀람': { primary: '#FF9800', background: '#FFF3E0' },
    '만족': { primary: '#4CAF50', background: '#E8F5E8' },
    '실망': { primary: '#FF5722', background: '#FBE9E7' }
  },
  emojis: {
    '긍정': '😊', '부정': '😔', '불만': '😤', '분노': '😠',
    '불안': '😰', '중립': '😐', '기쁨': '😄', '슬픔': '😢',
    '놀람': '😲', '만족': '😌', '실망': '😞'
  },
  confidenceThreshold: 0.7,
  displayDuration: 5000, // 5초
};

// 스토리지 설정
export const STORAGE_CONFIG = {
  keys: {
    chatHistory: 'hi_care_chat_history',
    userPreferences: 'hi_care_user_preferences',
    sessionData: 'hi_care_session_data',
    offlineQueue: 'hi_care_offline_queue',
    appState: 'hi_care_app_state',
  },
  encryption: APP_CONFIG.security.encryptLocalStorage,
  compression: true,
  maxSize: 5 * 1024 * 1024, // 5MB
};

// 네트워크 설정
export const NETWORK_CONFIG = {
  retry: {
    attempts: 3,
    delay: 1000,
    backoff: 2,
  },
  timeout: {
    default: 10000, // 10초
    upload: 60000, // 60초
    download: 30000, // 30초
  },
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true',
    'X-Client-Version': APP_CONFIG.version,
  }
};

// 개발 도구 설정
export const DEV_CONFIG = {
  enabled: ENV_CONFIG.DEBUG,
  features: {
    reactDevTools: true,
    reduxDevTools: true,
    performanceMonitor: true,
    errorBoundary: true,
  },
  logging: {
    api: true,
    state: true,
    performance: true,
    errors: true,
  }
};

// 기능 플래그
export const FEATURE_FLAGS = {
  // 실험적 기능
  experimentalUI: false,
  betaFeatures: ENV_CONFIG.DEBUG,
  
  // 기능 토글
  voiceInput: false,
  imageUpload: true,
  fileUpload: false,
  notifications: true,
  analytics: !ENV_CONFIG.DEBUG,
  
  // AI 기능
  emotionAnalysis: true,
  smartSuggestions: true,
  contextAwareness: true,
  multiLanguage: false,
};

// 접근성 설정
export const ACCESSIBILITY_CONFIG = {
  highContrast: false,
  fontSize: 'medium', // small, medium, large
  reduceMotion: false,
  screenReader: true,
  keyboardNavigation: true,
  focusIndicators: true,
};

// 설정 유틸리티 함수들
export const getConfig = (path) => {
  const keys = path.split('.');
  let config = { APP_CONFIG, MODEL_CONFIG, EMOTION_CONFIG, STORAGE_CONFIG };
  
  for (const key of keys) {
    config = config[key];
    if (!config) return undefined;
  }
  
  return config;
};

export const isFeatureEnabled = (feature) => {
  return FEATURE_FLAGS[feature] || false;
};

export const getEnvironment = () => {
  return import.meta.env.MODE || 'development';
};

export const isDevelopment = () => {
  return getEnvironment() === 'development';
};

export const isProduction = () => {
  return getEnvironment() === 'production';
};

// 기본 내보내기
export default {
  APP: APP_CONFIG,
  MODEL: MODEL_CONFIG,
  EMOTION: EMOTION_CONFIG,
  STORAGE: STORAGE_CONFIG,
  NETWORK: NETWORK_CONFIG,
  DEV: DEV_CONFIG,
  FEATURES: FEATURE_FLAGS,
  ACCESSIBILITY: ACCESSIBILITY_CONFIG,
  utils: {
    getConfig,
    isFeatureEnabled,
    getEnvironment,
    isDevelopment,
    isProduction,
  }
}; 