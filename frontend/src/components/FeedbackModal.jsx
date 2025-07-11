/**
 * 피드백 모달 컴포넌트
 * 상담 종료 후 평점 및 피드백 수집
 */

import React, { useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL;

/**
 * 피드백 모달 컴포넌트
 * @param {string} sessionId - 세션 ID
 * @param {Function} onClose - 닫기 핸들러
 * @param {Function} onRestart - 재시작 핸들러
 */
function FeedbackModal({ sessionId, onClose, onRestart }) {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [category, setCategory] = useState('');

  // 평점별 이모지와 메시지
  const ratingConfig = {
    1: { emoji: '😤', message: '매우 불만족', color: '#f44336' },
    2: { emoji: '😔', message: '불만족', color: '#ff9800' },
    3: { emoji: '😐', message: '보통', color: '#ffc107' },
    4: { emoji: '😊', message: '만족', color: '#4caf50' },
    5: { emoji: '😍', message: '매우 만족', color: '#2196f3' }
  };

  // 피드백 카테고리
  const feedbackCategories = [
    { value: 'response_quality', label: '답변 품질' },
    { value: 'response_speed', label: '응답 속도' },
    { value: 'user_experience', label: '사용자 경험' },
    { value: 'problem_resolution', label: '문제 해결' },
    { value: 'technical_issue', label: '기술적 문제' },
    { value: 'other', label: '기타' }
  ];

  /**
   * 평점 제출 핸들러
   */
  const handleSubmit = async () => {
    if (!rating) {
      alert('평점을 선택해주세요.');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_URL}/chat/submit-rating`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          session_id: sessionId,
          rating: rating,
          feedback: feedback.trim(),
          category: category,
          timestamp: new Date().toISOString()
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSubmitted(true);
        
        // 3초 후 자동으로 모달 닫기
        setTimeout(() => {
          onClose();
        }, 3000);
      } else {
        throw new Error('평점 제출 실패');
      }
    } catch (error) {
      console.error('[피드백] 제출 오류:', error);
      alert('피드백 제출 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * 건너뛰기 핸들러
   */
  const handleSkip = () => {
    onClose();
  };

  if (submitted) {
    return (
      <div className="modal-overlay">
        <div className="feedback-modal submitted">
          <div className="success-content">
            <div className="success-icon">✅</div>
            <h3>피드백 감사합니다!</h3>
            <p>소중한 의견을 주셔서 감사합니다.</p>
            <p>더 나은 서비스를 위해 노력하겠습니다.</p>
            
            <div className="rating-display">
              <span className="submitted-rating">
                {ratingConfig[rating].emoji} {ratingConfig[rating].message}
              </span>
            </div>

            <div className="final-actions">
              <button 
                onClick={onRestart}
                className="restart-btn"
              >
                🔄 새 상담 시작
              </button>
              <button 
                onClick={onClose}
                className="close-btn"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay">
      <div className="feedback-modal">
        <div className="modal-header">
          <h3>상담 만족도 평가</h3>
          <p>오늘 상담은 어떠셨나요? 솔직한 평가를 남겨주세요.</p>
        </div>

        <div className="modal-content">
          {/* 평점 선택 */}
          <div className="rating-section">
            <h4>만족도를 선택해주세요</h4>
            <div className="rating-stars">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  className={`rating-star ${
                    star <= (hoveredRating || rating) ? 'active' : ''
                  }`}
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHoveredRating(star)}
                  onMouseLeave={() => setHoveredRating(0)}
                  style={{
                    color: star <= (hoveredRating || rating) 
                      ? ratingConfig[star]?.color 
                      : '#ddd'
                  }}
                >
                  ⭐
                </button>
              ))}
            </div>
            
            {(hoveredRating || rating) > 0 && (
              <div className="rating-feedback">
                <span className="rating-emoji">
                  {ratingConfig[hoveredRating || rating]?.emoji}
                </span>
                <span className="rating-text">
                  {ratingConfig[hoveredRating || rating]?.message}
                </span>
              </div>
            )}
          </div>

          {/* 피드백 카테고리 */}
          {rating > 0 && (
            <div className="category-section">
              <h4>어떤 부분에 대한 평가인가요?</h4>
              <div className="category-options">
                {feedbackCategories.map((cat) => (
                  <label key={cat.value} className="category-option">
                    <input
                      type="radio"
                      name="category"
                      value={cat.value}
                      checked={category === cat.value}
                      onChange={(e) => setCategory(e.target.value)}
                    />
                    <span>{cat.label}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* 상세 피드백 */}
          {rating > 0 && (
            <div className="feedback-section">
              <h4>
                {rating <= 2 
                  ? '어떤 점이 아쉬우셨나요?' 
                  : '추가로 하실 말씀이 있으신가요?'
                }
                <span className="optional">(선택사항)</span>
              </h4>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder={
                  rating <= 2 
                    ? '개선이 필요한 부분을 알려주세요...'
                    : '좋았던 점이나 개선 아이디어를 자유롭게 작성해주세요...'
                }
                maxLength={500}
                rows={4}
                className="feedback-textarea"
              />
              <div className="character-count">
                {feedback.length}/500
              </div>
            </div>
          )}
        </div>

        <div className="modal-actions">
          <button 
            onClick={handleSkip}
            className="skip-btn"
            disabled={isSubmitting}
          >
            건너뛰기
          </button>
          <button
            onClick={handleSubmit}
            disabled={!rating || isSubmitting}
            className="submit-btn"
          >
            {isSubmitting ? '제출 중...' : '평가 완료'}
          </button>
        </div>

        {/* 세션 정보 */}
        <div className="session-info-footer">
          <small>세션 ID: {sessionId}</small>
        </div>
      </div>
    </div>
  );
}

/**
 * 간단한 평점 컴포넌트 (인라인 사용)
 * @param {Function} onRate - 평점 선택 핸들러
 * @param {number} value - 현재 평점
 */
export function QuickRating({ onRate, value = 0 }) {
  const [hovered, setHovered] = useState(0);

  return (
    <div className="quick-rating">
      <span>평가: </span>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          className={`quick-star ${star <= (hovered || value) ? 'active' : ''}`}
          onClick={() => onRate(star)}
          onMouseEnter={() => setHovered(star)}
          onMouseLeave={() => setHovered(0)}
        >
          ⭐
        </button>
      ))}
    </div>
  );
}

export default FeedbackModal; 