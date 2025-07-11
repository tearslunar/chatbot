/**
 * 추천 FAQ 컴포넌트
 * 관련된 자주 묻는 질문들을 표시하고 선택할 수 있게 함
 */

import React, { useState } from 'react';

/**
 * 추천 FAQ 목록 컴포넌트
 * @param {Array} faqs - FAQ 배열
 * @param {Function} onQuestionSelect - 질문 선택 핸들러
 * @param {number} maxDisplay - 최대 표시 개수
 */
function RecommendedFAQs({ faqs = [], onQuestionSelect, maxDisplay = 3 }) {
  const [expanded, setExpanded] = useState(false);
  
  if (!faqs.length) {
    return null;
  }

  const displayFaqs = expanded ? faqs : faqs.slice(0, maxDisplay);
  const hasMore = faqs.length > maxDisplay;

  const handleQuestionClick = (question) => {
    if (onQuestionSelect) {
      onQuestionSelect(question);
    }
  };

  return (
    <div className="recommended-faqs">
      <div className="faqs-header">
        <h4>💡 관련 질문</h4>
        <span className="faqs-count">({faqs.length}개)</span>
      </div>
      
      <div className="faqs-list">
        {displayFaqs.map((faq, index) => (
          <FAQItem
            key={index}
            faq={faq}
            onSelect={handleQuestionClick}
            index={index}
          />
        ))}
      </div>

      {hasMore && (
        <button 
          className="faqs-toggle"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? (
            <>접기 ▲</>
          ) : (
            <>더 보기 ({faqs.length - maxDisplay}개 더) ▼</>
          )}
        </button>
      )}
    </div>
  );
}

/**
 * 개별 FAQ 아이템 컴포넌트
 * @param {Object} faq - FAQ 객체
 * @param {Function} onSelect - 선택 핸들러
 * @param {number} index - 인덱스
 */
function FAQItem({ faq, onSelect, index }) {
  const [showAnswer, setShowAnswer] = useState(false);
  
  const question = faq.question || faq.text || '';
  const answer = faq.answer || faq.response || '';
  const score = faq.score || 0;
  const category = faq.category || '일반';

  // 신뢰도 점수에 따른 색상
  const getScoreColor = (score) => {
    if (score >= 0.8) return '#4CAF50'; // 높음 - 초록
    if (score >= 0.6) return '#FF9800'; // 중간 - 주황
    return '#9E9E9E'; // 낮음 - 회색
  };

  // 카테고리별 이모지
  const getCategoryEmoji = (category) => {
    const emojiMap = {
      '자동차보험': '🚗',
      '건강보험': '🏥',
      '생명보험': '👥',
      '가입': '✍️',
      '보상': '💰',
      '변경': '🔄',
      '해지': '❌',
      '일반': '❓'
    };
    return emojiMap[category] || '❓';
  };

  return (
    <div className={`faq-item ${showAnswer ? 'expanded' : ''}`}>
      <div className="faq-question-wrapper">
        <button
          className="faq-question"
          onClick={() => onSelect(question)}
          title="클릭하여 이 질문을 입력창에 추가"
        >
          <span className="faq-index">{index + 1}.</span>
          <span className="faq-text">{question}</span>
          <span className="faq-select-icon">📤</span>
        </button>
        
        <div className="faq-meta">
          <span className="faq-category">
            {getCategoryEmoji(category)} {category}
          </span>
          <span 
            className="faq-score"
            style={{ color: getScoreColor(score) }}
            title={`관련도: ${Math.round(score * 100)}%`}
          >
            {Math.round(score * 100)}%
          </span>
          
          {answer && (
            <button
              className="faq-toggle"
              onClick={() => setShowAnswer(!showAnswer)}
              title="답변 보기/숨기기"
            >
              {showAnswer ? '▲' : '▼'}
            </button>
          )}
        </div>
      </div>

      {showAnswer && answer && (
        <div className="faq-answer">
          <div className="faq-answer-content">
            {answer.length > 200 ? (
              <>
                {answer.substring(0, 200)}...
                <button className="faq-read-more">더 보기</button>
              </>
            ) : (
              answer
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * FAQ 검색 컴포넌트
 * @param {Array} allFaqs - 전체 FAQ 목록
 * @param {Function} onResults - 검색 결과 핸들러
 */
export function FAQSearch({ allFaqs = [], onResults }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (term) => {
    if (!term.trim()) {
      onResults([]);
      return;
    }

    setIsSearching(true);
    
    try {
      // 간단한 텍스트 매칭 (실제로는 서버에서 벡터 검색)
      const filtered = allFaqs.filter(faq => 
        faq.question.toLowerCase().includes(term.toLowerCase()) ||
        (faq.answer && faq.answer.toLowerCase().includes(term.toLowerCase()))
      ).slice(0, 5);
      
      // 검색 결과에 점수 추가
      const scored = filtered.map(faq => ({
        ...faq,
        score: 0.8 // 임시 점수
      }));
      
      onResults(scored);
    } catch (error) {
      console.error('FAQ 검색 오류:', error);
      onResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    
    // 디바운싱
    clearTimeout(window.faqSearchTimeout);
    window.faqSearchTimeout = setTimeout(() => {
      handleSearch(value);
    }, 300);
  };

  return (
    <div className="faq-search">
      <div className="search-input-wrapper">
        <input
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          placeholder="FAQ 검색..."
          className="faq-search-input"
        />
        {isSearching && <span className="search-loading">🔍</span>}
      </div>
    </div>
  );
}

export default RecommendedFAQs; 