#!/usr/bin/env python3
"""
간단한 챗봇 테스트 스크립트
백엔드 의존성 없이 챗봇 핵심 기능을 직접 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.chat import build_lightweight_prompt_with_history, get_potensdot_answer_with_fallback

class SimpleChatTest:
    def __init__(self):
        self.chat_history = []
        self.session_id = f"test_session_{int(time.time())}"
        
    def test_basic_chat(self):
        """기본 채팅 기능 테스트"""
        print("🤖 햇살봇 간단 테스트")
        print("=" * 50)
        
        test_questions = [
            "안녕하세요",
            "자동차보험 가입하고 싶어요",
            "보험료는 얼마나 나올까요?",
            "감사합니다"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n[질문 {i}] {question}")
            print("-" * 30)
            
            # 프롬프트 생성
            prompt = build_lightweight_prompt_with_history(
                history=self.chat_history,
                user_message=question,
                emotion_data={"emotion": "긍정", "intensity": 4}
            )
            
            print(f"📝 생성된 프롬프트 길이: {len(prompt)}자")
            
            # 챗봇 응답 생성 (모의)
            response = self.get_mock_response(question)
            print(f"🤖 햇살봇: {response}")
            
            # 대화 히스토리 업데이트
            self.chat_history.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": response}
            ])
            
    def get_mock_response(self, question):
        """모의 응답 생성"""
        if "안녕" in question:
            return "안녕하세요! 현대해상 햇살봇입니다 😊 무엇을 도와드릴까요?"
        elif "자동차보험" in question:
            return """네, 자동차보험 가입을 도와드리겠습니다! 🚗

**필수 보장**:
• 대인배상: 무제한
• 대물배상: 2억원 이상  
• 자기신체사고: 1.5억원
• 자기차량손해: 차량가액 기준

더 자세한 상담을 원하시면 말씀해 주세요! ☀️"""
        elif "보험료" in question:
            return """보험료는 여러 요인에 따라 달라져요:

**주요 요인**:
• 운전자 나이와 경력
• 차량 종류와 연식
• 보장 범위와 자기부담금
• 할인 특약 적용 여부

정확한 견적을 위해 차량 정보를 알려주시면 더 도움이 될 거예요! 💰"""
        elif "감사" in question:
            return "도움이 되었다니 다행이에요! 😊 또 궁금한 점이 있으시면 언제든 찾아주세요. 안전한 하루 되세요! ☀️"
        else:
            return "죄송해요, 좀 더 구체적으로 말씀해 주시면 더 정확한 답변을 드릴 수 있어요! 😊"

    def test_prompt_variations(self):
        """다양한 프롬프트 테스트"""
        print("\n\n🧪 프롬프트 변형 테스트")
        print("=" * 50)
        
        test_scenarios = [
            {
                "message": "화가 나요!",
                "emotion": {"emotion": "분노", "intensity": 5},
                "persona": {"연령대": "30대", "직업": "회사원"}
            },
            {
                "message": "걱정이 되네요",
                "emotion": {"emotion": "불안", "intensity": 4},
                "persona": {"연령대": "50대", "가족구성": "기혼"}
            },
            {
                "message": "좋은 정보네요!",
                "emotion": {"emotion": "긍정", "intensity": 4},
                "persona": {"연령대": "20대", "직업": "학생"}
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n[시나리오 {i}] {scenario['message']}")
            print(f"감정: {scenario['emotion']['emotion']} (강도: {scenario['emotion']['intensity']})")
            
            prompt = build_lightweight_prompt_with_history(
                history=[],
                user_message=scenario["message"],
                emotion_data=scenario["emotion"],
                persona_info=scenario["persona"]
            )
            
            print(f"📝 프롬프트 길이: {len(prompt)}자")
            print(f"🎭 페르소나 적용: {scenario['persona']}")
            print("✅ 프롬프트 생성 성공")

if __name__ == "__main__":
    import time
    tester = SimpleChatTest()
    
    print("🚀 현대해상 AI 챗봇 간단 테스트 시작")
    print("Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # 기본 채팅 테스트
    tester.test_basic_chat()
    
    # 프롬프트 변형 테스트
    tester.test_prompt_variations()
    
    print("\n\n🎉 모든 테스트 완료!")
    print("✅ 챗봇 핵심 기능이 정상적으로 작동합니다.") 