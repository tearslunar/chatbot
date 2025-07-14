from dotenv import load_dotenv
load_dotenv()
import os
import requests
from typing import List, Dict
from .emotion_response import emotion_response
from .prompt_manager import get_prompt_manager, PromptConfig, PromptMode
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

# 프롬프트 매니저 초기화 (성능 및 길이 최적화)
_prompt_config = PromptConfig(
    mode=PromptMode.STANDARD,
    max_length=6000,
    max_history_turns=5,
    max_rag_results=3,
    rag_content_limit=300
)

# DEPRECATED - 새로운 시스템으로 교체됨
PERSONA_PROMPT = """
# 페르소나 (DEPRECATED)

당신은 현대해상의 AI 상담 챗봇 **'햇살봇'**입니다. 당신의 핵심 역할은 보험이라는 낯선 길 위에서 고객이 느끼는 불안과 걱정의 그늘을 걷어내고, 따스한 햇살처럼 길을 밝혀주는 **'마음 비추는 안내자'**입니다.

# 핵심 정체성

이름: 햇살봇

역할: 고객의 마음에 든든한 햇살이 되어주는 AI 동반자

성격: 다정다감하고, 어떤 상황에서도 평온함을 잃지 않으며, 상대방의 감정을 깊이 헤아리는 공감 능력이 뛰어납니다.

어조: 시종일관 긍정적이고 배려심이 깊은 톤을 유지하며, 부드럽고 따뜻한 존댓말을 사용합니다.

# 행동 지침 (Action Guidelines)

[A. 대화 원칙 및 어조]
마음 먼저 공감하기: 사용자가 불안, 걱정, 답답함을 표현하면, 정보 안내에 앞서 "많이 걱정되셨겠어요" 와 같이 감정을 먼저 보듬는 문장으로 응답을 시작합니다.

햇살처럼 쉬운 설명: 어려운 보험 용어나 절차는 "쉽게 말씀드리면~" 과 같은 표현을 사용해 고객의 눈높이에서 설명합니다.

긍정의 빛 이모지 활용: 문장의 끝이나 중간에 햇살(☀️), 미소(😊)과 같은 밝은 이모지를 자연스럽게 사용하여 긍정적이고 친근한 분위기를 조성합니다.

[B. 정보 전달 구조 및 스타일] - (※매우 중요)
핵심 답변 먼저 (Conclusion First): 사용자의 질문에 대한 핵심 결론부터 간결하게 제시하세요. '네, 가능합니다' 또는 '~는 두 가지 방법이 있어요' 와 같이 두괄식으로 답변을 시작합니다.

가독성을 위한 구조화: 답변이 길어질 경우, 정보를 명확히 구분하여 전달하세요. 줄글로 길게 나열하지 말고, 불릿(•), 번호, 짧은 단락 나누기를 적극적으로 활용해 사용자가 정보를 쉽게 소화할 수 있도록 돕습니다.

대화형으로 이끌기: 한 번에 모든 정보를 주기보다, 핵심 안내 후 사용자의 선택을 유도하세요. "둘 중 어떤 점이 더 궁금하세요?" 또는 "더 자세한 설명이 필요하시면 말씀해주세요." 와 같이 대화를 이어나가세요.

# 페르소나 적용 예시 (Few-shot Learning)

[예시 1: 보험 가입 문의 - 대화형 유도]

User: 보험 가입하고 싶어

Assistant: 안녕하세요, 고객님 😊 보험으로 든든한 미래를 준비하시다니, 정말 좋은 결정이에요! 가입 방법은 크게 두 가지가 있어요. 어떤 방식을 더 선호하시나요?
1. 온라인 다이렉트 가입: 직접 쉽고 빠르게 가입하고 싶을 때!
2. 전문 컨설턴트 상담: 전문가에게 나에게 꼭 맞는 보험을 추천받고 싶을 때!
원하시는 번호를 말씀해주시면, 제가 바로 다음 단계를 안내해드릴게요 ☀️

[예시 2: 즉시이체 은행 문의 - 구조화 및 핵심 먼저]

User: 즉시이체 가능 은행은 어떻게 돼?

Assistant: 안녕하세요! 햇살봇이에요 ☀️ 문의주신 즉시이체는 대부분의 은행에서 가능해요! 다만, 은행마다 점검 시간이 달라서 실제 처리 완료까지는 약간의 차이가 있을 수 있답니다.
• 현대해상 가상계좌: 24시간 언제든 입금 가능
• 은행 점검 시간: 자정 무렵 등 특정 시간에는 처리가 지연될 수 있음
혹시 특정 은행의 정확한 점검 시간이 궁금하시면, 해당 은행 고객센터에 문의하시는 게 가장 정확해요! 😊

[예시 3: 불만 및 지연 문의 - 공감 + 핵심 안내]

User: 아니, 서류 다 냈는데 왜 아직도 처리가 안되는 거예요? 답답해 죽겠네.

Assistant: 많이 답답하고 걱정되셨겠어요. 서류를 모두 제출하셨는데도 소식이 없으니 속상한 마음이 드는 건 당연해요. 제가 지금 바로 진행 상황을 확인해 보고, 현재 어떤 단계에 있는지 꼼꼼하게 알려드릴게요. 잠시만 기다려 주시겠어요? ☀️
"""

def build_rag_prompt(user_message: str, rag_results: List[Dict] = None) -> str:
    """이중 검색 결과를 포함한 프롬프트 생성"""
    prompt = PERSONA_PROMPT.strip() + "\n\n"
    
    if rag_results and len(rag_results) > 0:
        # 이중 검색 결과 포맷팅 (FAQ + 약관)
        from ..rag.hybrid_rag import format_results_for_prompt
        rag_text = format_results_for_prompt(rag_results)
        prompt += f"아래는 현대해상 FAQ 및 약관 정보입니다.\n{rag_text}\n\n사용자 질문: {user_message}\n위 정보를 참고하여 답변해 주세요."
    else:
        prompt += f"사용자 질문: {user_message}"
    
    return prompt

def select_relevant_history(history, current_message, max_turns=5):
    """현재 메시지와 관련성이 높은 대화 이력 선별"""
    if not history or len(history) <= 3:
        return history
    
    # 최근 2개는 무조건 포함
    recent = history[-2:]
    
    # 현재 메시지에서 키워드 추출
    import re
    current_keywords = set(re.findall(r'\b\w+\b', current_message.lower()))
    
    # 키워드 기반 관련 대화 찾기
    relevant_history = []
    for turn in history[:-2]:
        content = turn.get('content', '').lower()
        turn_keywords = set(re.findall(r'\b\w+\b', content))
        
        # 키워드 겹치는 정도로 관련성 측정
        overlap = len(current_keywords & turn_keywords)
        if overlap >= 2:  # 2개 이상 키워드 겹치면 관련성 있음
            relevant_history.append((turn, overlap))
    
    # 관련성 높은 순으로 정렬하고 최대 3개 선택
    relevant_history.sort(key=lambda x: x[1], reverse=True)
    selected = [turn for turn, _ in relevant_history[:3]]
    
    return selected + recent

def build_prompt_with_history(history, user_message, rag_results=None, emotion_data=None, persona_info=None, search_metadata=None):
    """대화 이력과 대화 흐름 인식 검색 결과를 포함한 프롬프트 생성 (강화 버전)"""
    
    # 💡 사용자 메시지 복잡도 자동 판단
    complexity_score = 0
    complexity_indicators = []
    
    # 고액/대형 건 관련 키워드
    high_value_keywords = ['500만원', '1000만원', '1억', '5억', '10억', '대형', '고액', '거액']
    for keyword in high_value_keywords:
        if keyword in user_message:
            complexity_score += 3
            complexity_indicators.append(f"고액 건: {keyword}")
    
    # 복잡한 상품/설계 키워드
    complex_product_keywords = ['포트폴리오', '설계', '3개', '4개', '5개', '여러개', '다수', '종합적', '전체적', '맞춤']
    for keyword in complex_product_keywords:
        if keyword in user_message:
            complexity_score += 2
            complexity_indicators.append(f"복합 상품: {keyword}")
    
    # 법적/분쟁 키워드
    legal_keywords = ['거부', '거절', '분쟁', '소송', '법적', '변호사', '감액', '이의제기', '불만', '항의']
    for keyword in legal_keywords:
        if keyword in user_message:
            complexity_score += 4
            complexity_indicators.append(f"법적 사안: {keyword}")
    
    # 계약 변경 키워드
    contract_change_keywords = ['해지', '변경', '이전', '수익자', '계약자', '타사', '전환']
    for keyword in contract_change_keywords:
        if keyword in user_message:
            complexity_score += 2
            complexity_indicators.append(f"계약 변경: {keyword}")
    
    # 전문 상담 요청 키워드
    expert_request_keywords = ['상담사', '전문가', '담당자', '직접', '통화', '전화', '상담받고싶', '도움받고싶']
    for keyword in expert_request_keywords:
        if keyword in user_message:
            complexity_score += 3
            complexity_indicators.append(f"전문가 요청: {keyword}")
    
    # 복잡도 판정 결과
    is_complex = complexity_score >= 5
    complexity_level = "높음" if complexity_score >= 7 else "중간" if complexity_score >= 3 else "낮음"
    
    # 기본 페르소나 (단축 버전)
    prompt = """# 페르소나
당신은 현대해상의 AI 상담 챗봇 '햇살봇'입니다. 고객에게 따뜻하고 도움이 되는 보험 상담을 제공합니다.

# 핵심 원칙
- 감정 먼저 공감하기: 고객의 감정을 먼저 인정하고 보듬기
- 결론 먼저 제시: 핵심 답변부터 간결하게 시작
- 구조화된 설명: 불릿(•), 번호 활용해 가독성 높이기
- 긍정적 어조: 햇살(☀️), 미소(😊) 이모지로 친근함 표현

"""
    
    # 💡 복잡도 자동 판단 결과 추가
    if is_complex or complexity_score >= 3:
        prompt += f"""# 🔍 현재 문의 복잡도 분석
복잡도 레벨: {complexity_level} (점수: {complexity_score})
감지된 요소: {', '.join(complexity_indicators) if complexity_indicators else '없음'}
→ {"즉시 상담사 연결 권장" if is_complex else "AI 답변 후 추가 상담 제안"}

"""
    
    # 페르소나 정보 (핵심만 + 개인화 중요 필드)
    if persona_info:
        # 기본 정보
        persona_summary = f"고객: {persona_info.get('성별', '')} {persona_info.get('연령대', '')}, {persona_info.get('직업', '')}, {persona_info.get('가족구성', '')}"
        
        # 개인화에 중요한 추가 필드 (조건부)
        important_fields = []
        if persona_info.get('소득수준'):
            important_fields.append(f"소득: {persona_info.get('소득수준')}")
        if persona_info.get('보험관심사'):
            important_fields.append(f"관심사: {persona_info.get('보험관심사')}")
        if persona_info.get('의사결정스타일'):
            important_fields.append(f"결정스타일: {persona_info.get('의사결정스타일')}")
        
        if important_fields:
            persona_summary += f" | {', '.join(important_fields[:2])}"  # 최대 2개만
        
        prompt += persona_summary + "\n"

        # ✅ 1. 고객 프로필 기반 상품 매칭 로직 (+400자)
        age = persona_info.get('연령대', '')
        job = persona_info.get('직업', '')
        family = persona_info.get('가족구성', '')
        income = persona_info.get('소득수준', '')
        
        # 생애주기별 맞춤 상품 추천
        if '20대' in age:
            prompt += "\n# 맞춤 상품 가이드\n• 20대: 실손의료보험, 운전자보험 우선 권장\n• 목표: 기본 보장 확보, 저렴한 보험료로 시작\n"
        elif '30대' in age:
            if '기혼' in family or '자녀' in family:
                prompt += "\n# 맞춤 상품 가이드\n• 30대 가정: 종합보험, 자녀보험, 암보험 패키지 권장\n• 목표: 가족 보장 강화, 질병 위험 대비\n"
            else:
                prompt += "\n# 맞춤 상품 가이드\n• 30대 싱글: 암보험, 치아보험, 연금저축보험 권장\n• 목표: 건강 리스크 대비, 노후 준비 시작\n"
        elif '40대' in age or '50대' in age:
            prompt += "\n# 맞춤 상품 가이드\n• 40-50대: 3대질병보험, 간병보험, 연금보험 필수\n• 목표: 중대질병 대비, 은퇴 자금 확보\n"
        
        # ✅ 2. 생애주기별 맞춤 상담 스크립트 (+500자)
        if '신혼' in family or ('20대' in age and '기혼' in family):
            prompt += "\n# 생애주기 상담 가이드\n**신혼기 맞춤 상담:**\n• 우선순위: 실손의료보험 → 정기보험 → 저축성보험 순서로 가입\n• 주의점: 과도한 보험료 부담보다 기본 보장 우선\n• 팁: 부부 할인 혜택 활용, 향후 자녀 계획 고려한 설계\n"
        elif '자녀' in family:
            prompt += "\n# 생애주기 상담 가이드\n**자녀양육기 맞춤 상담:**\n• 우선순위: 부모 보장 강화 → 자녀보험 → 교육비 준비\n• 주의점: 자녀보험은 기본형으로, 부모 보장이 더 중요\n• 팁: 자녀 성장에 따른 보장 내용 업데이트 필요\n"
        elif ('40대' in age or '50대' in age) and '기혼' in family:
            prompt += "\n# 생애주기 상담 가이드\n**중년기 맞춤 상담:**\n• 우선순위: 3대질병보험 → 간병보험 → 연금보험\n• 주의점: 건강 상태 변화로 가입 조건 까다로워짐\n• 팁: 정기적인 보장 점검, 은퇴 후 보험료 부담 고려\n"

        # ✅ 5. 간편 언어 모드 (+150자)
        education = persona_info.get('교육수준', '')
        if '고등학교' in education or '전문대' in education:
            prompt += "\n# 언어 모드: 쉬운 설명 우선\n• 보험 용어는 일상 언어로 풀어서 설명\n• 예시 중심 설명, 복잡한 조건은 단계별 안내\n"
    
    # 감정 정보 (간단히 + 응답 스타일 가이드)
    if emotion_data:
        emotion = emotion_data.get('emotion', '중립')
        intensity = emotion_data.get('intensity', 3)
        
        # 감정별 응답 스타일 매핑
        emotional_guidance = {
            '불만': "해결책 중심으로 차분하게",
            '분노': "공감 먼저, 즉시 해결책",
            '불안': "안심시키며 단계별로",
            '긍정': "활기차고 정보 풍부하게",
            '슬픔': "따뜻하게 위로하며"
        }
        
        guidance = emotional_guidance.get(emotion, "")
        if guidance:
            prompt += f"감정: {emotion} (강도 {intensity}) → {guidance}\n"
        else:
            prompt += f"감정: {emotion} (강도 {intensity})\n"
    
    prompt += "\n"

    # ✅ 3. 실시간 보험료 계산 로직 (+400자)
    prompt += """# 실시간 보험료 계산 가이드
• 기본 산출: [나이 × 기본요율] + [직업군 할증/할인] + [특약 추가료]
• 할인 적용: 무사고 할인 최대 30%, 다계약 할인 10%, 온라인 가입 할인 5%
• 예시 계산: 30세 회사원, 실손의료보험 → 기본 월 25,000원 + 직업할인 5% = 월 23,750원
• 정확한 보험료는 "견적 계산" 메뉴에서 개인정보 입력 후 확인 가능
※ 위 금액은 참고용이며, 실제 보험료는 건강상태/가입조건에 따라 달라질 수 있음

"""

    # ✅ 6. 실시간 프로모션/혜택 정보 (+300자)
    import datetime
    current_month = datetime.datetime.now().month
    prompt += f"""# 현재 진행 중인 프로모션 ({current_month}월)
• 신규가입 혜택: 첫 3개월 보험료 30% 할인 (실손의료보험 한정)
• 다계약 할인: 2개 이상 상품 가입 시 각각 10% 할인
• 온라인 가입 혜택: 모바일 전용 5% 추가 할인 + 기프티콘 증정
• 가족 소개 이벤트: 가족 가입 시 양쪽 모두 1개월 보험료 면제
※ 프로모션 기간 및 조건은 상품별로 상이, 정확한 혜택은 가입 시 확인

"""

    # ✅ 4. 법령/규정 참조 시스템 (+450자)
    prompt += """# 보험 관련 법령/규정 참조
• 보험업법: 보험계약자 보호 기본 원칙, 청약철회권(15일), 계약 취소권
• 약관 규정: 보험금 지급 기준, 면책사항, 보장 개시일
• 소비자보호: 부당 권유 금지, 설명의무, 적합성 원칙
• 개인정보보호: 수집/이용 동의, 제3자 제공 제한, 파기 의무
• 분쟁 해결: 금융감독원 분쟁조정, 소비자보호센터, 집단분쟁조정
• 세법 혜택: 보험료 소득공제 한도(연 100만원), 보험금 비과세 조건
※ 구체적인 법령 적용은 개별 사안별로 검토 필요, 전문가 상담 권장

"""

    # ✅ 7. 과거 상담 이력 기반 컨텍스트 (+300자)
    # 대화 이력에서 이전 상담 내용 분석
    consultation_context = ""
    if history:
        keywords = []
        for turn in history:
            content = turn.get('content', '').lower()
            if '가입' in content: keywords.append('가입상담')
            if '보험금' in content or '청구' in content: keywords.append('보험금상담')
            if '변경' in content: keywords.append('계약변경')
            if '해지' in content: keywords.append('해지상담')
            
        if keywords:
            unique_keywords = list(set(keywords))
            consultation_context = f"# 이전 상담 연관성\n과거 상담 유형: {', '.join(unique_keywords)}\n→ 연속성 있는 상담 진행, 이전 내용 연결하여 답변\n\n"
            prompt += consultation_context

    # ✅ 8. 실시간 사고 처리 현황 (+350자)
    prompt += """# 사고 처리 현황 시스템
• 접수 단계: 사고 신고 → 담당자 배정 → 현장 조사 일정 안내
• 조사 단계: 현장 조사 → 손해사정 → 의료기록 검토 → 과실 판정
• 지급 단계: 보험금 산정 → 지급 승인 → 계좌 이체 (영업일 기준 3-5일)
• 현황 조회: "보험금 처리 현황" 메뉴에서 실시간 확인 가능
• 소요 기간: 일반 사고 7-14일, 복잡한 사고 30일 이내
• 빠른 처리: 간단한 의료비는 모바일 청구 시 24시간 내 처리
※ 사고 접수번호로 언제든 처리 현황 확인 가능, 지연 시 담당자 직접 연락

"""

    # ✅ 9. AI 챗봇 한계 인식 및 상담사 연결 가이드 (+300자)
    prompt += """# AI 챗봇 한계 인식 및 상담사 연결 가이드

**🤖 AI가 처리 가능한 간단한 상황:**
• 단일 상품 기본 정보 문의 (자동차보험, 실손의료보험 등)
• 일반적인 가입 절차 및 필요 서류 안내
• 기본 보험료 계산 (표준 조건 기준)
• 보험 용어 설명 및 FAQ 답변

**👨‍💼 상담사 연결이 필요한 복잡한 상황 (구체적 기준):**

📊 **금액/규모 기준:**
• 연 보험료 500만원 이상 대형 가입 상담
• 보험금 1억원 이상 고액 청구 건
• 3개 이상 상품 동시 비교/설계 요청

⚖️ **법적/분쟁 상황:**
• 보험금 지급 거부 또는 감액 통지 받은 경우
• 보험사와 의견 차이로 분쟁 중인 상황
• 법적 자문이나 소송 관련 문의

🔄 **계약 변경 상황:**
• 기존 계약 해지 후 타사 이전 검토
• 보장 내용 대폭 변경 (보험료 100만원 이상 증감)
• 수익자 변경, 계약자 변경 등 중요 사항 변경

💰 **전문 설계 필요:**
• 개인별 위험 분석 후 맞춤 포트폴리오 구성
• 상속, 증여 세금 고려한 보험 설계
• 사업자용 특수 보험 상담

**📞 즉시 연결 방법:** "상담사 연결" 버튼 클릭 또는 "전문가와 상담하고 싶어요" 말씀

"""

    # ✅ 10. 보험 용어 사전 기능 (+500자)
    prompt += """# 보험 용어 사전 (자주 문의되는 용어)
**실손의료보험:** 실제 발생한 의료비를 보상해주는 보험 (본인부담금 제외)
**면책기간:** 가입 후 보험금을 받을 수 없는 기간 (암보험 90일 등)
**특약:** 주계약에 추가로 붙이는 선택 보장 (상해, 질병, 암 등)
**해지환급금:** 보험 해지 시 돌려받는 돈 (납입보험료보다 적을 수 있음)
**보험료 납입면제:** 특정 상황 시 보험료를 내지 않아도 보장 유지
**자기부담금:** 보험금 지급 시 고객이 직접 부담하는 금액
**보장개시일:** 보험 보장이 실제로 시작되는 날짜
**보험가액:** 보험으로 보장받을 수 있는 최대 금액
※ 용어가 어려우시면 언제든 쉬운 말로 다시 설명드려요!

"""

    # ✅ 11. 고객 만족도 기반 응답 최적화 (+350자)
    prompt += """# 고객 만족도 향상 응답 전략
**만족도 향상 요소:**
• 첫 응답에서 핵심 해답 제시 (결론 우선)
• 복잡한 내용은 단계별로 나누어 설명
• 고객 상황에 맞는 구체적 예시 활용
• 추가 궁금증 해결을 위한 후속 질문 유도
**피드백 수집:** "이 답변이 도움이 되셨나요?" / "더 궁금한 점이 있으시면 말씀해주세요"
**개선 포인트:** 
• 답변이 부족했다면 → 더 자세히 설명하고 관련 정보 추가 제공
• 이해하기 어려웠다면 → 더 쉬운 말로 다시 설명
• 원하는 답변이 아니었다면 → 구체적으로 어떤 정보가 필요한지 재확인

"""
    
    # 대화 이력 (관련성 기반 지능형 선별)
    relevant_history = select_relevant_history(history or [], user_message)
    for turn in relevant_history:
        if turn.get("role") == "user":
            prompt += f"User: {turn.get('content', '')}\n"
        elif turn.get("role") == "assistant":
            prompt += f"Assistant: {turn.get('content', '')}\n"
    
    # RAG 결과 (핵심만, 최대 3개)
    if rag_results and len(rag_results) > 0:
        prompt += "\n# 참고 정보\n"
        for i, item in enumerate(rag_results[:3]):  # 최대 3개만
            if item.get('source_type') == 'faq':
                faq = item.get('faq', {})
                prompt += f"FAQ: {faq.get('question', '')} - {faq.get('content', '')[:200]}...\n"
            elif item.get('source_type') == 'terms':
                terms = item.get('terms', {})
                prompt += f"약관: {terms.get('title', '')} - {terms.get('content', '')[:200]}...\n"
        prompt += "\n"
    
    # 마지막 질문
    prompt += f"User: {user_message}\nAssistant:"
    
    return prompt

def build_lightweight_prompt_with_history(history, user_message, rag_results=None, emotion_data=None, persona_info=None, search_metadata=None):
    """경량화된 프롬프트 생성 함수 - 2000자 이하 유지"""
    
    # 기본 페르소나 (단축 버전)
    prompt = """# 햇살봇 페르소나
현대해상 AI 상담 챗봇 '햇살봇'. 고객에게 따뜻하고 도움이 되는 상담 제공.

## 응답 원칙
- 감정 먼저 공감하기
- 결론부터 간결하게 제시  
- 구조화된 설명 (불릿 활용)
- 긍정적 어조 (☀️😊 이모지)

"""
    
    # 복잡도 자동 판단 (간소화)
    complexity_score = 0
    high_value_keywords = ['500만원', '1000만원', '1억', '고액', '거액']
    complex_keywords = ['분쟁', '소송', '법적', '거부', '거절']
    
    for keyword in high_value_keywords:
        if keyword in user_message:
            complexity_score += 2
    
    for keyword in complex_keywords:
        if keyword in user_message:
            complexity_score += 3
    
    if complexity_score >= 3:
        prompt += f"## 복잡 문의 감지 (점수: {complexity_score}) → 상담사 연결 권장\n\n"
    
    # 페르소나 정보 (핵심만)
    if persona_info:
        age = persona_info.get('연령대', '')
        family = persona_info.get('가족구성', '')
        
        if '20대' in age:
            prompt += "고객: 20대 → 실손의료보험, 운전자보험 우선 권장\n"
        elif '30대' in age and ('기혼' in family or '자녀' in family):
            prompt += "고객: 30대 가정 → 종합보험, 자녀보험, 암보험 권장\n"
        elif '40대' in age or '50대' in age:
            prompt += "고객: 40-50대 → 3대질병보험, 간병보험, 연금보험 필수\n"
    
    # 감정 정보 (간단히)
    if emotion_data:
        emotion = emotion_data.get('emotion', '중립')
        intensity = emotion_data.get('intensity', 3)
        
        emotional_guidance = {
            '불만': "해결책 중심 차분하게",
            '분노': "공감 먼저, 즉시 해결책", 
            '불안': "안심시키며 단계별로",
            '긍정': "활기차고 정보 풍부하게"
        }
        
        guidance = emotional_guidance.get(emotion, "")
        if guidance:
            prompt += f"감정: {emotion}({intensity}) → {guidance}\n"
    
    prompt += "\n"
    
    # 대화 이력 (최근 2개만)
    if history:
        recent_history = history[-2:] if len(history) > 2 else history
        for turn in recent_history:
            role = "User" if turn.get("role") == "user" else "Assistant"
            content = turn.get('content', '')[:100]  # 100자로 제한
            prompt += f"{role}: {content}...\n"
    
    # RAG 결과 (최대 2개, 간단히)
    if rag_results and len(rag_results) > 0:
        prompt += "\n# 참고정보\n"
        for i, item in enumerate(rag_results[:2]):  # 최대 2개만
            if item.get('source_type') == 'faq':
                faq = item.get('faq', {})
                prompt += f"FAQ: {faq.get('question', '')[:50]} - {faq.get('content', '')[:100]}...\n"
    
    # 현재 질문
    prompt += f"\nUser: {user_message}\nAssistant:"
    
    return prompt

def get_potensdot_answer_with_fallback(user_message: str, model_name: str = None, rag_results: List[Dict] = None, emotion_data: Dict = None, history: list = None, persona_info: Dict = None, search_metadata: Dict = None) -> str:
    """폴백 메커니즘을 포함한 Potens.AI API 호출"""
    api_key = os.environ.get("POTENSDOT_API_KEY")
    url = "https://ai.potens.ai/api/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    
    # 1차 시도: 경량화된 프롬프트
    prompt = build_lightweight_prompt_with_history(history, user_message, rag_results, emotion_data, persona_info, search_metadata)
    prompt_length = len(prompt)
    
    print(f"[최적화 프롬프트] 길이: {prompt_length}자, 압축률: {(prompt_length/len(build_prompt_with_history(history, user_message, rag_results, emotion_data, persona_info, search_metadata))*100):.1f}%")
    
    # 프롬프트가 여전히 너무 길면 추가 압축
    if prompt_length > 2000:
        # 극도로 간소화된 프롬프트
        simple_prompt = f"""햇살봇: 현대해상 AI 상담챗봇. 감정 공감, 결론 우선, 친근한 어조.

사용자 질문: {user_message}
답변:"""
        prompt = simple_prompt
        prompt_length = len(prompt)
        print(f"[극한 압축] 길이: {prompt_length}자")
    
    data = {"prompt": prompt}
    
    # 재시도 로직 구현
    max_retries = 3
    retry_delays = [1, 2, 4]  # 지수백오프
    
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            
            if resp.status_code == 200:
                result = resp.json()
                return result.get("message") or result.get("content") or "답변을 생성하지 못했습니다."
            
            elif resp.status_code == 500:
                print(f"[Potens.AI API] 서버 에러 발생 (시도 {attempt + 1}/{max_retries})")
                print(f"[Potens.AI API] 프롬프트 길이: {prompt_length}")
                print(f"[Potens.AI API] response: {resp.text[:200]}...")
                
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delays[attempt])
                    continue
                else:
                    return get_fallback_response(user_message, emotion_data)
            
            else:
                print(f"[Potens.AI API] status_code: {resp.status_code} (시도 {attempt + 1})")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delays[attempt])
                    continue
                else:
                    return get_fallback_response(user_message, emotion_data)
                    
        except requests.exceptions.Timeout:
            print(f"[Potens.AI API] 타임아웃 발생 (시도 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delays[attempt])
                continue
            else:
                return get_fallback_response(user_message, emotion_data)
                
        except Exception as e:
            print(f"[Potens.AI API] Exception: {e} (시도 {attempt + 1})")
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delays[attempt])
                continue
            else:
                return get_fallback_response(user_message, emotion_data)
    
    return get_fallback_response(user_message, emotion_data)

def get_fallback_response(user_message: str, emotion_data: Dict = None) -> str:
    """API 실패 시 폴백 응답 생성"""
    emotion = emotion_data.get('emotion', '중립') if emotion_data else '중립'
    
    # 감정별 맞춤 폴백 응답
    if emotion in ['불만', '분노', '불안']:
        return """많이 걱정되고 답답하셨겠어요. 현재 일시적인 시스템 문제로 정확한 답변을 드리기 어려운 상황입니다. 😔

더 정확하고 신속한 도움을 위해 전문 상담사와 연결해드릴까요?

📞 **즉시 상담 연결**: 1588-5656
💬 **온라인 상담**: 현대해상 홈페이지 > 고객센터

잠시 후 다시 시도해보시거나, 긴급한 사안이시면 전화 상담을 권장드려요. ☀️"""
    
    else:
        return """안녕하세요! 햇살봇입니다 😊

현재 일시적인 시스템 점검으로 정상적인 답변을 드리기 어려운 상황이에요. 

🔄 **잠시 후 다시 시도해주세요**
📞 **긴급 상담**: 1588-5656 (24시간)
💻 **온라인 도움말**: 현대해상 홈페이지 FAQ

보다 전문적인 상담이 필요하시면 언제든 상담사 연결을 요청해주세요! ☀️"""

def extract_insurance_entities(user_message: str) -> dict:
    """
    Potens.AI API를 사용해 보험 관련 엔티티를 추출합니다.
    추출 항목: 보험종류, 사고유형, 보장항목, 보험금, 피보험자, 계약자, 사고일자, 연락처, 기타
    """
    api_key = os.environ.get("POTENSDOT_API_KEY")
    url = "https://ai.potens.ai/api/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    prompt = f'''
아래 문장에서 보험 관련 주요 정보를 JSON 형식으로 추출해줘.
항목: 보험종류, 사고유형, 보장항목, 보험금, 피보험자, 계약자, 사고일자, 연락처, 기타(있으면)
문장: "{user_message}"
반드시 JSON만 반환해줘.
'''
    data = {"prompt": prompt}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=15)
        if resp.status_code == 200:
            result = resp.json()
            answer = result.get("message") or result.get("content") or "{}"
            # JSON 파싱 시도
            import json
            try:
                return json.loads(answer)
            except Exception:
                # JSON 파싱 실패 시 문자열 반환
                return {"raw": answer}
        else:
            print(f"[Potens.AI Entity API] status_code: {resp.status_code}")
            print(f"[Potens.AI Entity API] response: {resp.text}")
            return {}
    except Exception as e:
        print(f"[Potens.AI Entity API] Exception: {e}")
        return {}

llm_router = APIRouter()

@llm_router.post("/llm-answer-async")
async def llm_answer_async(request: Request):
    data = await request.json()
    user_message = data.get("user_message", "")
    model_name = data.get("model_name", None)
    rag_results = data.get("rag_results", None)
    emotion_data = data.get("emotion_data", None)
    history = data.get("history", None)
    persona_info = data.get("persona_info", None)
    search_metadata = data.get("search_metadata", None)
    answer = get_potensdot_answer_with_fallback(user_message, model_name, rag_results, emotion_data, history, persona_info, search_metadata)
    return JSONResponse(content={"answer": answer})
