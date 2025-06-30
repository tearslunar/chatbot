import os
import requests
from typing import Dict, List, Tuple
from datetime import datetime
import json

class EmotionAnalyzer:
    def __init__(self):
        self.api_key = os.environ.get("POTENSDOT_API_KEY")
        self.emotion_history = []
        
    def analyze_emotion(self, text: str) -> Dict:
        """감정 분석 - 감정 유형과 강도를 반환"""
        url = "https://ai.potens.ai/api/chat"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        prompt = f"""다음 문장의 감정을 분석해주세요.
        감정 유형: 긍정/부정/불만/분노/불안/중립/기쁨/슬픔/놀람
        감정 강도: 1-5 (1: 매우 약함, 5: 매우 강함)
        
        JSON 형태로 답변해주세요:
        {{"emotion": "감정유형", "intensity": 강도, "confidence": 신뢰도}}
        
        문장: {text}"""
        
        data = {"prompt": prompt}
        
        try:
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                result = resp.json()
                answer = result.get("answer") or result.get("content") or str(result)
                
                # JSON 파싱 시도
                try:
                    emotion_data = json.loads(answer)
                    emotion_data['timestamp'] = datetime.now().isoformat()
                    self.emotion_history.append(emotion_data)
                    return emotion_data
                except:
                    # JSON 파싱 실패 시 기본 형태로 반환
                    return {
                        "emotion": "중립",
                        "intensity": 3,
                        "confidence": 0.5,
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                return self._get_default_emotion()
        except:
            return self._get_default_emotion()
    
    def _get_default_emotion(self) -> Dict:
        return {
            "emotion": "중립",
            "intensity": 3,
            "confidence": 0.5,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_emotion_trend(self, window_size: int = 5) -> Dict:
        """최근 감정 변화 트렌드 분석"""
        if len(self.emotion_history) < 2:
            return {"trend": "stable", "change": 0}
        
        recent_emotions = self.emotion_history[-window_size:]
        
        # 감정 강도 변화 계산
        intensities = [e.get('intensity', 3) for e in recent_emotions]
        avg_intensity = sum(intensities) / len(intensities)
        
        # 부정적 감정 비율 계산
        negative_count = sum(1 for e in recent_emotions 
                           if e.get('emotion') in ['부정', '불만', '분노', '불안', '슬픔'])
        negative_ratio = negative_count / len(recent_emotions)
        
        return {
            "trend": "increasing" if negative_ratio > 0.6 else "stable" if negative_ratio > 0.3 else "decreasing",
            "negative_ratio": negative_ratio,
            "avg_intensity": avg_intensity,
            "recommendation": self._get_recommendation(negative_ratio, avg_intensity)
        }
    
    def _get_recommendation(self, negative_ratio: float, intensity: float) -> str:
        """감정 상태에 따른 권장사항"""
        if negative_ratio > 0.7 or intensity > 4:
            return "immediate_agent"
        elif negative_ratio > 0.5:
            return "suggest_agent"
        elif negative_ratio > 0.3:
            return "empathetic_response"
        else:
            return "normal_response"
    
    def is_escalation_needed(self) -> bool:
        """상담사 연결이 필요한지 판단"""
        trend = self.get_emotion_trend()
        return trend['recommendation'] in ['immediate_agent', 'suggest_agent']
    
    def get_emotion_summary(self) -> Dict:
        """감정 분석 요약"""
        if not self.emotion_history:
            return {"total_messages": 0, "dominant_emotion": "중립"}
        
        emotions = [e.get('emotion', '중립') for e in self.emotion_history]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        
        return {
            "total_messages": len(self.emotion_history),
            "dominant_emotion": dominant_emotion,
            "emotion_distribution": emotion_counts,
            "current_trend": self.get_emotion_trend()
        }

# 전역 인스턴스
emotion_analyzer = EmotionAnalyzer() 