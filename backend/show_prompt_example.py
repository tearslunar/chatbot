#!/usr/bin/env python3
"""
새로운 프롬프트 시스템 생성 예시 확인
실제 최적화된 프롬프트 구조와 내용 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.chat import build_optimized_prompt

def show_prompt_examples():
    """다양한 시나리오의 프롬프트 예시 출력"""
    
    scenarios = [
        {
            "name": "🚗 자동차보험 가입 상담 (긍정적 고객)",
            "user_message": "자동차보험 처음 가입해보려고 해요. 어떤 보장이 필요한지 알려주세요.",
            "emotion_data": {"emotion": "긍정", "intensity": 4},
            "persona_info": {
                "성별": "남성",
                "연령대": "20대",
                "직업": "대학생",
                "운전경력": "초보"
            },
            "rag_results": [
                {
                    "source_type": "faq",
                    "faq": {
                        "question": "자동차보험 필수 보장은?",
                        "content": "대인배상, 대물배상, 자기신체사고, 자기차량손해가 기본 4대 보장입니다."
                    }
                }
            ]
        },
        {
            "name": "😤 보험금 처리 지연 불만 (복잡한 대화 이력)",
            "user_message": "한 달째 기다리고 있는데 언제 처리해주시나요?",
            "emotion_data": {"emotion": "불만", "intensity": 7},
            "persona_info": {
                "성별": "여성",
                "연령대": "40대",
                "직업": "회사원"
            },
            "history": [
                {"role": "user", "content": "교통사고 보험금 신청했어요"},
                {"role": "assistant", "content": "접수번호 A123456으로 신청이 완료되었습니다. 7-14일 내 처리 예정입니다."},
                {"role": "user", "content": "2주가 지났는데 연락이 없네요"},
                {"role": "assistant", "content": "확인 결과 추가 서류가 필요해서 지연되고 있습니다. 곧 연락드리겠습니다."},
                {"role": "user", "content": "서류는 벌써 제출했는데요?"},
                {"role": "assistant", "content": "서류 확인했습니다. 현재 사고 조사 중이며 일주일 내 완료 예정입니다."}
            ],
            "rag_results": [
                {
                    "source_type": "faq",
                    "faq": {
                        "question": "보험금 지급이 지연되는 이유는?",
                        "content": "사고 조사, 의료기록 확인, 과실 비율 산정 등으로 지연될 수 있으며, 복잡한 경우 최대 30일 소요됩니다."
                    }
                }
            ]
        }
    ]
    
    print("🔍 새로운 프롬프트 최적화 시스템 생성 예시")
    print("=" * 80)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 예시 {i}: {scenario['name']}")
        print(f"💬 사용자 메시지: {scenario['user_message']}")
        print("=" * 60)
        
        # 프롬프트 생성 (name 제외)
        prompt_args = {k: v for k, v in scenario.items() if k != 'name'}
        prompt = build_optimized_prompt(**prompt_args)
        
        print("📄 **생성된 프롬프트:**")
        print("```")
        print(prompt)
        print("```")
        
        # 통계 정보
        lines = prompt.split('\n')
        sections = [line for line in lines if line.startswith('#')]
        
        print(f"\n📊 **프롬프트 분석:**")
        print(f"  📏 총 길이: {len(prompt)}자")
        print(f"  📄 총 줄 수: {len(lines)}줄")
        print(f"  🧩 섹션 수: {len(sections)}개")
        print(f"  📋 섹션 목록: {', '.join(section.replace('#', '').strip() for section in sections)}")
        
        if i < len(scenarios):
            print("\n" + "=" * 80)

def main():
    show_prompt_examples()

if __name__ == "__main__":
    main() 