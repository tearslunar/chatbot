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

  // compact 모드일 때 크기 고정, 투명도/흐림 제거
  const style = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    padding: '2px 6px',
    borderRadius: '12px',
    fontSize: '13px',
    fontWeight: '500',
    marginLeft: '8px',
    whiteSpace: 'nowrap',
    backgroundColor: config.bgColor,
    color: config.color,
    border: `1px solid ${config.color}20`,
    opacity: 1,
    filter: 'none',
    minHeight: '28px',
    minWidth: '28px',
    height: '28px',
    lineHeight: '24px',
  };
  const emojiStyle = {
    fontSize: '20px',
    marginRight: '4px',
    lineHeight: '24px',
  };
  return (
    <div className={`emotion-indicator compact`} style={style}>
      <span style={emojiStyle}>{config.emoji}</span>
      <span className="emotion-text">{emotion.emotion}</span>
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