import React, { useState, useEffect } from 'react';
import './PremiumCalculator.css';

const PremiumCalculator = ({ 
  insuranceType = 'auto', 
  onCalculationComplete = null,
  onSubscribe = null,
  selectedPersona = null
}) => {
  const [formData, setFormData] = useState({
    // 공통 정보
    age: '',
    gender: '',
    occupation: '',
    region: '',
    
    // 자동차보험 관련
    vehicleType: '',
    vehicleAge: '',
    drivingExperience: '',
    accidentHistory: '',
    vehicleBrand: '',
    
    // 건강보험 관련
    height: '',
    weight: '',
    smokingStatus: '',
    drinkingStatus: '',
    medicalHistory: '',
    
    // 생명보험 관련
    insuranceAmount: '',
    familyMembers: '',
    
    // 여행보험 관련
    destination: '',
    travelDays: '',
    travelType: ''
  });

  const [calculationResult, setCalculationResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [discounts, setDiscounts] = useState([]);

  // 페르소나 정보가 있으면 자동으로 일부 필드 채우기
  useEffect(() => {
    if (selectedPersona) {
      const personaAge = selectedPersona['연령대'] || '';
      const personaGender = selectedPersona['성별'] || '';
      const personaOccupation = selectedPersona['직업'] || '';
      const personaVehicle = selectedPersona['차량 정보'] || '';
      
      setFormData(prev => ({
        ...prev,
        age: extractAgeFromRange(personaAge),
        gender: personaGender,
        occupation: personaOccupation,
        vehicleBrand: extractVehicleBrand(personaVehicle)
      }));
    }
  }, [selectedPersona]);

  const extractAgeFromRange = (ageRange) => {
    if (ageRange.includes('20대')) return '25';
    if (ageRange.includes('30대')) return '35';
    if (ageRange.includes('40대')) return '45';
    if (ageRange.includes('50대')) return '55';
    if (ageRange.includes('60대')) return '65';
    return '';
  };

  const extractVehicleBrand = (vehicleInfo) => {
    if (vehicleInfo.includes('현대')) return '현대';
    if (vehicleInfo.includes('기아')) return '기아';
    if (vehicleInfo.includes('테슬라')) return '테슬라';
    if (vehicleInfo.includes('벤츠')) return '벤츠';
    if (vehicleInfo.includes('BMW')) return 'BMW';
    return '';
  };

  const updateFormData = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const calculatePremium = async () => {
    setIsCalculating(true);
    
    try {
      // 간단한 클라이언트 사이드 계산 (실제로는 백엔드 API 호출)
      const result = performCalculation();
      setCalculationResult(result);
      
      if (onCalculationComplete) {
        onCalculationComplete(result);
      }
    } catch (error) {
      console.error('보험료 계산 오류:', error);
    } finally {
      setIsCalculating(false);
    }
  };

  const performCalculation = () => {
    let basePremium = 0;
    let discountRate = 0;
    let appliedDiscounts = [];

    switch (insuranceType) {
      case 'auto':
        basePremium = calculateAutoPremium();
        break;
      case 'health':
        basePremium = calculateHealthPremium();
        break;
      case 'life':
        basePremium = calculateLifePremium();
        break;
      case 'travel':
        basePremium = calculateTravelPremium();
        break;
      default:
        basePremium = 50000;
    }

    // 할인 계산
    const discountInfo = calculateDiscounts();
    discountRate = discountInfo.rate;
    appliedDiscounts = discountInfo.discounts;

    const finalPremium = Math.round(basePremium * (1 - discountRate / 100));
    const savings = basePremium - finalPremium;

    return {
      basePremium,
      finalPremium,
      discountRate,
      savings,
      appliedDiscounts,
      insuranceType
    };
  };

  const calculateAutoPremium = () => {
    let premium = 80000; // 기본 보험료
    
    const age = parseInt(formData.age);
    if (age < 26) premium += 20000;
    else if (age > 60) premium += 10000;
    else if (age >= 30 && age <= 50) premium -= 5000;

    if (formData.vehicleAge === '3년이상') premium += 15000;
    if (formData.drivingExperience === '1년미만') premium += 25000;
    if (formData.accidentHistory === '있음') premium += 30000;

    return premium;
  };

  const calculateHealthPremium = () => {
    let premium = 45000; // 기본 보험료
    
    const age = parseInt(formData.age);
    if (age > 50) premium += 20000;
    else if (age < 30) premium -= 5000;

    if (formData.smokingStatus === '흡연') premium += 15000;
    if (formData.medicalHistory === '있음') premium += 25000;

    const bmi = calculateBMI();
    if (bmi > 30 || bmi < 18) premium += 10000;

    return premium;
  };

  const calculateLifePremium = () => {
    let premium = 60000; // 기본 보험료
    
    const age = parseInt(formData.age);
    const amount = parseInt(formData.insuranceAmount) || 10000;
    
    premium = premium + (amount / 10000) * 5000;
    if (age > 50) premium *= 1.5;
    if (formData.familyMembers === '3명이상') premium += 20000;

    return premium;
  };

  const calculateTravelPremium = () => {
    let premium = 5000; // 기본 보험료 (일당)
    
    const days = parseInt(formData.travelDays) || 1;
    if (formData.destination === '해외') premium += 3000;
    if (formData.travelType === '모험여행') premium += 2000;

    return premium * days;
  };

  const calculateBMI = () => {
    const height = parseInt(formData.height);
    const weight = parseInt(formData.weight);
    if (height && weight) {
      return weight / ((height / 100) ** 2);
    }
    return 22; // 평균값
  };

  const calculateDiscounts = () => {
    let totalDiscount = 0;
    let discounts = [];

    // 연령 할인
    const age = parseInt(formData.age);
    if (age >= 30 && age <= 50) {
      totalDiscount += 5;
      discounts.push('우량연령 5% 할인');
    }

    // 브랜드 할인 (자동차보험)
    if (insuranceType === 'auto' && formData.vehicleBrand === '현대') {
      totalDiscount += 10;
      discounts.push('현대차 오너 10% 할인');
    }

    // 무사고 할인
    if (formData.accidentHistory === '없음') {
      totalDiscount += 15;
      discounts.push('무사고 우수고객 15% 할인');
    }

    // 건강 할인 (건강보험)
    if (insuranceType === 'health' && formData.smokingStatus === '비흡연') {
      totalDiscount += 10;
      discounts.push('비흡연자 10% 할인');
    }

    // 온라인 가입 할인
    totalDiscount += 5;
    discounts.push('온라인 가입 5% 할인');

    // 최대 할인율 제한
    totalDiscount = Math.min(totalDiscount, 35);

    return { rate: totalDiscount, discounts };
  };

  const isFormValid = () => {
    const requiredFields = ['age', 'gender'];
    
    switch (insuranceType) {
      case 'auto':
        requiredFields.push('vehicleType', 'drivingExperience');
        break;
      case 'health':
        requiredFields.push('height', 'weight');
        break;
      case 'life':
        requiredFields.push('insuranceAmount');
        break;
      case 'travel':
        requiredFields.push('destination', 'travelDays');
        break;
    }

    return requiredFields.every(field => formData[field]);
  };

  const getInsuranceTypeTitle = () => {
    const titles = {
      auto: '자동차보험',
      health: '건강보험',
      life: '생명보험',
      travel: '여행보험'
    };
    return titles[insuranceType] || '보험';
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

  const renderFormFields = () => {
    switch (insuranceType) {
      case 'auto':
        return renderAutoFields();
      case 'health':
        return renderHealthFields();
      case 'life':
        return renderLifeFields();
      case 'travel':
        return renderTravelFields();
      default:
        return null;
    }
  };

  const renderCommonFields = () => (
    <div className="form-section">
      <h4 className="section-title">기본 정보</h4>
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="age">나이</label>
          <input
            type="number"
            id="age"
            value={formData.age}
            onChange={(e) => updateFormData('age', e.target.value)}
            placeholder="나이를 입력하세요"
            min="18"
            max="80"
          />
        </div>
        <div className="form-field">
          <label htmlFor="gender">성별</label>
          <select
            id="gender"
            value={formData.gender}
            onChange={(e) => updateFormData('gender', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="남성">남성</option>
            <option value="여성">여성</option>
          </select>
        </div>
      </div>
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="occupation">직업</label>
          <input
            type="text"
            id="occupation"
            value={formData.occupation}
            onChange={(e) => updateFormData('occupation', e.target.value)}
            placeholder="직업을 입력하세요"
          />
        </div>
        <div className="form-field">
          <label htmlFor="region">거주지역</label>
          <select
            id="region"
            value={formData.region}
            onChange={(e) => updateFormData('region', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="서울">서울</option>
            <option value="경기">경기</option>
            <option value="부산">부산</option>
            <option value="기타">기타</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderAutoFields = () => (
    <div className="form-section">
      <h4 className="section-title">차량 정보</h4>
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="vehicleBrand">차량 브랜드</label>
          <select
            id="vehicleBrand"
            value={formData.vehicleBrand}
            onChange={(e) => updateFormData('vehicleBrand', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="현대">현대</option>
            <option value="기아">기아</option>
            <option value="테슬라">테슬라</option>
            <option value="벤츠">벤츠</option>
            <option value="BMW">BMW</option>
            <option value="기타">기타</option>
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="vehicleType">차량 종류</label>
          <select
            id="vehicleType"
            value={formData.vehicleType}
            onChange={(e) => updateFormData('vehicleType', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="경차">경차</option>
            <option value="소형차">소형차</option>
            <option value="중형차">중형차</option>
            <option value="대형차">대형차</option>
            <option value="SUV">SUV</option>
          </select>
        </div>
      </div>
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="vehicleAge">차량 연식</label>
          <select
            id="vehicleAge"
            value={formData.vehicleAge}
            onChange={(e) => updateFormData('vehicleAge', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="1년미만">1년 미만</option>
            <option value="1-3년">1-3년</option>
            <option value="3년이상">3년 이상</option>
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="drivingExperience">운전 경력</label>
          <select
            id="drivingExperience"
            value={formData.drivingExperience}
            onChange={(e) => updateFormData('drivingExperience', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="1년미만">1년 미만</option>
            <option value="1-3년">1-3년</option>
            <option value="3-5년">3-5년</option>
            <option value="5년이상">5년 이상</option>
          </select>
        </div>
      </div>
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="accidentHistory">사고 이력</label>
          <select
            id="accidentHistory"
            value={formData.accidentHistory}
            onChange={(e) => updateFormData('accidentHistory', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="없음">없음</option>
            <option value="1회">1회</option>
            <option value="2회이상">2회 이상</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderHealthFields = () => (
    <div className="form-section">
      <h4 className="section-title">건강 정보</h4>
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="height">신장 (cm)</label>
          <input
            type="number"
            id="height"
            value={formData.height}
            onChange={(e) => updateFormData('height', e.target.value)}
            placeholder="신장을 입력하세요"
            min="140"
            max="220"
          />
        </div>
        <div className="form-field">
          <label htmlFor="weight">체중 (kg)</label>
          <input
            type="number"
            id="weight"
            value={formData.weight}
            onChange={(e) => updateFormData('weight', e.target.value)}
            placeholder="체중을 입력하세요"
            min="30"
            max="200"
          />
        </div>
      </div>
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="smokingStatus">흡연 여부</label>
          <select
            id="smokingStatus"
            value={formData.smokingStatus}
            onChange={(e) => updateFormData('smokingStatus', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="비흡연">비흡연</option>
            <option value="흡연">흡연</option>
            <option value="금연">금연</option>
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="medicalHistory">병력</label>
          <select
            id="medicalHistory"
            value={formData.medicalHistory}
            onChange={(e) => updateFormData('medicalHistory', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="없음">없음</option>
            <option value="있음">있음</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderLifeFields = () => (
    <div className="form-section">
      <h4 className="section-title">보장 정보</h4>
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="insuranceAmount">보장 금액 (만원)</label>
          <select
            id="insuranceAmount"
            value={formData.insuranceAmount}
            onChange={(e) => updateFormData('insuranceAmount', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="10000">1억원</option>
            <option value="20000">2억원</option>
            <option value="30000">3억원</option>
            <option value="50000">5억원</option>
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="familyMembers">가족 구성원</label>
          <select
            id="familyMembers"
            value={formData.familyMembers}
            onChange={(e) => updateFormData('familyMembers', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="1명">1명</option>
            <option value="2명">2명</option>
            <option value="3명이상">3명 이상</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderTravelFields = () => (
    <div className="form-section">
      <h4 className="section-title">여행 정보</h4>
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="destination">여행지</label>
          <select
            id="destination"
            value={formData.destination}
            onChange={(e) => updateFormData('destination', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="국내">국내</option>
            <option value="해외">해외</option>
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="travelDays">여행 기간 (일)</label>
          <input
            type="number"
            id="travelDays"
            value={formData.travelDays}
            onChange={(e) => updateFormData('travelDays', e.target.value)}
            placeholder="여행 일수"
            min="1"
            max="365"
          />
        </div>
      </div>
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="travelType">여행 유형</label>
          <select
            id="travelType"
            value={formData.travelType}
            onChange={(e) => updateFormData('travelType', e.target.value)}
          >
            <option value="">선택하세요</option>
            <option value="관광여행">관광여행</option>
            <option value="비즈니스">비즈니스</option>
            <option value="모험여행">모험여행</option>
          </select>
        </div>
      </div>
    </div>
  );

  return (
    <div className="premium-calculator">
      <div className="calculator-header">
        <h3 className="calculator-title">
          <span className="calculator-icon">{getInsuranceTypeIcon()}</span>
          {getInsuranceTypeTitle()} 보험료 계산
        </h3>
        <p className="calculator-subtitle">
          간단한 정보 입력으로 예상 보험료를 확인해보세요
        </p>
      </div>

      <div className="calculator-form">
        {renderCommonFields()}
        {renderFormFields()}
      </div>

      <div className="calculator-actions">
        <button
          className="calculate-button"
          onClick={calculatePremium}
          disabled={!isFormValid() || isCalculating}
        >
          {isCalculating ? (
            <>
              <span className="loading-spinner">⏳</span>
              계산 중...
            </>
          ) : (
            <>
              <span className="btn-icon">🧮</span>
              보험료 계산하기
            </>
          )}
        </button>
      </div>

      {calculationResult && (
        <div className="calculation-result">
          <div className="result-header">
            <h4 className="result-title">
              <span className="result-icon">💰</span>
              보험료 계산 결과
            </h4>
          </div>

          <div className="result-content">
            <div className="premium-breakdown">
              <div className="premium-item">
                <span className="premium-label">기본 보험료</span>
                <span className="premium-value base">
                  {calculationResult.basePremium.toLocaleString()}원
                </span>
              </div>
              
              {calculationResult.discountRate > 0 && (
                <div className="premium-item discount">
                  <span className="premium-label">
                    할인율 ({calculationResult.discountRate}%)
                  </span>
                  <span className="premium-value discount">
                    -{calculationResult.savings.toLocaleString()}원
                  </span>
                </div>
              )}
              
              <div className="premium-item final">
                <span className="premium-label">최종 보험료</span>
                <span className="premium-value final">
                  {calculationResult.finalPremium.toLocaleString()}원
                </span>
              </div>
            </div>

            {calculationResult.appliedDiscounts.length > 0 && (
              <div className="applied-discounts">
                <h5 className="discounts-title">적용된 할인</h5>
                <ul className="discounts-list">
                  {calculationResult.appliedDiscounts.map((discount, index) => (
                    <li key={index} className="discount-item">
                      <span className="discount-icon">🎯</span>
                      <span className="discount-text">{discount}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="result-actions">
              <button
                className="action-btn save-quote"
                onClick={() => console.log('견적 저장')}
              >
                <span className="btn-icon">📋</span>
                견적 저장
              </button>
              
              {onSubscribe && (
                <button
                  className="action-btn subscribe-now"
                  onClick={() => onSubscribe(calculationResult)}
                >
                  <span className="btn-icon">🛡️</span>
                  바로 가입하기
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PremiumCalculator; 