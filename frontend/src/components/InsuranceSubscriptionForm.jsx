
import React, { useState } from 'react';
import { useChatContext } from '../context/ChatContext'; // ChatContext import
import { SecurityUtils } from '../utils/encryption';

const API_URL = import.meta.env.VITE_API_URL;

function InsuranceSubscriptionForm({ sessionId = 'unknown' }) {
  const { actions } = useChatContext(); // ChatContext 사용
  const [formData, setFormData] = useState({
    name: '',
    birthDate: '',
    gender: '',
    phone: '',
    email: '',
    address: '',
    occupation: '',
  });

  const [maskedData, setMaskedData] = useState({
    name: '',
    phone: '',
    email: '',
  });
  const [inputErrors, setInputErrors] = useState({});
  const [isSecurityMode, setIsSecurityMode] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const updateFormData = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const updateSecureFormData = (field, value, dataType) => {
    const validation = SecurityUtils.validate(value, dataType);
    
    setInputErrors(prev => ({
      ...prev,
      [field]: validation.isValid ? '' : validation.errorMessage
    }));

    if (validation.isValid) {
      let finalValue = validation.formattedValue;

      if (isSecurityMode && value.trim()) {
        finalValue = SecurityUtils.encrypt(validation.formattedValue);
        SecurityUtils.log('데이터 암호화', { field, dataType });
      }

      const maskType = dataType || field;
      setMaskedData(prev => ({
        ...prev,
        [field]: SecurityUtils.mask(validation.formattedValue, maskType)
      }));

      setFormData(prev => ({
        ...prev,
        [field]: finalValue
      }));
    }
  };

  const handleSubscription = async () => {
    setIsLoading(true);
    try {
      const securityMetadata = {
        ip_address: 'client-side',
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        encryption_enabled: isSecurityMode
      };

      const processedFormData = { ...formData };
      let decryptedName = '';

      const sensitiveFields = ['name', 'phone', 'email', 'address'];
      if (isSecurityMode) {
        for (const field of sensitiveFields) {
          if (processedFormData[field] && typeof processedFormData[field] === 'string') {
            try {
              const decryptedValue = SecurityUtils.decrypt(processedFormData[field]) || processedFormData[field];
              if (field === 'name') {
                decryptedName = decryptedValue;
              }
              processedFormData[field] = decryptedValue;
            } catch (e) {
              console.warn(`[보안] ${field} 복호화 실패:`, e);
            }
          }
        }
      }

      const response = await fetch(`${API_URL}/auto-insurance/subscribe`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          session_id: sessionId,
          subscription_info: processedFormData,
          security_metadata: securityMetadata
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        SecurityUtils.log('보험 가입 신청 성공', {
          application_id: result.application_id,
          security_enabled: isSecurityMode
        });
        
        // 채팅 컨텍스트에 메시지 추가
        const customerName = decryptedName || formData.name || '고객';
        actions.addMessage({
          role: 'system',
          content: `${customerName}님의 보험 가입 신청 정보가 시스템에 정상적으로 접수되었습니다. 관련하여 궁금한 점이 있으시면 편하게 질문해주세요.`
        });

        alert('가입 신청이 완료되었습니다. 채팅창에서 접수 사실을 확인하고 이어서 상담하실 수 있습니다.');

      } else {
        const errorData = await response.json();
        SecurityUtils.log('보험 가입 신청 실패', { error: errorData.error });
        alert(`가입 신청 중 오류가 발생했습니다: ${errorData.error}`);
      }
    } catch (error) {
      console.error('보험 가입 신청 실패:', error);
      SecurityUtils.log('보험 가입 신청 네트워크 오류', { error: error.message });
      alert('가입 신청 중 네트워크 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="subscription-form-container">
      <div className="security-header">
        <h3>보험 가입 정보 입력</h3>
        <div className="security-indicator">
          <span className="security-icon">🔐</span>
          <span className="security-text">256bit AES 암호화 보호</span>
          <button 
            className="security-toggle"
            onClick={() => setIsSecurityMode(!isSecurityMode)}
            title={isSecurityMode ? "마스킹 해제" : "마스킹 활성화"}
          >
            {isSecurityMode ? "👁️‍🗨️" : "👁️"}
          </button>
        </div>
      </div>

      <div className="security-notice">
        <p>🛡️ 입력하신 개인정보는 개인정보보호법에 따라 안전하게 암호화되어 보호됩니다.</p>
      </div>

      <div className="form-grid">
        <div className="form-group">
          <label>이름 * 
            {isSecurityMode && maskedData.name && (
              <span className="masked-display"> (표시: {maskedData.name})</span>
            )}
          </label>
          <input 
            type="text" 
            value={isSecurityMode && maskedData.name ? maskedData.name : formData.name}
            onChange={e => updateSecureFormData('name', e.target.value, 'name')}
            placeholder="홍길동"
            className={inputErrors.name ? 'input-error' : ''}
          />
          {inputErrors.name && <p className="error-message">{inputErrors.name}</p>}
        </div>
        
        <div className="form-group">
          <label>생년월일 *</label>
          <input 
            type="date" 
            value={formData.birthDate}
            onChange={e => updateFormData('birthDate', e.target.value)}
          />
        </div>
        
        <div className="form-group">
          <label>성별 *</label>
          <select 
            value={formData.gender}
            onChange={e => updateFormData('gender', e.target.value)}
          >
            <option value="">선택해주세요</option>
            <option value="male">남성</option>
            <option value="female">여성</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>연락처 *
            {isSecurityMode && maskedData.phone && (
              <span className="masked-display"> (표시: {maskedData.phone})</span>
            )}
          </label>
          <input 
            type="tel" 
            value={isSecurityMode && maskedData.phone ? maskedData.phone : formData.phone}
            onChange={e => updateSecureFormData('phone', e.target.value, 'phone')}
            placeholder="010-1234-5678"
            className={inputErrors.phone ? 'input-error' : ''}
          />
          {inputErrors.phone && <p className="error-message">{inputErrors.phone}</p>}
        </div>
        
        <div className="form-group full-width">
          <label>이메일 *
            {isSecurityMode && maskedData.email && (
              <span className="masked-display"> (표시: {maskedData.email})</span>
            )}
          </label>
          <input 
            type="email" 
            value={isSecurityMode && maskedData.email ? maskedData.email : formData.email}
            onChange={e => updateSecureFormData('email', e.target.value, 'email')}
            placeholder="example@email.com"
            className={inputErrors.email ? 'input-error' : ''}
          />
          {inputErrors.email && <p className="error-message">{inputErrors.email}</p>}
        </div>
        
        <div className="form-group full-width">
          <label>주소 *</label>
          <input 
            type="text" 
            value={formData.address}
            onChange={e => updateSecureFormData('address', e.target.value, 'address')}
            placeholder="서울시 강남구 테헤란로 123"
            className={inputErrors.address ? 'input-error' : ''}
          />
          {inputErrors.address && <p className="error-message">{inputErrors.address}</p>}
        </div>
        
        <div className="form-group">
          <label>직업</label>
          <input 
            type="text" 
            value={formData.occupation}
            onChange={e => updateFormData('occupation', e.target.value)}
            placeholder="직업을 입력해주세요"
          />
        </div>
      </div>
      <button 
        className="btn-primary" 
        onClick={handleSubscription}
        disabled={isLoading}
      >
        {isLoading ? '처리 중...' : '가입 신청'}
      </button>
    </div>
  );
}

export default InsuranceSubscriptionForm;
