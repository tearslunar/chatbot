/**
 * Hi-Care AI 챗봇 API 클라이언트
 * 중앙화된 설정을 사용하는 HTTP 클라이언트
 */

import { APP_CONFIG, NETWORK_CONFIG } from '../config/settings.js';

/**
 * HTTP 상태 코드
 */
const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
};

/**
 * API 에러 클래스
 */
class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * 네트워크 에러 클래스
 */
class NetworkError extends Error {
  constructor(message, originalError = null) {
    super(message);
    this.name = 'NetworkError';
    this.originalError = originalError;
  }
}

/**
 * API 클라이언트 클래스
 */
class ApiClient {
  constructor() {
    this.baseURL = APP_CONFIG.api.baseURL;
    this.timeout = APP_CONFIG.api.timeout;
    this.retryAttempts = APP_CONFIG.api.retryAttempts;
    this.retryDelay = APP_CONFIG.api.retryDelay;
  }

  /**
   * 요청 헤더 생성
   */
  getHeaders(customHeaders = {}) {
    return {
      ...NETWORK_CONFIG.headers,
      ...customHeaders,
    };
  }

  /**
   * 응답 처리
   */
  async handleResponse(response) {
    if (!response.ok) {
      let errorData = null;
      
      try {
        errorData = await response.json();
      } catch (e) {
        // JSON 파싱 실패 시 텍스트로 시도
        try {
          errorData = { message: await response.text() };
        } catch (e2) {
          errorData = { message: '알 수 없는 에러가 발생했습니다.' };
        }
      }

      throw new ApiError(
        errorData.message || `HTTP ${response.status}`,
        response.status,
        errorData
      );
    }

    try {
      return await response.json();
    } catch (e) {
      // JSON이 아닌 응답의 경우
      return { success: true };
    }
  }

  /**
   * 재시도 로직이 포함된 fetch
   */
  async fetchWithRetry(url, options, attempt = 1) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return await this.handleResponse(response);

    } catch (error) {
      clearTimeout(timeoutId);

      // 중단된 요청 (타임아웃)
      if (error.name === 'AbortError') {
        throw new NetworkError('요청 시간이 초과되었습니다.');
      }

      // 네트워크 에러
      if (!navigator.onLine) {
        throw new NetworkError('인터넷 연결을 확인해주세요.');
      }

      // 재시도 로직
      if (attempt < this.retryAttempts && this.shouldRetry(error)) {
        console.log(`[API] 재시도 ${attempt}/${this.retryAttempts - 1}: ${url}`);
        await this.delay(this.retryDelay * attempt);
        return this.fetchWithRetry(url, options, attempt + 1);
      }

      // API 에러는 그대로 전파
      if (error instanceof ApiError) {
        throw error;
      }

      // 기타 에러는 NetworkError로 변환
      throw new NetworkError(
        error.message || '네트워크 에러가 발생했습니다.',
        error
      );
    }
  }

  /**
   * 재시도 여부 결정
   */
  shouldRetry(error) {
    // API 에러의 경우 5xx 에러만 재시도
    if (error instanceof ApiError) {
      return error.status >= 500;
    }
    
    // 네트워크 에러는 재시도
    return true;
  }

  /**
   * 지연 함수
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * GET 요청
   */
  async get(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const requestOptions = {
      method: 'GET',
      headers: this.getHeaders(options.headers),
    };

    return this.fetchWithRetry(url, requestOptions);
  }

  /**
   * POST 요청
   */
  async post(endpoint, data = null, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const requestOptions = {
      method: 'POST',
      headers: this.getHeaders(options.headers),
      body: data ? JSON.stringify(data) : null,
    };

    return this.fetchWithRetry(url, requestOptions);
  }

  /**
   * PUT 요청
   */
  async put(endpoint, data = null, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const requestOptions = {
      method: 'PUT',
      headers: this.getHeaders(options.headers),
      body: data ? JSON.stringify(data) : null,
    };

    return this.fetchWithRetry(url, requestOptions);
  }

  /**
   * DELETE 요청
   */
  async delete(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const requestOptions = {
      method: 'DELETE',
      headers: this.getHeaders(options.headers),
    };

    return this.fetchWithRetry(url, requestOptions);
  }

  /**
   * 파일 업로드
   */
  async uploadFile(endpoint, file, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const formData = new FormData();
    formData.append('file', file);

    // 파일 업로드 시에는 Content-Type 헤더를 제거 (브라우저가 자동 설정)
    const headers = { ...this.getHeaders(options.headers) };
    delete headers['Content-Type'];

    const requestOptions = {
      method: 'POST',
      headers,
      body: formData,
    };

    return this.fetchWithRetry(url, requestOptions);
  }
}

// 싱글톤 인스턴스 생성
const apiClient = new ApiClient();

/**
 * 채팅 API
 */
export const chatApi = {
  // 메시지 전송
  sendMessage: (data) => apiClient.post('/chat/message', data),
  
  // 세션 종료
  endSession: (sessionId) => apiClient.post('/chat/end-session', { session_id: sessionId }),
  
  // 평점 제출
  submitRating: (data) => apiClient.post('/chat/submit-rating', data),
  
  // 채팅 히스토리
  getHistory: (sessionId) => apiClient.get(`/chat/history/${sessionId}`),
  
  // 대화 요약
  getSummary: (sessionId) => apiClient.get(`/chat/summary/${sessionId}`),
};

/**
 * 페르소나 API
 */
export const personaApi = {
  // 페르소나 목록
  getList: () => apiClient.get('/persona/list'),
  
  // 페르소나 설정
  set: (data) => apiClient.post('/persona/set', data),
  
  // 페르소나 인사말
  getGreeting: (sessionId) => apiClient.post('/persona/greeting', { session_id: sessionId }),
};

/**
 * 보험 API
 */
export const insuranceApi = {
  // 개인정보 검증
  validatePersonalData: (data) => apiClient.post('/insurance/validate-personal-data', data),
  
  // 보험료 계산
  calculatePremium: (data) => apiClient.post('/insurance/calculate-premium', data),
  
  // 상품 정보
  getProducts: () => apiClient.get('/insurance/products'),
  
  // 가입 신청
  apply: (data) => apiClient.post('/insurance/apply', data),
};

/**
 * 감정 분석 API
 */
export const emotionApi = {
  // 감정 분석
  analyze: (text) => apiClient.post('/emotion/analyze', { text }),
  
  // 감정 히스토리
  getHistory: (sessionId) => apiClient.get(`/emotion/history/${sessionId}`),
  
  // 감정 통계
  getStats: (sessionId) => apiClient.get(`/emotion/stats/${sessionId}`),
};

/**
 * FAQ API
 */
export const faqApi = {
  // FAQ 검색
  search: (query) => apiClient.post('/faq/search', { query }),
  
  // 추천 FAQ
  getRecommended: (context) => apiClient.post('/faq/recommended', context),
  
  // FAQ 상세
  getDetail: (faqId) => apiClient.get(`/faq/${faqId}`),
};

/**
 * 시스템 API
 */
export const systemApi = {
  // 헬스 체크
  healthCheck: () => apiClient.get('/health'),
  
  // 버전 정보
  getVersion: () => apiClient.get('/version'),
  
  // 통계
  getStats: () => apiClient.get('/stats'),
};

// 기본 내보내기
export default apiClient;

// 에러 클래스 내보내기
export { ApiError, NetworkError }; 