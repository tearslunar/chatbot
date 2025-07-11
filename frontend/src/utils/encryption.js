import CryptoJS from 'crypto-js';

// 🔐 보안 설정
const ENCRYPTION_KEY = process.env.REACT_APP_ENCRYPTION_KEY || 'hi-care-2024-secure-key-32ch';
const IV_LENGTH = 16; // AES block size

/**
 * 🔒 개인정보 암호화 (AES-256-CBC)
 * @param {string} plaintext - 암호화할 평문
 * @returns {string} 암호화된 데이터 (Base64)
 */
export const encryptPersonalData = (plaintext) => {
  try {
    if (!plaintext || typeof plaintext !== 'string') {
      return '';
    }

    // 랜덤 IV 생성
    const iv = CryptoJS.lib.WordArray.random(IV_LENGTH);
    
    // AES 암호화
    const encrypted = CryptoJS.AES.encrypt(plaintext, ENCRYPTION_KEY, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    });

    // IV + 암호화된 데이터를 Base64로 인코딩
    const combined = iv.concat(encrypted.ciphertext);
    return CryptoJS.enc.Base64.stringify(combined);
  } catch (error) {
    console.error('[암호화 오류]', error);
    return '';
  }
};

/**
 * 🔓 개인정보 복호화 (AES-256-CBC)
 * @param {string} encryptedData - 암호화된 데이터 (Base64)
 * @returns {string} 복호화된 평문
 */
export const decryptPersonalData = (encryptedData) => {
  try {
    if (!encryptedData || typeof encryptedData !== 'string') {
      return '';
    }

    // Base64 디코딩
    const combined = CryptoJS.enc.Base64.parse(encryptedData);
    
    // IV와 암호화된 데이터 분리
    const iv = CryptoJS.lib.WordArray.create(combined.words.slice(0, 4));
    const ciphertext = CryptoJS.lib.WordArray.create(combined.words.slice(4));
    
    // AES 복호화
    const decrypted = CryptoJS.AES.decrypt(
      CryptoJS.lib.CipherParams.create({ ciphertext: ciphertext }),
      ENCRYPTION_KEY,
      {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
      }
    );

    return decrypted.toString(CryptoJS.enc.Utf8);
  } catch (error) {
    console.error('[복호화 오류]', error);
    return '';
  }
};

/**
 * 👁️ 개인정보 마스킹 처리
 * @param {string} data - 마스킹할 데이터
 * @param {string} type - 데이터 타입 ('name', 'phone', 'email', 'card', 'account')
 * @returns {string} 마스킹된 데이터
 */
export const maskPersonalData = (data, type) => {
  if (!data || typeof data !== 'string') {
    return '';
  }

  const cleanData = data.trim();
  
  switch (type) {
    case 'name':
      // 이름: 홍*동, 김** (2자 이상일 때 중간 마스킹)
      if (cleanData.length <= 2) {
        return cleanData[0] + '*';
      }
      return cleanData[0] + '*'.repeat(cleanData.length - 2) + cleanData[cleanData.length - 1];
      
    case 'phone':
      // 전화번호: 010-1234-5678 → 010-****-5678
      const phoneMatch = cleanData.match(/^(\d{3})-?(\d{4})-?(\d{4})$/);
      if (phoneMatch) {
        return `${phoneMatch[1]}-****-${phoneMatch[3]}`;
      }
      return cleanData.replace(/\d/g, (char, index) => 
        index < 3 || index >= cleanData.length - 4 ? char : '*'
      );
      
    case 'email':
      // 이메일: example@email.com → ex***@email.com
      const emailParts = cleanData.split('@');
      if (emailParts.length === 2) {
        const localPart = emailParts[0];
        const domainPart = emailParts[1];
        const maskedLocal = localPart.length > 2 
          ? localPart.substring(0, 2) + '*'.repeat(localPart.length - 2)
          : localPart[0] + '*';
        return `${maskedLocal}@${domainPart}`;
      }
      return cleanData;
      
    case 'card':
      // 카드번호: 1234-5678-9012-3456 → 1234-****-****-3456
      const cardClean = cleanData.replace(/\D/g, '');
      if (cardClean.length >= 8) {
        return cardClean.substring(0, 4) + '-****-****-' + cardClean.substring(cardClean.length - 4);
      }
      return '*'.repeat(cleanData.length);
      
    case 'account':
      // 계좌번호: 123-456-789012 → 123-***-**9012
      const accountParts = cleanData.split('-');
      if (accountParts.length >= 2) {
        const lastPart = accountParts[accountParts.length - 1];
        const maskedLast = lastPart.length > 4 
          ? '*'.repeat(lastPart.length - 4) + lastPart.substring(lastPart.length - 4)
          : lastPart;
        return accountParts[0] + '-***-' + maskedLast;
      }
      return cleanData;
      
    case 'birthDate':
      // 생년월일: 1990-01-01 → 19**-**-01
      if (cleanData.match(/^\d{4}-\d{2}-\d{2}$/)) {
        const parts = cleanData.split('-');
        return `${parts[0].substring(0, 2)}**-**-${parts[2]}`;
      }
      return cleanData;
      
    default:
      // 기본: 앞 2자, 뒤 2자 제외하고 마스킹
      if (cleanData.length <= 4) {
        return cleanData[0] + '*'.repeat(cleanData.length - 1);
      }
      return cleanData.substring(0, 2) + '*'.repeat(cleanData.length - 4) + cleanData.substring(cleanData.length - 2);
  }
};

/**
 * 🔐 민감정보 입력 필드 보안 강화
 * @param {string} value - 입력 값
 * @param {string} type - 필드 타입
 * @returns {Object} {isValid, errorMessage, formattedValue}
 */
export const validateAndFormatSecureInput = (value, type) => {
  const result = {
    isValid: true,
    errorMessage: '',
    formattedValue: value
  };

  if (!value) {
    return result;
  }

  switch (type) {
    case 'cardNumber':
      // 카드번호: 숫자만 허용, 16자리 검증
      const cardDigits = value.replace(/\D/g, '');
      if (cardDigits.length > 16) {
        result.isValid = false;
        result.errorMessage = '카드번호는 16자리 숫자여야 합니다.';
      } else {
        // 4자리마다 하이픈 추가
        result.formattedValue = cardDigits.replace(/(\d{4})/g, '$1-').replace(/-$/, '');
      }
      break;
      
    case 'cvv':
      // CVV: 숫자만 허용, 3-4자리
      const cvvDigits = value.replace(/\D/g, '');
      if (cvvDigits.length > 4) {
        result.isValid = false;
        result.errorMessage = 'CVV는 3-4자리 숫자여야 합니다.';
      } else {
        result.formattedValue = cvvDigits;
      }
      break;
      
    case 'expiryDate':
      // 유효기간: MM/YY 형식
      const expiryDigits = value.replace(/\D/g, '');
      if (expiryDigits.length > 4) {
        result.isValid = false;
        result.errorMessage = '유효기간은 MM/YY 형식이어야 합니다.';
      } else {
        result.formattedValue = expiryDigits.replace(/(\d{2})(\d{1,2})/, '$1/$2');
      }
      break;
      
    case 'phone':
      // 전화번호: 숫자만 허용, 010으로 시작
      const phoneDigits = value.replace(/\D/g, '');
      if (phoneDigits.length > 11) {
        result.isValid = false;
        result.errorMessage = '전화번호는 11자리 숫자여야 합니다.';
      } else if (phoneDigits.length >= 3 && !phoneDigits.startsWith('010')) {
        result.isValid = false;
        result.errorMessage = '휴대폰 번호는 010으로 시작해야 합니다.';
      } else {
        // 010-1234-5678 형식으로 포맷팅
        result.formattedValue = phoneDigits.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
      }
      break;
      
    default:
      break;
  }

  return result;
};

/**
 * 🛡️ 보안 감사 로그 (개발용)
 * @param {string} action - 액션 타입
 * @param {Object} metadata - 메타데이터
 */
export const logSecurityEvent = (action, metadata = {}) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(`[보안 감사] ${new Date().toISOString()} - ${action}`, {
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      ...metadata
    });
  }
};

// 🔐 보안 유틸리티 객체
export const SecurityUtils = {
  encrypt: encryptPersonalData,
  decrypt: decryptPersonalData,
  mask: maskPersonalData,
  validate: validateAndFormatSecureInput,
  log: logSecurityEvent
}; 