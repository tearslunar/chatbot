import os
import requests
from typing import Dict, List, Tuple
from datetime import datetime
import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import re

# 욕설/부정어 사전 (간단 예시)
NEGATIVE_WORDS = list(set([
    '짜증', '화나', '빡쳐', '개같', '씨발', '좆', '미친', '죽겠', '엿같', '지랄', '존나', '개새', '병신', '꺼져', '싫어', '실망', '불만', '불안', '분노', '짜증나', '답답', '최악', '실수', '에러', '오류', '망했', '화났', '빡침', '짜증남', '짜증나요', '화나요', '화가', '짜증이', '짜증을', '화가나', '화가남', '화가나요', '짜증나네', '화나네', '짜증나서', '화나서', '짜증나니까', '화나니까'
]))

class EmotionAnalyzer:
    def __init__(self):
        self.api_key = os.environ.get("POTENSDOT_API_KEY")
        self.emotion_history = []
        self.last_raw_response = None  # 원본 응답 저장
        self.max_history = 100  # 최근 100개만 저장
        # 🚨 감정 강도 지속 모니터링 추가
        self.high_intensity_threshold = 4  # 강도 4 이상을 고강도로 판단
        self.consecutive_high_intensity_limit = 3  # 연속 3회 이상이면 상담 종료
        self.session_termination_triggered = False  # 세션 종료 트리거 상태
        
    def analyze_emotion(self, text: str) -> Dict:
        """
        감정 분석 - 감정 유형과 강도를 반환
        욕설/부정어 사전 기반 보정, threshold 조정, 원본 응답 저장 및 로그 출력 포함
        """
        url = "https://ai.potens.ai/api/chat"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        prompt = f"""다음 문장의 감정을 분석해주세요.
        감정 유형: 긍정/부정/불만/분노/불안/중립/기쁨/슬픔/놀람
        감정 강도: 1-5 (1: 매우 약함, 5: 매우 강함)
        
        아래 형태로 답변해주세요:
        {{"emotion": "감정유형", "intensity": 강도, "confidence": 신뢰도}}
        
        문장: {text}"""
        
        data = {"prompt": prompt}
        
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=15)
            self.last_raw_response = resp.text  # 원본 응답 저장
            if resp.status_code == 200:
                result = resp.json()
                answer = result.get("answer") or result.get("content") or result.get("message") or str(result)
                
                # JSON 파싱 시도
                cleaned_answer = answer.strip()
                match = re.search(r'```json\s*(\{.*?\})\s*```', cleaned_answer, re.DOTALL)
                if match:
                    cleaned_answer = match.group(1)
                else:
                    # 혹시 다른 코드블록(``` ... ```)만 있을 때도 처리
                    match = re.search(r'```\s*(\{.*?\})\s*```', cleaned_answer, re.DOTALL)
                    if match:
                        cleaned_answer = match.group(1)
                try:
                    emotion_data = json.loads(cleaned_answer.strip())
                except Exception:
                    return self._get_default_emotion()
                # 욕설/부정어 사전 기반 보정
                if any(word in text for word in NEGATIVE_WORDS):
                    emotion_data['emotion'] = '분노'
                    emotion_data['intensity'] = 5
                    emotion_data['confidence'] = 0.99
                # threshold 조정: 부정/불만/분노/불안 등은 intensity 4 이상으로 보정
                if emotion_data.get('emotion') in ['부정', '불만', '분노', '불안', '슬픔'] and emotion_data.get('intensity', 3) < 4:
                    emotion_data['intensity'] = 4
                emotion_data['timestamp'] = datetime.now().isoformat()
                self.emotion_history.append(emotion_data)
                if len(self.emotion_history) > self.max_history:
                    self.emotion_history = self.emotion_history[-self.max_history:]
                return emotion_data
            else:
                return self._get_default_emotion()
        except Exception:
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
            return {"trend": "stable", "change": 0, "recommendation": "normal_response"}
        
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

    # 🚨 감정 강도 지속 모니터링 및 자동 상담 종료 기능
    def check_consecutive_high_intensity(self) -> Dict:
        """연속 고강도 감정 체크"""
        if len(self.emotion_history) < self.consecutive_high_intensity_limit:
            return {
                "consecutive_count": 0,
                "requires_termination": False,
                "intensity_pattern": []
            }
        
        # 최근 N개 메시지의 감정 강도 확인
        recent_emotions = self.emotion_history[-self.consecutive_high_intensity_limit:]
        intensity_pattern = [e.get('intensity', 3) for e in recent_emotions]
        
        # 모두 고강도(4 이상)인지 확인
        consecutive_high_count = 0
        for intensity in intensity_pattern:
            if intensity >= self.high_intensity_threshold:
                consecutive_high_count += 1
            else:
                consecutive_high_count = 0  # 연속성이 끊어지면 리셋
        
        requires_termination = consecutive_high_count >= self.consecutive_high_intensity_limit
        
        return {
            "consecutive_count": consecutive_high_count,
            "requires_termination": requires_termination,
            "intensity_pattern": intensity_pattern,
            "recent_emotions": [e.get('emotion') for e in recent_emotions]
        }

    def should_terminate_session(self) -> bool:
        """세션 종료가 필요한지 판단"""
        if self.session_termination_triggered:
            return False  # 이미 종료 트리거된 경우 중복 방지
        
        high_intensity_check = self.check_consecutive_high_intensity()
        
        if high_intensity_check["requires_termination"]:
            self.session_termination_triggered = True
            return True
        
        return False

    def get_termination_message(self) -> str:
        """상담 종료 안내 메시지 생성"""
        if not self.session_termination_triggered:
            return ""
        
        high_intensity_check = self.check_consecutive_high_intensity()
        recent_emotions = high_intensity_check.get("recent_emotions", [])
        
        return f"""

🚨 **중요 안내** 🚨

고객님의 감정 상태를 지속적으로 모니터링한 결과, 높은 강도의 감정({', '.join(recent_emotions)})이 연속으로 감지되었습니다.

더 전문적이고 신속한 해결을 위해 **상담사와의 직접 상담**을 강력히 권장드립니다.

**즉시 상담사 연결 방법:**
📞 고객센터: 1588-5656
💬 채팅 상담사 연결 버튼 클릭
🌐 온라인 상담 신청

AI 상담으로는 한계가 있는 복잡한 상황으로 판단됩니다. 
전문 상담사가 고객님의 문제를 더 정확하고 빠르게 해결해드릴 수 있습니다. ☀️

**상담이 자동으로 종료됩니다. 언제든 다시 시작하실 수 있습니다.**
"""

    def reset_termination_state(self):
        """종료 상태 리셋 (새 세션 시작 시 사용)"""
        self.session_termination_triggered = False

# 전역 인스턴스
emotion_analyzer = EmotionAnalyzer()

emotion_router = APIRouter()

@emotion_router.post("/emotion-analyze-async")
async def emotion_analyze_async(request: Request):
    data = await request.json()
    text = data.get("text", "")
    result = emotion_analyzer.analyze_emotion(text)
    return JSONResponse(content=result)

@emotion_router.post("/emotion-history-reset")
async def emotion_history_reset():
    emotion_analyzer.emotion_history = []
    emotion_analyzer.reset_termination_state()  # 🚨 종료 상태도 함께 리셋
    return JSONResponse(content={"result": "ok"})

@emotion_router.get("/emotion-intensity-status")
async def emotion_intensity_status():
    """현재 감정 강도 지속 상태 확인"""
    high_intensity_check = emotion_analyzer.check_consecutive_high_intensity()
    trend = emotion_analyzer.get_emotion_trend()
    
    return JSONResponse(content={
        "consecutive_high_intensity": high_intensity_check,
        "emotion_trend": trend,
        "termination_triggered": emotion_analyzer.session_termination_triggered,
        "recent_emotions": emotion_analyzer.emotion_history[-5:] if emotion_analyzer.emotion_history else [],
        "risk_level": "high" if high_intensity_check.get("consecutive_count", 0) >= 2 else "medium" if high_intensity_check.get("consecutive_count", 0) >= 1 else "low"
    }) 