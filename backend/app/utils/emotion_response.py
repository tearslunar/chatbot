from typing import Dict, List
from ..sentiment.advanced import emotion_analyzer
from .prompt_manager import get_prompt_manager, PromptConfig, PromptMode

class EmotionBasedResponse:
    """감정 기반 응답 처리 클래스 - 새로운 프롬프트 매니저 통합"""
    
    def __init__(self):
        # 새로운 프롬프트 매니저 사용
        self.prompt_config = PromptConfig(
            mode=PromptMode.STANDARD,
            max_length=6000,
            max_history_turns=5,
            max_rag_results=3,
            rag_content_limit=300
        )

    def get_emotion_enhanced_response(self, base_response: str, emotion_data: Dict) -> str:
        """감정 기반 응답 향상 (기존 기능 유지)"""
        return base_response

    def get_escalation_suggestion(self, emotion_data: Dict, trend: Dict) -> str:
        """상담사 연결 제안 (기존 기능 유지)"""
        emotion = emotion_data.get('emotion', '중립')
        intensity = emotion_data.get('intensity', 3)
        
        if trend.get('recommendation') == 'immediate_agent':
            return "\n\n🚨 **긴급 상담사 연결이 필요합니다.**\n상담사가 즉시 도와드리겠습니다."
        elif trend.get('recommendation') == 'suggest_agent':
            return "\n\n💬 **상담사 연결을 권장드립니다.**\n더 전문적인 도움을 받으실 수 있습니다."
        elif trend.get('recommendation') == 'empathetic_response':
            return "\n\n💙 **더 자세한 상담이 필요하시면 상담사 연결을 고려해보세요.**"
        return ""

    def get_emotion_aware_prompt(self, user_message: str, emotion_data: Dict, rag_faqs: List[Dict] = None) -> str:
        """감정 인식 프롬프트 생성 - 새로운 프롬프트 매니저 사용"""
        print("[DEPRECATED] get_emotion_aware_prompt는 새로운 build_optimized_prompt를 사용하세요.")
        
        # 새로운 프롬프트 매니저 사용
        prompt_manager = get_prompt_manager(self.prompt_config)
        
        # RAG FAQ를 새로운 형식으로 변환
        rag_results = []
        if rag_faqs:
            for item in rag_faqs:
                rag_results.append({
                    'source_type': 'faq',
                    'faq': item.get('faq', {})
                })
        
        optimized_prompt = prompt_manager.build_optimized_prompt(
            user_message=user_message,
            emotion_data=emotion_data,
            rag_results=rag_results
        )
        
        return optimized_prompt

# 싱글톤 인스턴스
emotion_response = EmotionBasedResponse() 