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
        # 🚨 감정 격화 감지 및 상담 종료 권장 로직 (완화된 설정)
        self.high_intensity_threshold = 5  # 강도 5만을 고강도로 판단 (더 엄격하게)
        self.extreme_intensity_threshold = 5  # 강도 5는 극도로 격화된 상태
        self.consecutive_high_intensity_limit = 5  # 연속 5회 이상이면 상담 종료 권장 (더 관대하게)
        self.session_termination_triggered = False  # 세션 종료 트리거 상태
        self.termination_warning_given = False  # 종료 경고 발생 여부
        self.escalation_attempts = 0  # 에스컬레이션 시도 횟수
        self.cooling_down_attempts = 0  # 감정 완화 시도 횟수
        
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
                # threshold 조정: 강한 부정적 감정만 보정 (더 보수적으로)
                if emotion_data.get('emotion') in ['분노', '불만'] and emotion_data.get('intensity', 3) < 4:
                    emotion_data['intensity'] = 4
                    # 일반적인 부정/불안/슬픔은 자동 보정하지 않음
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
    def check_emotional_escalation(self) -> Dict:
        """감정 격화 상태 종합 분석"""
        if len(self.emotion_history) == 0:
            return {
                "escalation_level": "none",
                "consecutive_high_count": 0,
                "extreme_emotion_detected": False,
                "requires_intervention": False,
                "requires_termination": False,
                "intervention_type": "none"
            }
        
        # 최근 감정들 분석
        recent_window = min(5, len(self.emotion_history))
        recent_emotions = self.emotion_history[-recent_window:]
        
        # 1. 연속 고강도 감정 체크
        consecutive_high_count = 0
        current_streak = 0
        
        for emotion in reversed(recent_emotions):
            intensity = emotion.get('intensity', 3)
            if intensity >= self.high_intensity_threshold:
                current_streak += 1
            else:
                break
        
        consecutive_high_count = current_streak
        
        # 2. 극도 감정 상태 체크 (강도 5)
        extreme_emotion_detected = any(
            e.get('intensity', 3) >= self.extreme_intensity_threshold 
            for e in recent_emotions
        )
        
        # 3. 부정적 감정의 지속성 체크
        negative_emotions = ['분노', '불만', '불안', '슬픔', '부정']
        negative_count = sum(
            1 for e in recent_emotions 
            if e.get('emotion') in negative_emotions
        )
        negative_persistence = negative_count / len(recent_emotions)
        
        # 4. 평균 감정 강도
        avg_intensity = sum(e.get('intensity', 3) for e in recent_emotions) / len(recent_emotions)
        
        # 5. 에스컬레이션 레벨 결정
        escalation_level = "none"
        requires_intervention = False
        requires_termination = False
        intervention_type = "none"
        
        if extreme_emotion_detected and consecutive_high_count >= 3:
            escalation_level = "critical"
            requires_intervention = True
            if consecutive_high_count >= self.consecutive_high_intensity_limit:
                requires_termination = True
                intervention_type = "immediate_termination"
            else:
                intervention_type = "cooling_down"
                
        elif consecutive_high_count >= 4 or (negative_persistence > 0.8 and avg_intensity > 4.2):
            escalation_level = "high"
            requires_intervention = True
            intervention_type = "de_escalation"
            
        elif negative_persistence > 0.7 or avg_intensity > 4.0:
            escalation_level = "moderate"
            requires_intervention = True
            intervention_type = "empathy_boost"
        
        return {
            "escalation_level": escalation_level,
            "consecutive_high_count": consecutive_high_count,
            "extreme_emotion_detected": extreme_emotion_detected,
            "negative_persistence": negative_persistence,
            "avg_intensity": avg_intensity,
            "requires_intervention": requires_intervention,
            "requires_termination": requires_termination,
            "intervention_type": intervention_type,
            "recent_pattern": [
                {"emotion": e.get('emotion'), "intensity": e.get('intensity')} 
                for e in recent_emotions
            ]
        }

    def should_terminate_session(self) -> Dict:
        """세션 종료 필요성 및 개입 방식 판단 - 자동 종료 완전 비활성화"""
        escalation_analysis = self.check_emotional_escalation()
        
        # 🚨 자동 종료 완전 비활성화 - 항상 False 반환
        return {
            "should_terminate": False,
            "intervention_needed": False,
            "escalation_data": escalation_analysis
        }
    
    def get_intervention_message(self, escalation_data: Dict) -> str:
        """에스컬레이션 상황에 맞는 개입 메시지 생성"""
        intervention_type = escalation_data.get("intervention_type", "none")
        escalation_level = escalation_data.get("escalation_level", "none")
        
        if intervention_type == "immediate_termination":
            return self._get_immediate_termination_message()
        elif intervention_type == "cooling_down":
            return self._get_cooling_down_message()
        elif intervention_type == "de_escalation":
            return self._get_de_escalation_message()
        elif intervention_type == "empathy_boost":
            return self._get_empathy_message()
        
        return ""
    
    def _get_immediate_termination_message(self) -> str:
        """즉시 상담 종료 메시지"""
        messages = [
            "고객님의 감정이 많이 격해지신 것 같습니다. 보다 전문적인 상담을 위해 상담사와 직접 연결해드리겠습니다.",
            "현재 상황에 대해 깊이 이해하고 있으며, 더 나은 서비스를 위해 전문 상담사와의 통화를 권해드립니다.",
            "고객님의 소중한 의견을 충분히 반영하기 위해 상담사 연결 서비스를 이용해주시기 바랍니다."
        ]
        return random.choice(messages) + "\n\n📞 상담사 연결: 1588-5656 (평일 9시-18시)\n💬 채팅 상담: 고객센터 → 채팅 상담 신청"
    
    def _get_cooling_down_message(self) -> str:
        """감정 완화 메시지"""
        messages = [
            "고객님의 마음을 충분히 이해합니다. 잠시 시간을 두고 차근차근 해결책을 찾아보는 것이 어떨까요?",
            "현재 상황이 답답하시겠지만, 함께 단계별로 문제를 해결해보겠습니다.",
            "고객님의 어려움을 공감하며, 최선의 해결 방안을 찾아드리겠습니다."
        ]
        return random.choice(messages) + "\n\n원하시면 언제든 전문 상담사와 연결해드릴 수 있습니다."
    
    def _get_de_escalation_message(self) -> str:
        """상황 완화 메시지"""
        messages = [
            "고객님의 상황을 정확히 파악하여 도움을 드리고 싶습니다. 구체적으로 어떤 부분이 가장 문제가 되시는지 말씀해주시겠어요?",
            "불편을 끼쳐드려 정말 죄송합니다. 문제 해결을 위해 차근차근 접근해보겠습니다.",
            "고객님의 입장에서 충분히 이해됩니다. 보다 나은 해결책을 제시해드리겠습니다."
        ]
        return random.choice(messages)
    
    def _get_empathy_message(self) -> str:
        """공감 강화 메시지"""
        messages = [
            "고객님의 마음을 이해합니다. 더 자세한 안내를 위해 관련 정보를 확인해드리겠습니다.",
            "불편하셨던 점에 대해 진심으로 사과드립니다. 도움이 될 수 있는 방법을 찾아보겠습니다.",
            "고객님의 소중한 의견 감사합니다. 더 나은 서비스를 제공할 수 있도록 노력하겠습니다."
        ]
        return random.choice(messages)

    def get_termination_message(self) -> str:
        """상담 종료 안내 메시지 생성 (레거시 호환)"""
        return self._get_immediate_termination_message()
        
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
    escalation_analysis = emotion_analyzer.check_emotional_escalation()
    trend = emotion_analyzer.get_emotion_trend()
    
    return JSONResponse(content={
        "escalation_analysis": escalation_analysis,
        "emotion_trend": trend,
        "termination_triggered": emotion_analyzer.session_termination_triggered,
        "recent_emotions": emotion_analyzer.emotion_history[-5:] if emotion_analyzer.emotion_history else [],
        "risk_level": escalation_analysis.get("escalation_level", "none")
    }) 