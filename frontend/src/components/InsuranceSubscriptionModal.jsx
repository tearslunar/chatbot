import React, { useState, useEffect } from 'react';
import './InsuranceSubscriptionModal.css';
import { SecurityUtils } from '../utils/encryption';

const API_URL = import.meta.env.VITE_API_URL;

// 보험 가입 단계 정의
const SUBSCRIPTION_STEPS = [
  { id: 1, name: '상품 선택', description: '원하시는 보험 상품을 선택해주세요' },
  { id: 2, name: '개인정보', description: '가입자 정보를 입력해주세요' },
  { id: 3, name: '약관 동의', description: '약관을 확인하고 동의해주세요' },
  { id: 4, name: '결제 정보', description: '결제 정보를 입력해주세요' },
  { id: 5, name: '가입 완료', description: '가입이 완료되었습니다' }
];

// 보험 상품 카테고리
const INSURANCE_CATEGORIES = [
  {
    id: 'auto',
    name: '자동차보험',
    description: '안전한 운전을 위한 종합 보장',
    icon: '🚗',
    products: [
      { id: 'auto_comprehensive', name: '종합보험', price: '월 89,000원부터', features: ['대인배상', '대물배상', '자차', '자상'] },
      { id: 'auto_driver', name: '운전자보험', price: '월 12,000원부터', features: ['운전 중 상해', '벌금', '변호사 비용'] }
    ]
  },
  {
    id: 'health',
    name: '건강보험',
    description: '건강한 삶을 위한 든든한 보장',
    icon: '🏥',
    products: [
      { id: 'health_comprehensive', name: '종합건강보험', price: '월 45,000원부터', features: ['입원', '통원', '수술', '진단'] },
      { id: 'health_cancer', name: '암보험', price: '월 25,000원부터', features: ['암 진단', '암 치료', '항암 치료', '수술비'] }
    ]
  },
  {
    id: 'life',
    name: '생명보험',
    description: '가족을 위한 평생 보장',
    icon: '👨‍👩‍👧‍👦',
    products: [
      { id: 'life_term', name: '정기생명보험', price: '월 35,000원부터', features: ['사망보장', '고도장해', '만기환급'] },
      { id: 'life_whole', name: '종신보험', price: '월 180,000원부터', features: ['평생보장', '적립', '대출', '연금전환'] }
    ]
  },
  {
    id: 'travel',
    name: '여행보험',
    description: '안전한 여행을 위한 특별 보장',
    icon: '✈️',
    products: [
      { id: 'travel_domestic', name: '국내여행보험', price: '1일 2,000원부터', features: ['상해', '질병', '휴대품', '배상책임'] },
      { id: 'travel_overseas', name: '해외여행보험', price: '1일 8,000원부터', features: ['의료비', '항공기지연', '여권분실', '응급이송'] }
    ]
  }
];

function InsuranceSubscriptionModal({ isOpen, onClose, selectedPersona, actionContext }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // 상품 선택
    selectedCategory: null,
    selectedProduct: null,
    
    // 개인정보 (암호화된 데이터)
    name: '',
    birthDate: '',
    gender: '',
    phone: '',
    email: '',
    address: '',
    occupation: '',
    
    // 약관 동의
    agreements: {
      terms: false,
      privacy: false,
      marketing: false,
      thirdParty: false
    },
    
    // 결제 정보 (고도 암호화 필요)
    paymentMethod: 'card',
    cardNumber: '',
    expiryDate: '',
    cvv: '',
    cardHolder: '',
    bankAccount: '',
    accountHolder: ''
  });

  // 🔐 보안 관련 상태 추가
  const [maskedData, setMaskedData] = useState({
    name: '',
    phone: '',
    email: '',
    cardNumber: '',
    bankAccount: ''
  });
  const [inputErrors, setInputErrors] = useState({});
  const [isSecurityMode, setIsSecurityMode] = useState(true);

  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // 페르소나 기반 상품 추천
  useEffect(() => {
    if (selectedPersona && isOpen) {
      loadRecommendedProducts();
    }
  }, [selectedPersona, isOpen]);

  // 대화 액션 컨텍스트 처리
  useEffect(() => {
    if (actionContext && actionContext.insurance_type && isOpen) {
      // 보험 타입에 따라 카테고리 자동 선택
      const typeMap = {
        '자동차보험': 'auto',
        '건강보험': 'health',
        '생명보험': 'life',
        '여행보험': 'travel'
      };
      
      const categoryId = typeMap[actionContext.insurance_type];
      if (categoryId) {
        setFormData(prev => ({
          ...prev,
          selectedCategory: categoryId
        }));
      }
    }
  }, [actionContext, isOpen]);

  const loadRecommendedProducts = async () => {
    if (!selectedPersona) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/get-recommended-products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona: selectedPersona })
      });
      
      if (response.ok) {
        const data = await response.json();
        setRecommendedProducts(data.products || []);
      }
    } catch (error) {
      console.error('상품 추천 로드 실패:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 입력값 업데이트
  const updateFormData = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 🔐 보안 입력값 업데이트 (암호화 + 마스킹)
  const updateSecureFormData = (field, value, dataType) => {
    // 입력 검증 및 포맷팅
    const validation = SecurityUtils.validate(value, dataType);
    
    // 오류 상태 업데이트
    setInputErrors(prev => ({
      ...prev,
      [field]: validation.isValid ? '' : validation.errorMessage
    }));

    if (validation.isValid) {
      // 민감정보 필드는 암호화 처리
      const sensitiveFields = ['name', 'phone', 'email', 'cardNumber', 'cvv', 'bankAccount', 'address'];
      let finalValue = validation.formattedValue;

      if (sensitiveFields.includes(field)) {
        // 보안 모드에서는 암호화
        if (isSecurityMode && value.trim()) {
          finalValue = SecurityUtils.encrypt(validation.formattedValue);
          SecurityUtils.log('데이터 암호화', { field, dataType });
        }

        // 마스킹된 데이터 업데이트 (화면 표시용)
        const maskType = dataType || field;
        setMaskedData(prev => ({
          ...prev,
          [field]: SecurityUtils.mask(validation.formattedValue, maskType)
        }));
      }

      // 실제 데이터 업데이트
      setFormData(prev => ({
        ...prev,
        [field]: finalValue
      }));
    }
  };

  // 중첩 객체 업데이트 (약관 동의용)
  const updateNestedFormData = (parent, field, value) => {
    setFormData(prev => ({
      ...prev,
      [parent]: {
        ...prev[parent],
        [field]: value
      }
    }));
  };

  // 다음 단계로 이동
  const goToNextStep = () => {
    if (currentStep < SUBSCRIPTION_STEPS.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  // 이전 단계로 이동
  const goToPrevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  // 현재 단계 유효성 검증
  const isCurrentStepValid = () => {
    switch (currentStep) {
      case 1:
        return formData.selectedProduct !== null;
      case 2:
        return formData.name && formData.birthDate && formData.gender && 
               formData.phone && formData.email && formData.address;
      case 3:
        return formData.agreements.terms && formData.agreements.privacy;
      case 4:
        if (formData.paymentMethod === 'card') {
          return formData.cardNumber && formData.expiryDate && formData.cvv && formData.cardHolder;
        } else {
          return formData.bankAccount && formData.accountHolder;
        }
      default:
        return true;
    }
  };

  // 가입 신청 처리
  const handleSubscription = async () => {
    setIsLoading(true);
    try {
      // 🔐 보안 메타데이터 수집
      const securityMetadata = {
        ip_address: 'client-side', // 실제 서비스에서는 서버에서 IP 수집
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        encryption_enabled: isSecurityMode
      };

      // 🔐 민감정보 암호화 처리 (클라이언트 측에서 이미 암호화됨)
      const processedFormData = { ...formData };
      
      // 보안 모드에서 민감정보 복호화 (서버 전송용)
      const sensitiveFields = ['name', 'phone', 'email', 'address', 'cardNumber', 'cvv', 'bankAccount'];
      if (isSecurityMode) {
        for (const field of sensitiveFields) {
          if (processedFormData[field] && typeof processedFormData[field] === 'string') {
            try {
              // 클라이언트에서 암호화된 데이터를 복호화하여 서버로 전송
              processedFormData[field] = SecurityUtils.decrypt(processedFormData[field]) || processedFormData[field];
            } catch (e) {
              // 복호화 실패 시 원본 데이터 유지
              console.warn(`[보안] ${field} 복호화 실패:`, e);
            }
          }
        }
      }

      // 🔐 보안 강화된 가입 신청 요청
      const response = await fetch(`${API_URL}/submit-secure-insurance-application`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          session_id: sessionId,
          form_data: processedFormData,
          persona: selectedPersona,
          consent_agreements: formData.agreements,
          security_metadata: securityMetadata
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // 보안 로그
        SecurityUtils.log('보험 가입 신청 성공', {
          application_id: result.application_id,
          security_enabled: isSecurityMode
        });
        
        // 성공 메시지와 마스킹된 확인 정보 표시
        console.log('보험 가입 신청 성공:', result);
        console.log('확인 정보 (마스킹됨):', result.confirmation_data);
        
        goToNextStep(); // 완료 단계로 이동
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

  // 모달 닫기
  const handleClose = () => {
    setCurrentStep(1);
    setFormData({
      selectedCategory: null,
      selectedProduct: null,
      name: '',
      birthDate: '',
      gender: '',
      phone: '',
      email: '',
      address: '',
      occupation: '',
      agreements: {
        terms: false,
        privacy: false,
        marketing: false,
        thirdParty: false
      },
      paymentMethod: 'card',
      cardNumber: '',
      expiryDate: '',
      cvv: '',
      cardHolder: '',
      bankAccount: '',
      accountHolder: ''
    });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="insurance-modal-overlay" onClick={handleClose}>
      <div className="insurance-modal-content" onClick={e => e.stopPropagation()}>
        <div className="insurance-modal-header">
          <h2>보험 가입 신청</h2>
          <button className="insurance-modal-close" onClick={handleClose}>×</button>
        </div>

        {/* 진행 단계 표시 */}
        <div className="step-progress">
          {SUBSCRIPTION_STEPS.map((step, index) => (
            <div 
              key={step.id} 
              className={`step-item ${currentStep >= step.id ? 'active' : ''} ${currentStep === step.id ? 'current' : ''}`}
            >
              <div className="step-number">{step.id}</div>
              <div className="step-info">
                <div className="step-name">{step.name}</div>
                <div className="step-desc">{step.description}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="insurance-modal-body">
          {/* 단계 1: 상품 선택 */}
          {currentStep === 1 && (
            <div className="step-content">
              <h3>보험 상품 선택</h3>
              
              {/* 페르소나 기반 추천 상품 */}
              {selectedPersona && recommendedProducts.length > 0 && (
                <div className="recommended-section">
                  <h4>🎯 {selectedPersona.페르소나명}님을 위한 맞춤 추천</h4>
                  <div className="recommended-products">
                    {recommendedProducts.map(product => (
                      <div 
                        key={product.id}
                        className={`product-card recommended ${formData.selectedProduct?.id === product.id ? 'selected' : ''}`}
                        onClick={() => updateFormData('selectedProduct', product)}
                      >
                        <div className="product-badge">추천</div>
                        <div className="product-icon">{product.icon}</div>
                        <h5>{product.name}</h5>
                        <p className="product-price">{product.price}</p>
                        <ul className="product-features">
                          {product.features.map((feature, idx) => (
                            <li key={idx}>{feature}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 전체 상품 카테고리 */}
              <div className="insurance-categories">
                {INSURANCE_CATEGORIES.map(category => (
                  <div key={category.id} className="category-section">
                    <div className="category-header">
                      <span className="category-icon">{category.icon}</span>
                      <div>
                        <h4>{category.name}</h4>
                        <p>{category.description}</p>
                      </div>
                    </div>
                    <div className="products-grid">
                      {category.products.map(product => (
                        <div 
                          key={product.id}
                          className={`product-card ${formData.selectedProduct?.id === product.id ? 'selected' : ''}`}
                          onClick={() => updateFormData('selectedProduct', { ...product, categoryId: category.id, categoryName: category.name })}
                        >
                          <h5>{product.name}</h5>
                          <p className="product-price">{product.price}</p>
                          <ul className="product-features">
                            {product.features.map((feature, idx) => (
                              <li key={idx}>{feature}</li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 단계 2: 개인정보 입력 */}
          {currentStep === 2 && (
            <div className="step-content">
              <div className="security-header">
                <h3>개인정보 입력</h3>
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
            </div>
          )}

          {/* 단계 3: 약관 동의 */}
          {currentStep === 3 && (
            <div className="step-content">
              <h3>약관 동의</h3>
              <div className="agreements-section">
                <div className="agreement-item required">
                  <label className="agreement-label">
                    <input 
                      type="checkbox" 
                      checked={formData.agreements.terms}
                      onChange={e => updateNestedFormData('agreements', 'terms', e.target.checked)}
                    />
                    <span className="checkmark"></span>
                    <span className="agreement-text">
                      보험약관 및 상품설명서에 동의합니다 (필수)
                    </span>
                  </label>
                  <button className="view-detail">전문보기</button>
                </div>
                
                <div className="agreement-item required">
                  <label className="agreement-label">
                    <input 
                      type="checkbox" 
                      checked={formData.agreements.privacy}
                      onChange={e => updateNestedFormData('agreements', 'privacy', e.target.checked)}
                    />
                    <span className="checkmark"></span>
                    <span className="agreement-text">
                      개인정보 수집·이용에 동의합니다 (필수)
                    </span>
                  </label>
                  <button className="view-detail">전문보기</button>
                </div>
                
                <div className="agreement-item">
                  <label className="agreement-label">
                    <input 
                      type="checkbox" 
                      checked={formData.agreements.marketing}
                      onChange={e => updateNestedFormData('agreements', 'marketing', e.target.checked)}
                    />
                    <span className="checkmark"></span>
                    <span className="agreement-text">
                      마케팅 정보 수신에 동의합니다 (선택)
                    </span>
                  </label>
                  <button className="view-detail">전문보기</button>
                </div>
                
                <div className="agreement-item">
                  <label className="agreement-label">
                    <input 
                      type="checkbox" 
                      checked={formData.agreements.thirdParty}
                      onChange={e => updateNestedFormData('agreements', 'thirdParty', e.target.checked)}
                    />
                    <span className="checkmark"></span>
                    <span className="agreement-text">
                      제3자 정보 제공에 동의합니다 (선택)
                    </span>
                  </label>
                  <button className="view-detail">전문보기</button>
                </div>
              </div>
            </div>
          )}

          {/* 단계 4: 결제 정보 */}
          {currentStep === 4 && (
            <div className="step-content">
              <h3>결제 정보</h3>
              
              <div className="payment-method-selector">
                <label className="payment-option">
                  <input 
                    type="radio" 
                    name="paymentMethod" 
                    value="card"
                    checked={formData.paymentMethod === 'card'}
                    onChange={e => updateFormData('paymentMethod', e.target.value)}
                  />
                  <span>신용카드</span>
                </label>
                <label className="payment-option">
                  <input 
                    type="radio" 
                    name="paymentMethod" 
                    value="bank"
                    checked={formData.paymentMethod === 'bank'}
                    onChange={e => updateFormData('paymentMethod', e.target.value)}
                  />
                  <span>계좌이체</span>
                </label>
              </div>

              {formData.paymentMethod === 'card' && (
                <div className="payment-form">
                  <div className="security-notice payment-security">
                    <span className="security-icon">🔒</span>
                    <span>결제 정보는 PCI DSS 기준으로 안전하게 보호됩니다</span>
                  </div>
                  
                  <div className="form-group">
                    <label>카드번호 *
                      {isSecurityMode && maskedData.cardNumber && (
                        <span className="masked-display"> (표시: {maskedData.cardNumber})</span>
                      )}
                    </label>
                    <input 
                      type="text" 
                      value={isSecurityMode && maskedData.cardNumber ? maskedData.cardNumber : formData.cardNumber}
                      onChange={e => updateSecureFormData('cardNumber', e.target.value, 'cardNumber')}
                      placeholder="1234-5678-9012-3456"
                      maxLength="19"
                      className={inputErrors.cardNumber ? 'input-error' : ''}
                      autoComplete="cc-number"
                    />
                    {inputErrors.cardNumber && <p className="error-message">{inputErrors.cardNumber}</p>}
                  </div>
                  
                  <div className="form-group-row">
                    <div className="form-group">
                      <label>유효기간 *</label>
                      <input 
                        type="text" 
                        value={formData.expiryDate}
                        onChange={e => updateSecureFormData('expiryDate', e.target.value, 'expiryDate')}
                        placeholder="MM/YY"
                        maxLength="5"
                        className={inputErrors.expiryDate ? 'input-error' : ''}
                        autoComplete="cc-exp"
                      />
                      {inputErrors.expiryDate && <p className="error-message">{inputErrors.expiryDate}</p>}
                    </div>
                    
                    <div className="form-group">
                      <label>CVV *</label>
                      <input 
                        type="password"
                        value={formData.cvv}
                        onChange={e => updateSecureFormData('cvv', e.target.value, 'cvv')}
                        placeholder="123"
                        maxLength="4"
                        className={inputErrors.cvv ? 'input-error' : ''}
                        autoComplete="cc-csc"
                      />
                      {inputErrors.cvv && <p className="error-message">{inputErrors.cvv}</p>}
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label>카드소유자명 *</label>
                    <input 
                      type="text" 
                      value={formData.cardHolder}
                      onChange={e => updateFormData('cardHolder', e.target.value)}
                      placeholder="홍길동"
                      autoComplete="cc-name"
                    />
                  </div>
                </div>
              )}

              {formData.paymentMethod === 'bank' && (
                <div className="payment-form">
                  <div className="security-notice payment-security">
                    <span className="security-icon">🔒</span>
                    <span>계좌 정보는 금융보안원 기준으로 안전하게 보호됩니다</span>
                  </div>
                  
                  <div className="form-group">
                    <label>계좌번호 *
                      {isSecurityMode && maskedData.bankAccount && (
                        <span className="masked-display"> (표시: {maskedData.bankAccount})</span>
                      )}
                    </label>
                    <input 
                      type="text" 
                      value={isSecurityMode && maskedData.bankAccount ? maskedData.bankAccount : formData.bankAccount}
                      onChange={e => updateSecureFormData('bankAccount', e.target.value, 'account')}
                      placeholder="123-456-789012"
                      className={inputErrors.bankAccount ? 'input-error' : ''}
                    />
                    {inputErrors.bankAccount && <p className="error-message">{inputErrors.bankAccount}</p>}
                  </div>
                  
                  <div className="form-group">
                    <label>예금주명 *</label>
                    <input 
                      type="text" 
                      value={formData.accountHolder}
                      onChange={e => updateFormData('accountHolder', e.target.value)}
                      placeholder="홍길동"
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 단계 5: 가입 완료 */}
          {currentStep === 5 && (
            <div className="step-content completion">
              <div className="completion-icon">🎉</div>
              <h3>가입 신청이 완료되었습니다!</h3>
              <p>선택하신 상품: <strong>{formData.selectedProduct?.name}</strong></p>
              <p>가입자: <strong>{formData.name}</strong>님</p>
              <div className="completion-info">
                <h4>다음 단계</h4>
                <ul>
                  <li>📧 가입 신청 확인 이메일을 발송했습니다</li>
                  <li>📞 영업일 기준 1-2일 내 담당자가 연락드립니다</li>
                  <li>📋 필요 시 추가 서류를 요청할 수 있습니다</li>
                  <li>✅ 심사 완료 후 보험증권을 발행합니다</li>
                </ul>
              </div>
              <div className="completion-actions">
                <button className="btn-primary" onClick={handleClose}>확인</button>
              </div>
            </div>
          )}
        </div>

        {/* 하단 버튼 영역 */}
        {currentStep < 5 && (
          <div className="insurance-modal-footer">
            <div className="footer-buttons">
              {currentStep > 1 && (
                <button className="btn-secondary" onClick={goToPrevStep}>
                  이전
                </button>
              )}
              
              {currentStep < 4 && (
                <button 
                  className="btn-primary" 
                  onClick={goToNextStep}
                  disabled={!isCurrentStepValid()}
                >
                  다음
                </button>
              )}
              
              {currentStep === 4 && (
                <button 
                  className="btn-primary" 
                  onClick={handleSubscription}
                  disabled={!isCurrentStepValid() || isLoading}
                >
                  {isLoading ? '처리 중...' : '가입 신청'}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default InsuranceSubscriptionModal; 