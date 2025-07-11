/**
 * 감정 표시 컴포넌트
 * 사용자의 감정 상태를 시각적으로 표시
 */

import React from 'react';

// 감정별 설정
const EMOTION_CONFIG = {
  '긍정': { emoji: '😊', color: '#4CAF50', bgColor: '#E8F5E8' },
  '부정': { emoji: '😔', color: '#FF9800', bgColor: '#FFF3E0' },
  '불만': { emoji: '😤', color: '#F44336', bgColor: '#FFEBEE' },
  '분노': { emoji: '😠', color: '#D32F2F', bgColor: '#FFCDD2' },
  '불안': { emoji: '😰', color: '#9C27B0', bgColor: '#F3E5F5' },
  '중립': { emoji: '😐', color: '#607D8B', bgColor: '#ECEFF1' },
  '기쁨': { emoji: '😄', color: '#4CAF50', bgColor: '#E8F5E8' },
  '슬픔': { emoji: '😢', color: '#2196F3', bgColor: '#E3F2FD' },
  '놀람': { emoji: '😲', color: '#FF9800', bgColor: '#FFF3E0' },
  '만족': { emoji: '😌', color: '#4CAF50', bgColor: '#E8F5E8' },
  '실망': { emoji: '😞', color: '#FF5722', bgColor: '#FBE9E7' }
};

/**
 * 감정 표시기 컴포넌트
 * @param {Object} emotion - 감정 객체 {emotion: string, confidence: number, intensity?: number}
 * @param {boolean} compact - 컴팩트 모드 여부
 */
function EmotionIndicator({ emotion, compact = false }) {
  if (!emotion || !emotion.emotion) {
    return null;
  }

  const config = EMOTION_CONFIG[emotion.emotion] || EMOTION_CONFIG['중립'];
  const confidence = emotion.confidence || 0;
  const intensity = emotion.intensity || 0;

  // 신뢰도를 백분율로 변환
  const confidencePercent = Math.round(confidence * 100);
  
  // 강도에 따른 크기 조정
  const sizeMultiplier = compact ? 0.8 : (1 + intensity * 0.3);
  
  // 신뢰도에 따른 투명도 조정
  const opacity = Math.max(0.5, confidence);

  const style = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: compact ? '4px' : '8px',
    padding: compact ? '4px 8px' : '8px 12px',
    backgroundColor: config.bgColor,
    color: config.color,
    borderRadius: compact ? '12px' : '16px',
    fontSize: compact ? '12px' : '14px',
    fontWeight: '500',
    border: `1px solid ${config.color}20`,
    opacity: opacity,
    transform: `scale(${sizeMultiplier})`,
    transition: 'all 0.3s ease'
  };

  const emojiStyle = {
    fontSize: compact ? '14px' : '18px',
    marginRight: compact ? '2px' : '4px'
  };

  return (
    <div className={`emotion-indicator ${compact ? 'compact' : ''}`} style={style}>
      <span style={emojiStyle}>{config.emoji}</span>
      <span className="emotion-text">
        {emotion.emotion}
        {!compact && confidencePercent >= 70 && (
          <span className="confidence"> ({confidencePercent}%)</span>
        )}
      </span>
      
      {!compact && intensity > 0 && (
        <div className="intensity-bar">
          <div 
            className="intensity-fill"
            style={{
              width: `${intensity * 100}%`,
              height: '3px',
              backgroundColor: config.color,
              borderRadius: '2px',
              marginTop: '2px'
            }}
          />
        </div>
      )}
    </div>
  );
}

/**
 * 감정 히스토리 표시 컴포넌트
 * @param {Array} emotions - 감정 히스토리 배열
 * @param {number} limit - 표시할 최대 개수
 */
export function EmotionHistory({ emotions = [], limit = 5 }) {
  if (!emotions.length) {
    return null;
  }

  const recentEmotions = emotions.slice(-limit);

  return (
    <div className="emotion-history">
      <h4>감정 변화</h4>
      <div className="emotion-timeline">
        {recentEmotions.map((emotion, index) => (
          <EmotionIndicator 
            key={index} 
            emotion={emotion} 
            compact={true}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * 감정 통계 표시 컴포넌트
 * @param {Array} emotions - 감정 히스토리 배열
 */
export function EmotionStats({ emotions = [] }) {
  if (!emotions.length) {
    return null;
  }

  // 감정별 빈도 계산
  const emotionCounts = emotions.reduce((acc, emotion) => {
    const name = emotion.emotion || '중립';
    acc[name] = (acc[name] || 0) + 1;
    return acc;
  }, {});

  // 가장 빈번한 감정
  const dominantEmotion = Object.entries(emotionCounts)
    .sort(([,a], [,b]) => b - a)[0];

  // 평균 신뢰도 계산
  const avgConfidence = emotions.reduce((sum, emotion) => sum + (emotion.confidence || 0), 0) / emotions.length;

  return (
    <div className="emotion-stats">
      <h4>감정 분석 요약</h4>
      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-label">주요 감정:</span>
          <EmotionIndicator 
            emotion={{ emotion: dominantEmotion[0] }} 
            compact={true}
          />
        </div>
        <div className="stat-item">
          <span className="stat-label">분석 정확도:</span>
          <span className="stat-value">{Math.round(avgConfidence * 100)}%</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">감정 변화:</span>
          <span className="stat-value">{Object.keys(emotionCounts).length}가지</span>
        </div>
      </div>
    </div>
  );
}

export default EmotionIndicator; 