import React, { useState, useMemo } from 'react';
import './ClaimGuide.css';

const ClaimGuide = ({ 
  insuranceType = 'auto',
  claimType = null,
  onContactSupport = null,
  onStartClaim = null 
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedClaimType, setSelectedClaimType] = useState(claimType);
  const [expandedFaq, setExpandedFaq] = useState(null);

  // 보험 타입별 청구 유형 정의
  const claimTypes = useMemo(() => {
    switch (insuranceType) {
      case 'auto':
        return [
          { id: 'collision', name: '교통사고', icon: '🚗', urgency: 'high', timeLimit: '3일 이내' },
          { id: 'theft', name: '도난/분실', icon: '🔓', urgency: 'high', timeLimit: '7일 이내' },
          { id: 'vandalism', name: '파손/낙서', icon: '🔨', urgency: 'medium', timeLimit: '30일 이내' },
          { id: 'natural_disaster', name: '자연재해', icon: '🌪️', urgency: 'medium', timeLimit: '30일 이내' },
          { id: 'glass_damage', name: '유리 파손', icon: '🪟', urgency: 'low', timeLimit: '60일 이내' },
          { id: 'other', name: '기타 손해', icon: '❓', urgency: 'low', timeLimit: '60일 이내' }
        ];
      case 'health':
        return [
          { id: 'emergency', name: '응급치료', icon: '🚨', urgency: 'high', timeLimit: '즉시' },
          { id: 'hospitalization', name: '입원', icon: '🏥', urgency: 'high', timeLimit: '3일 이내' },
          { id: 'surgery', name: '수술', icon: '🔬', urgency: 'high', timeLimit: '7일 이내' },
          { id: 'outpatient', name: '외래진료', icon: '👨‍⚕️', urgency: 'medium', timeLimit: '30일 이내' },
          { id: 'dental', name: '치과치료', icon: '🦷', urgency: 'low', timeLimit: '60일 이내' },
          { id: 'mental_health', name: '정신건강', icon: '🧠', urgency: 'medium', timeLimit: '30일 이내' }
        ];
      case 'life':
        return [
          { id: 'death', name: '사망보험금', icon: '💼', urgency: 'high', timeLimit: '30일 이내' },
          { id: 'disability', name: '장해보험금', icon: '♿', urgency: 'high', timeLimit: '30일 이내' },
          { id: 'critical_illness', name: '중대질병', icon: '💊', urgency: 'high', timeLimit: '30일 이내' },
          { id: 'accident', name: '상해보험금', icon: '🩹', urgency: 'medium', timeLimit: '60일 이내' },
          { id: 'hospitalization', name: '입원급여금', icon: '🏥', urgency: 'medium', timeLimit: '60일 이내' },
          { id: 'surgery', name: '수술급여금', icon: '🔬', urgency: 'medium', timeLimit: '60일 이내' }
        ];
      case 'travel':
        return [
          { id: 'medical_emergency', name: '응급의료', icon: '🚑', urgency: 'high', timeLimit: '즉시' },
          { id: 'trip_cancellation', name: '여행취소', icon: '✈️', urgency: 'high', timeLimit: '즉시' },
          { id: 'baggage_loss', name: '수하물분실', icon: '🧳', urgency: 'medium', timeLimit: '21일 이내' },
          { id: 'travel_delay', name: '여행지연', icon: '⏰', urgency: 'medium', timeLimit: '30일 이내' },
          { id: 'personal_liability', name: '배상책임', icon: '⚖️', urgency: 'high', timeLimit: '7일 이내' },
          { id: 'rental_car', name: '렌터카손해', icon: '🚗', urgency: 'medium', timeLimit: '30일 이내' }
        ];
      default:
        return [];
    }
  }, [insuranceType]);

  // 선택된 청구 유형에 따른 단계별 가이드
  const claimSteps = useMemo(() => {
    if (!selectedClaimType) return [];

    const commonSteps = [
      {
        title: '사고 신고',
        description: '사고 발생 시 즉시 신고하세요',
        icon: '📞',
        urgent: true,
        tasks: [
          '보험회사 고객센터 연락 (24시간 접수)',
          '사고 접수번호 확인',
          '담당자 연락처 메모'
        ],
        tips: [
          '가능한 한 빨리 신고할수록 좋습니다',
          '사고 접수번호는 반드시 기록해 두세요'
        ]
      },
      {
        title: '현장 대응',
        description: '현장에서 필요한 조치를 취하세요',
        icon: '📋',
        urgent: false,
        tasks: [],
        tips: []
      },
      {
        title: '서류 준비',
        description: '청구에 필요한 서류를 준비하세요',
        icon: '📄',
        urgent: false,
        tasks: [],
        tips: ['원본 서류를 분실하지 않도록 주의하세요', '사본도 함께 준비해 두면 좋습니다']
      },
      {
        title: '청구 신청',
        description: '준비된 서류로 보험금을 청구하세요',
        icon: '💰',
        urgent: false,
        tasks: [
          '보험금 청구서 작성',
          '필요 서류 첨부',
          '온라인 또는 방문 접수'
        ],
        tips: ['누락된 서류가 있으면 처리가 지연될 수 있습니다']
      },
      {
        title: '심사 및 지급',
        description: '심사 완료 후 보험금이 지급됩니다',
        icon: '✅',
        urgent: false,
        tasks: [
          '심사 진행 상황 확인',
          '추가 서류 제출 (필요시)',
          '보험금 수령 확인'
        ],
        tips: ['심사 기간은 보통 7-14일 소요됩니다']
      }
    ];

    // 청구 유형별 맞춤 단계
    switch (selectedClaimType) {
      case 'collision':
        commonSteps[1].tasks = [
          '경찰신고 (인명피해 시 필수)',
          '사고 현장 사진 촬영',
          '상대방 정보 확인',
          '목격자 연락처 확보'
        ];
        commonSteps[2].tasks = [
          '사고사실확인원',
          '수리견적서',
          '차량등록증 사본',
          '운전면허증 사본',
          '병원진단서 (부상시)'
        ];
        break;
      case 'hospitalization':
        commonSteps[1].tasks = [
          '병원 접수 및 진료',
          '담당의와 상담',
          '입원 절차 진행'
        ];
        commonSteps[2].tasks = [
          '진단서',
          '입원확인서',
          '의료비 영수증',
          '통장 사본',
          '신분증 사본'
        ];
        break;
      case 'death':
        commonSteps[1].tasks = [
          '사망신고 (관공서)',
          '장례 절차 진행'
        ];
        commonSteps[2].tasks = [
          '사망진단서',
          '가족관계증명서',
          '수익자 신분증',
          '통장 사본',
          '보험증권'
        ];
        break;
      case 'trip_cancellation':
        commonSteps[1].tasks = [
          '여행사/항공사 취소 신청',
          '취소 사유 증명서 발급 요청'
        ];
        commonSteps[2].tasks = [
          '여행계약서',
          '취소 확인서',
          '취소 사유 증명서',
          '결제 영수증',
          '신분증 사본'
        ];
        break;
      default:
        commonSteps[1].tasks = ['현장 상황 파악', '필요시 관련 기관 신고'];
        commonSteps[2].tasks = ['관련 증명서류', '영수증', '신분증 사본'];
    }

    return commonSteps;
  }, [selectedClaimType]);

  // 자주 묻는 질문
  const faqs = useMemo(() => [
    {
      question: '보험금 청구 시한이 지나면 어떻게 되나요?',
      answer: '보험금 청구 시한이 지나면 청구가 거절될 수 있습니다. 하지만 부득이한 사유가 있는 경우 개별적으로 검토됩니다. 가능한 한 빨리 연락주세요.'
    },
    {
      question: '서류를 분실했을 때는 어떻게 하나요?',
      answer: '분실된 서류는 발급기관에서 재발급 받을 수 있습니다. 병원 서류는 병원에서, 관공서 서류는 해당 기관에서 재발급 신청하세요.'
    },
    {
      question: '보험금은 언제 지급되나요?',
      answer: '서류가 완벽하게 접수된 후 보통 7-14일 이내에 지급됩니다. 복잡한 사안의 경우 더 오래 걸릴 수 있습니다.'
    },
    {
      question: '부분 손해도 보상받을 수 있나요?',
      answer: '가입하신 보험의 보장 범위 내에서 부분 손해도 보상 가능합니다. 자차보험이나 종합보험 가입자의 경우 더 넓은 보장을 받을 수 있습니다.'
    },
    {
      question: '다른 보험회사와 중복으로 가입했다면?',
      answer: '중복보험의 경우 각 보험회사에서 비례하여 보상합니다. 모든 보험회사에 중복 가입 사실을 알려주셔야 합니다.'
    }
  ], []);

  const getUrgencyColor = (urgency) => {
    const colors = {
      high: '#d32f2f',
      medium: '#f57c00',
      low: '#388e3c'
    };
    return colors[urgency] || colors.low;
  };

  const getUrgencyText = (urgency) => {
    const texts = {
      high: '긴급',
      medium: '보통',
      low: '여유'
    };
    return texts[urgency] || texts.low;
  };

  const getInsuranceTypeIcon = () => {
    const icons = {
      auto: '🚗',
      health: '🏥',
      life: '👨‍👩‍👧‍👦',
      travel: '✈️'
    };
    return icons[insuranceType] || '🛡️';
  };

  const getInsuranceTypeName = () => {
    const names = {
      auto: '자동차보험',
      health: '건강보험',
      life: '생명보험',
      travel: '여행보험'
    };
    return names[insuranceType] || '보험';
  };

  const handleClaimTypeSelect = (claimTypeId) => {
    setSelectedClaimType(claimTypeId);
    setActiveStep(0);
  };

  const handleStepClick = (stepIndex) => {
    setActiveStep(stepIndex);
  };

  const handleFaqToggle = (index) => {
    setExpandedFaq(expandedFaq === index ? null : index);
  };

  return (
    <div className="claim-guide">
      <div className="guide-header">
        <h3 className="guide-title">
          <span className="title-icon">{getInsuranceTypeIcon()}</span>
          {getInsuranceTypeName()} 보험금 청구 가이드
        </h3>
        <p className="guide-subtitle">
          단계별 안내에 따라 쉽고 빠르게 보험금을 청구하세요
        </p>
      </div>

      {!selectedClaimType ? (
        <div className="claim-type-selection">
          <h4 className="selection-title">
            <span className="selection-icon">📋</span>
            청구 유형을 선택해 주세요
          </h4>
          
          <div className="claim-types-grid">
            {claimTypes.map((type) => (
              <div
                key={type.id}
                className="claim-type-card"
                onClick={() => handleClaimTypeSelect(type.id)}
              >
                <div className="card-icon">{type.icon}</div>
                <div className="card-content">
                  <h5 className="card-title">{type.name}</h5>
                  <div className="card-meta">
                    <span 
                      className="urgency-badge"
                      style={{ backgroundColor: getUrgencyColor(type.urgency) }}
                    >
                      {getUrgencyText(type.urgency)}
                    </span>
                    <span className="time-limit">{type.timeLimit}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="claim-process">
          <div className="process-header">
            <button 
              className="back-button"
              onClick={() => setSelectedClaimType(null)}
            >
              ← 뒤로 가기
            </button>
            
            <div className="selected-type">
              <span className="type-icon">
                {claimTypes.find(t => t.id === selectedClaimType)?.icon}
              </span>
              <span className="type-name">
                {claimTypes.find(t => t.id === selectedClaimType)?.name}
              </span>
              <span className="type-limit">
                신고기한: {claimTypes.find(t => t.id === selectedClaimType)?.timeLimit}
              </span>
            </div>
          </div>

          <div className="steps-container">
            <div className="steps-navigation">
              {claimSteps.map((step, index) => (
                <div
                  key={index}
                  className={`step-nav-item ${index === activeStep ? 'active' : ''} ${
                    index < activeStep ? 'completed' : ''
                  }`}
                  onClick={() => handleStepClick(index)}
                >
                  <div className="step-number">
                    {index < activeStep ? '✓' : index + 1}
                  </div>
                  <div className="step-nav-content">
                    <span className="step-icon">{step.icon}</span>
                    <span className="step-title">{step.title}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="step-content">
              {claimSteps[activeStep] && (
                <div className="step-detail">
                  <div className="step-header">
                    <h4 className="step-title">
                      <span className="step-icon">{claimSteps[activeStep].icon}</span>
                      {claimSteps[activeStep].title}
                      {claimSteps[activeStep].urgent && (
                        <span className="urgent-badge">긴급</span>
                      )}
                    </h4>
                    <p className="step-description">
                      {claimSteps[activeStep].description}
                    </p>
                  </div>

                  {claimSteps[activeStep].tasks.length > 0 && (
                    <div className="step-tasks">
                      <h5 className="tasks-title">
                        <span className="tasks-icon">📝</span>
                        체크리스트
                      </h5>
                      <ul className="tasks-list">
                        {claimSteps[activeStep].tasks.map((task, taskIndex) => (
                          <li key={taskIndex} className="task-item">
                            <span className="task-checkbox">☐</span>
                            <span className="task-text">{task}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {claimSteps[activeStep].tips.length > 0 && (
                    <div className="step-tips">
                      <h5 className="tips-title">
                        <span className="tips-icon">💡</span>
                        유용한 팁
                      </h5>
                      <ul className="tips-list">
                        {claimSteps[activeStep].tips.map((tip, tipIndex) => (
                          <li key={tipIndex} className="tip-item">
                            {tip}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="step-actions">
                    {activeStep > 0 && (
                      <button
                        className="step-button prev"
                        onClick={() => setActiveStep(activeStep - 1)}
                      >
                        이전 단계
                      </button>
                    )}
                    
                    {activeStep < claimSteps.length - 1 ? (
                      <button
                        className="step-button next"
                        onClick={() => setActiveStep(activeStep + 1)}
                      >
                        다음 단계
                      </button>
                    ) : (
                      <button
                        className="step-button complete"
                        onClick={() => onStartClaim && onStartClaim(selectedClaimType)}
                      >
                        청구 신청하기
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="emergency-contact">
        <div className="contact-header">
          <h4 className="contact-title">
            <span className="contact-icon">🚨</span>
            긴급 연락처
          </h4>
        </div>
        <div className="contact-info">
          <div className="contact-item">
            <span className="contact-label">24시간 사고접수:</span>
            <a href="tel:1588-5114" className="contact-number">1588-5114</a>
          </div>
          <div className="contact-item">
            <span className="contact-label">고객센터:</span>
            <a href="tel:1588-1234" className="contact-number">1588-1234</a>
          </div>
          <div className="contact-item">
            <span className="contact-label">온라인 상담:</span>
            <button 
              className="contact-button"
              onClick={() => onContactSupport && onContactSupport()}
            >
              상담 신청
            </button>
          </div>
        </div>
      </div>

      <div className="faq-section">
        <h4 className="faq-title">
          <span className="faq-icon">❓</span>
          자주 묻는 질문
        </h4>
        
        <div className="faq-list">
          {faqs.map((faq, index) => (
            <div key={index} className="faq-item">
              <button
                className={`faq-question ${expandedFaq === index ? 'expanded' : ''}`}
                onClick={() => handleFaqToggle(index)}
              >
                <span className="question-text">{faq.question}</span>
                <span className="expand-icon">
                  {expandedFaq === index ? '−' : '+'}
                </span>
              </button>
              
              {expandedFaq === index && (
                <div className="faq-answer">
                  <p>{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ClaimGuide; 