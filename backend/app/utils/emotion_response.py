from typing import Dict, List
from backend.app.sentiment.advanced import emotion_analyzer

class EmotionBasedResponse:
    def __init__(self):
        self.emotion_responses = {
            "긍정": {
                "prefixes": [
                    "좋은 소식이네요! 😊",
                    "정말 기쁘네요! 🎉",
                    "훌륭합니다! 👍"
                ],
                "suffixes": [
                    "더 도움이 필요하시면 언제든 말씀해주세요!",
                    "행복한 하루 되세요! ☀️"
                ]
            },
            "부정": {
                "prefixes": [
                    "아, 그렇다니 안타깝네요 😔",
                    "힘드셨겠어요 💙",
                    "이해합니다. 도움이 필요하시군요"
                ],
                "suffixes": [
                    "더 자세히 도와드릴 수 있도록 상담사 연결을 제안드립니다.",
                    "혹시 상담사와 상담하시겠어요?"
                ]
            },
            "불만": {
                "prefixes": [
                    "불편을 끼쳐 정말 죄송합니다 😔",
                    "고객님의 불만사항을 정확히 파악했습니다",
                    "이런 상황이 발생해서 죄송합니다"
                ],
                "suffixes": [
                    "빠른 해결을 위해 상담사 연결을 권장드립니다.",
                    "상담사가 더 구체적으로 도와드릴 수 있습니다."
                ]
            },
            "분노": {
                "prefixes": [
                    "정말 죄송합니다. 고객님의 마음을 이해합니다 😔",
                    "이런 상황이 발생해서 정말 죄송합니다",
                    "고객님의 분노가 충분히 이해됩니다"
                ],
                "suffixes": [
                    "즉시 상담사 연결을 도와드리겠습니다.",
                    "상담사가 신속하게 해결해드리겠습니다."
                ]
            },
            "불안": {
                "prefixes": [
                    "걱정하지 마세요, 함께 해결해보겠습니다 💙",
                    "안심하세요, 도와드리겠습니다",
                    "걱정이 되시는 부분을 차근차근 해결해보겠습니다"
                ],
                "suffixes": [
                    "더 안심하실 수 있도록 상담사 연결을 제안드립니다.",
                    "상담사가 더 안전하게 안내해드릴 수 있습니다."
                ]
            },
            "중립": {
                "prefixes": [
                    "네, 알겠습니다",
                    "이해했습니다",
                    "확인했습니다"
                ],
                "suffixes": [
                    "더 궁금한 점이 있으시면 언제든 말씀해주세요!",
                    "도움이 필요하시면 언제든 연락주세요."
                ]
            }
        }
    
    def get_emotion_enhanced_response(self, base_response: str, emotion_data: Dict) -> str:
        """감정 상태에 따른 응답 강화"""
        emotion = emotion_data.get('emotion', '중립')
        intensity = emotion_data.get('intensity', 3)
        
        # 감정별 응답 템플릿 가져오기
        emotion_template = self.emotion_responses.get(emotion, self.emotion_responses['중립'])
        
        import random
        
        # 강도에 따른 접두사/접미사 선택
        if intensity >= 4:  # 강한 감정
            prefix = random.choice(emotion_template['prefixes'])
            suffix = random.choice(emotion_template['suffixes'])
        elif intensity >= 2:  # 보통 감정
            prefix = random.choice(emotion_template['prefixes'][:2])  # 첫 2개 중 선택
            suffix = random.choice(emotion_template['suffixes'][:2])
        else:  # 약한 감정
            prefix = ""
            suffix = random.choice(emotion_template['suffixes'][:1])
        
        # 응답 조합
        enhanced_response = base_response
        if prefix:
            enhanced_response = f"{prefix}\n\n{enhanced_response}"
        if suffix:
            enhanced_response = f"{enhanced_response}\n\n{suffix}"
        
        return enhanced_response
    
    def get_escalation_suggestion(self, emotion_data: Dict, trend: Dict) -> str:
        """상담사 연결 제안 메시지"""
        emotion = emotion_data.get('emotion', '중립')
        intensity = emotion_data.get('intensity', 3)
        
        if trend.get('recommendation') == 'immediate_agent':
            return "\n\n🚨 **긴급 상담사 연결이 필요합니다.**\n상담사가 즉시 도와드리겠습니다."
        elif trend.get('recommendation') == 'suggest_agent':
            return "\n\n💬 **상담사 연결을 권장드립니다.**\n더 전문적인 도움을 받으실 수 있습니다."
        elif trend.get('recommendation') == 'empathetic_response':
            return "\n\n💙 **더 자세한 상담이 필요하시면 상담사 연결을 고려해보세요.**"
        
        return ""
    
    def get_emotion_aware_prompt(self, user_message: str, emotion_data: Dict) -> str:
        """감정을 고려한 프롬프트 생성"""
        emotion = emotion_data.get('emotion', '중립')
        intensity = emotion_data.get('intensity', 3)
        
        emotion_context = {
            "긍정": "사용자가 긍정적인 상태이므로 친근하고 격려하는 톤으로 답변해주세요.",
            "부정": "사용자가 부정적인 상태이므로 공감하고 위로하는 톤으로 답변해주세요.",
            "불만": "사용자가 불만을 가지고 있으므로 사과하고 해결책을 제시하는 톤으로 답변해주세요.",
            "분노": "사용자가 분노한 상태이므로 진심 어린 사과와 즉각적인 해결책을 제시해주세요.",
            "불안": "사용자가 불안한 상태이므로 안심시키고 차근차근 설명하는 톤으로 답변해주세요.",
            "중립": "일반적인 정보 제공 톤으로 답변해주세요."
        }
        
        context = emotion_context.get(emotion, emotion_context['중립'])
        
        if intensity >= 4:
            context += " 감정 강도가 높으므로 더 신중하고 배려심 있는 답변을 해주세요."
        
        return f"{context}\n\n사용자 메시지: {user_message}"

# 전역 인스턴스
emotion_response = EmotionBasedResponse() 