import React from 'react';
import './InsuranceInfoCard.css';

const InsuranceInfoCard = ({ 
  product, 
  showComparison = false, 
  onCalculatePremium = null,
  onViewDetails = null,
  onSubscribe = null 
}) => {
  if (!product) return null;

  const {
    id,
    name,
    category,
    categoryIcon,
    monthlyPremium,
    coverageAmount,
    keyFeatures = [],
    specialBenefits = [],
    ageRange,
    conditions = [],
    discounts = [],
    rating = 0,
    popularityBadge = false
  } = product;

  const handleCalculatePremium = () => {
    if (onCalculatePremium) {
      onCalculatePremium(product);
    }
  };

  const handleViewDetails = () => {
    if (onViewDetails) {
      onViewDetails(product);
    }
  };

  const handleSubscribe = () => {
    if (onSubscribe) {
      onSubscribe(product);
    }
  };

  return (
    <div className="insurance-info-card" data-product-id={id}>
      {popularityBadge && (
        <div className="popularity-badge">
          🔥 인기 상품
        </div>
      )}
      
      <div className="card-header">
        <div className="category-info">
          <span className="category-icon">{categoryIcon}</span>
          <span className="category-name">{category}</span>
        </div>
        {rating > 0 && (
          <div className="rating">
            <span className="rating-stars">
              {'★'.repeat(Math.floor(rating))}{'☆'.repeat(5 - Math.floor(rating))}
            </span>
            <span className="rating-number">({rating})</span>
          </div>
        )}
      </div>

      <div className="card-body">
        <h3 className="product-name">{name}</h3>
        
        <div className="premium-info">
          <div className="monthly-premium">
            <span className="premium-label">월 보험료</span>
            <span className="premium-amount">{monthlyPremium}</span>
          </div>
          {coverageAmount && (
            <div className="coverage-amount">
              <span className="coverage-label">최대 보장</span>
              <span className="coverage-value">{coverageAmount}</span>
            </div>
          )}
        </div>

        {ageRange && (
          <div className="age-range">
            <span className="age-icon">👤</span>
            <span className="age-text">가입 연령: {ageRange}</span>
          </div>
        )}

        {keyFeatures.length > 0 && (
          <div className="key-features">
            <h4 className="features-title">주요 보장</h4>
            <ul className="features-list">
              {keyFeatures.slice(0, 4).map((feature, index) => (
                <li key={index} className="feature-item">
                  <span className="feature-icon">✓</span>
                  <span className="feature-text">{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {specialBenefits.length > 0 && (
          <div className="special-benefits">
            <h4 className="benefits-title">특별 혜택</h4>
            <div className="benefits-tags">
              {specialBenefits.slice(0, 3).map((benefit, index) => (
                <span key={index} className="benefit-tag">
                  {benefit}
                </span>
              ))}
            </div>
          </div>
        )}

        {discounts.length > 0 && (
          <div className="discounts">
            <h4 className="discounts-title">할인 혜택</h4>
            <div className="discount-tags">
              {discounts.map((discount, index) => (
                <span key={index} className="discount-tag">
                  🎯 {discount}
                </span>
              ))}
            </div>
          </div>
        )}

        {conditions.length > 0 && (
          <div className="conditions">
            <h4 className="conditions-title">가입 조건</h4>
            <ul className="conditions-list">
              {conditions.slice(0, 2).map((condition, index) => (
                <li key={index} className="condition-item">
                  {condition}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="card-actions">
        {onCalculatePremium && (
          <button 
            className="action-btn calculate-btn"
            onClick={handleCalculatePremium}
          >
            <span className="btn-icon">🧮</span>
            <span className="btn-text">보험료 계산</span>
          </button>
        )}
        
        {onViewDetails && (
          <button 
            className="action-btn details-btn"
            onClick={handleViewDetails}
          >
            <span className="btn-icon">📋</span>
            <span className="btn-text">상세보기</span>
          </button>
        )}
        
        {onSubscribe && (
          <button 
            className="action-btn subscribe-btn"
            onClick={handleSubscribe}
          >
            <span className="btn-icon">🛡️</span>
            <span className="btn-text">가입하기</span>
          </button>
        )}
      </div>
    </div>
  );
};

// 여러 보험 상품을 비교하는 컴포넌트
const InsuranceComparison = ({ products = [], onProductSelect = null }) => {
  if (!products || products.length === 0) return null;

  return (
    <div className="insurance-comparison">
      <div className="comparison-header">
        <h3 className="comparison-title">
          <span className="comparison-icon">📊</span>
          보험 상품 비교
        </h3>
        <p className="comparison-subtitle">
          {products.length}개 상품을 비교해보세요
        </p>
      </div>
      
      <div className="comparison-cards">
        {products.map((product, index) => (
          <InsuranceInfoCard
            key={product.id || index}
            product={product}
            showComparison={true}
            onSubscribe={onProductSelect}
          />
        ))}
      </div>
    </div>
  );
};

export { InsuranceInfoCard, InsuranceComparison };
export default InsuranceInfoCard; 