import React, { useState, useMemo } from 'react';
import './CoverageComparison.css';

const CoverageComparison = ({ 
  products = [], 
  insuranceType = 'auto',
  onProductSelect = null,
  showPremium = true,
  maxProducts = 3 
}) => {
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [sortBy, setSortBy] = useState('premium');
  const [filterBy, setFilterBy] = useState('all');

  // 보험 타입별 보장 항목 정의
  const coverageItems = useMemo(() => {
    switch (insuranceType) {
      case 'auto':
        return [
          { key: 'bodily_injury', name: '대인배상', icon: '👥', unit: '억원' },
          { key: 'property_damage', name: '대물배상', icon: '🚗', unit: '억원' },
          { key: 'self_damage', name: '자차손해', icon: '🔧', unit: '만원' },
          { key: 'personal_injury', name: '자손사고', icon: '🏥', unit: '만원' },
          { key: 'uninsured_motorist', name: '무보험차상해', icon: '⚠️', unit: '만원' },
          { key: 'emergency_service', name: '긴급출동서비스', icon: '🚨', unit: '회' },
          { key: 'rental_car', name: '대차비용', icon: '🚙', unit: '일' },
          { key: 'legal_support', name: '법률지원', icon: '⚖️', unit: '만원' }
        ];
      case 'health':
        return [
          { key: 'hospitalization', name: '입원비', icon: '🏥', unit: '만원' },
          { key: 'surgery', name: '수술비', icon: '🔬', unit: '만원' },
          { key: 'cancer_treatment', name: '암치료비', icon: '🎗️', unit: '만원' },
          { key: 'emergency_room', name: '응급실비용', icon: '🚨', unit: '만원' },
          { key: 'prescription_drugs', name: '처방약비', icon: '💊', unit: '만원' },
          { key: 'dental_care', name: '치과치료', icon: '🦷', unit: '만원' },
          { key: 'vision_care', name: '안과치료', icon: '👁️', unit: '만원' },
          { key: 'mental_health', name: '정신건강', icon: '🧠', unit: '만원' }
        ];
      case 'life':
        return [
          { key: 'death_benefit', name: '사망보험금', icon: '💼', unit: '억원' },
          { key: 'disability_benefit', name: '장애보험금', icon: '♿', unit: '만원' },
          { key: 'critical_illness', name: '중대질병', icon: '💊', unit: '만원' },
          { key: 'accident_benefit', name: '상해보험금', icon: '🩹', unit: '만원' },
          { key: 'hospitalization_benefit', name: '입원급여금', icon: '🏥', unit: '만원' },
          { key: 'surgery_benefit', name: '수술급여금', icon: '🔬', unit: '만원' },
          { key: 'family_benefit', name: '가족보장', icon: '👨‍👩‍👧‍👦', unit: '만원' },
          { key: 'education_benefit', name: '교육자금', icon: '🎓', unit: '만원' }
        ];
      case 'travel':
        return [
          { key: 'medical_expenses', name: '의료비', icon: '🏥', unit: '만원' },
          { key: 'emergency_evacuation', name: '긴급후송', icon: '🚁', unit: '만원' },
          { key: 'trip_cancellation', name: '여행취소', icon: '✈️', unit: '만원' },
          { key: 'baggage_loss', name: '수하물분실', icon: '🧳', unit: '만원' },
          { key: 'travel_delay', name: '여행지연', icon: '⏰', unit: '만원' },
          { key: 'personal_liability', name: '배상책임', icon: '⚖️', unit: '만원' },
          { key: 'rental_car_damage', name: '렌터카손해', icon: '🚗', unit: '만원' },
          { key: 'sports_coverage', name: '스포츠보장', icon: '🏂', unit: '만원' }
        ];
      default:
        return [];
    }
  }, [insuranceType]);

  // 제품 정렬 및 필터링
  const filteredAndSortedProducts = useMemo(() => {
    let filtered = [...products];
    
    if (filterBy !== 'all') {
      filtered = filtered.filter(product => 
        product.category === filterBy || product.popularityBadge
      );
    }

    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'premium':
          return parseFloat(a.monthlyPremium?.replace(/[^0-9]/g, '') || 0) - 
                 parseFloat(b.monthlyPremium?.replace(/[^0-9]/g, '') || 0);
        case 'coverage':
          return (b.coverageAmount?.replace(/[^0-9]/g, '') || 0) - 
                 (a.coverageAmount?.replace(/[^0-9]/g, '') || 0);
        case 'rating':
          return (b.rating || 0) - (a.rating || 0);
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

    return filtered.slice(0, maxProducts);
  }, [products, sortBy, filterBy, maxProducts]);

  const handleProductToggle = (productId) => {
    setSelectedProducts(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      } else if (prev.length < maxProducts) {
        return [...prev, productId];
      }
      return prev;
    });
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

  const formatCoverageValue = (product, item) => {
    const coverage = product.coverage?.[item.key] || product[item.key];
    
    if (!coverage) return '미보장';
    if (coverage === true) return '보장';
    if (coverage === false) return '미보장';
    if (typeof coverage === 'string') return coverage;
    if (typeof coverage === 'number') return `${coverage.toLocaleString()}${item.unit}`;
    
    return '미보장';
  };

  const getCoverageLevel = (product, item) => {
    const coverage = product.coverage?.[item.key] || product[item.key];
    
    if (!coverage || coverage === false) return 'none';
    if (coverage === true) return 'basic';
    
    const value = parseFloat(coverage.toString().replace(/[^0-9]/g, ''));
    if (value === 0) return 'none';
    if (value <= 100) return 'basic';
    if (value <= 500) return 'standard';
    if (value <= 1000) return 'premium';
    return 'platinum';
  };

  const getLevelColor = (level) => {
    const colors = {
      none: '#f5f5f5',
      basic: '#e3f2fd',
      standard: '#fff3e0',
      premium: '#f3e5f5',
      platinum: '#e8f5e8'
    };
    return colors[level] || colors.none;
  };

  const getLevelIcon = (level) => {
    const icons = {
      none: '❌',
      basic: '⭐',
      standard: '⭐⭐',
      premium: '⭐⭐⭐',
      platinum: '👑'
    };
    return icons[level] || icons.none;
  };

  if (!products || products.length === 0) {
    return (
      <div className="coverage-comparison empty">
        <div className="empty-state">
          <span className="empty-icon">📊</span>
          <h3>비교할 상품이 없습니다</h3>
          <p>보험 상품을 선택하여 보장 내용을 비교해보세요</p>
        </div>
      </div>
    );
  }

  return (
    <div className="coverage-comparison">
      <div className="comparison-header">
        <div className="header-content">
          <h3 className="comparison-title">
            <span className="title-icon">{getInsuranceTypeIcon()}</span>
            {getInsuranceTypeName()} 보장 비교
          </h3>
          <p className="comparison-subtitle">
            {filteredAndSortedProducts.length}개 상품의 보장 내용을 한눈에 비교해보세요
          </p>
        </div>
        
        <div className="comparison-controls">
          <div className="control-group">
            <label htmlFor="sort-by">정렬</label>
            <select 
              id="sort-by"
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="control-select"
            >
              <option value="premium">보험료 낮은순</option>
              <option value="coverage">보장 높은순</option>
              <option value="rating">평점 높은순</option>
              <option value="name">이름순</option>
            </select>
          </div>
          
          <div className="control-group">
            <label htmlFor="filter-by">필터</label>
            <select 
              id="filter-by"
              value={filterBy} 
              onChange={(e) => setFilterBy(e.target.value)}
              className="control-select"
            >
              <option value="all">전체</option>
              <option value="popular">인기상품</option>
              <option value="premium">프리미엄</option>
              <option value="basic">기본형</option>
            </select>
          </div>
        </div>
      </div>

      <div className="comparison-table-container">
        <table className="comparison-table">
          <thead>
            <tr>
              <th className="coverage-header">보장 항목</th>
              {filteredAndSortedProducts.map((product) => (
                <th key={product.id} className="product-header">
                  <div className="product-header-content">
                    <div className="product-info">
                      <h4 className="product-name">{product.name}</h4>
                      {showPremium && (
                        <div className="product-premium">
                          {product.monthlyPremium}
                        </div>
                      )}
                      {product.popularityBadge && (
                        <span className="popular-badge">🔥 인기</span>
                      )}
                      {product.rating && (
                        <div className="product-rating">
                          {'★'.repeat(Math.floor(product.rating))} 
                          ({product.rating})
                        </div>
                      )}
                    </div>
                    
                    <div className="product-actions">
                      <button
                        className={`select-button ${
                          selectedProducts.includes(product.id) ? 'selected' : ''
                        }`}
                        onClick={() => handleProductToggle(product.id)}
                      >
                        {selectedProducts.includes(product.id) ? '✓ 선택됨' : '선택'}
                      </button>
                      
                      {onProductSelect && (
                        <button
                          className="subscribe-button"
                          onClick={() => onProductSelect(product)}
                        >
                          가입하기
                        </button>
                      )}
                    </div>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          
          <tbody>
            {coverageItems.map((item) => (
              <tr key={item.key} className="coverage-row">
                <td className="coverage-item">
                  <div className="item-info">
                    <span className="item-icon">{item.icon}</span>
                    <span className="item-name">{item.name}</span>
                  </div>
                </td>
                
                {filteredAndSortedProducts.map((product) => {
                  const level = getCoverageLevel(product, item);
                  const value = formatCoverageValue(product, item);
                  
                  return (
                    <td 
                      key={`${product.id}-${item.key}`} 
                      className={`coverage-cell level-${level}`}
                      style={{ backgroundColor: getLevelColor(level) }}
                    >
                      <div className="coverage-content">
                        <span className="coverage-level">{getLevelIcon(level)}</span>
                        <span className="coverage-value">{value}</span>
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedProducts.length > 0 && (
        <div className="selected-products-summary">
          <div className="summary-header">
            <h4 className="summary-title">
              <span className="summary-icon">📋</span>
              선택된 상품 ({selectedProducts.length}개)
            </h4>
            <button 
              className="clear-selection"
              onClick={() => setSelectedProducts([])}
            >
              선택 해제
            </button>
          </div>
          
          <div className="summary-content">
            <div className="summary-cards">
              {selectedProducts.map(productId => {
                const product = filteredAndSortedProducts.find(p => p.id === productId);
                if (!product) return null;
                
                return (
                  <div key={productId} className="summary-card">
                    <div className="card-header">
                      <h5 className="card-title">{product.name}</h5>
                      <span className="card-premium">{product.monthlyPremium}</span>
                    </div>
                    <div className="card-features">
                      {product.keyFeatures?.slice(0, 3).map((feature, index) => (
                        <span key={index} className="feature-tag">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
            
            <div className="summary-actions">
              <button 
                className="compare-detailed"
                onClick={() => console.log('상세 비교', selectedProducts)}
              >
                <span className="btn-icon">🔍</span>
                상세 비교하기
              </button>
              
              <button 
                className="get-quotes"
                onClick={() => console.log('견적 요청', selectedProducts)}
              >
                <span className="btn-icon">📊</span>
                견적 받기
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="coverage-legend">
        <h4 className="legend-title">보장 수준 안내</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-icon">❌</span>
            <span className="legend-text">미보장</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">⭐</span>
            <span className="legend-text">기본</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">⭐⭐</span>
            <span className="legend-text">표준</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">⭐⭐⭐</span>
            <span className="legend-text">프리미엄</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">👑</span>
            <span className="legend-text">플래티넘</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoverageComparison; 