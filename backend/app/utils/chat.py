from dotenv import load_dotenv
load_dotenv()
import os
import requests
from typing import List, Dict
from backend.app.utils.emotion_response import emotion_response
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

PERSONA_PROMPT = """
# 페르소나

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
        from backend.app.rag.hybrid_rag import format_results_for_prompt
        rag_text = format_results_for_prompt(rag_results)
        prompt += f"아래는 현대해상 FAQ 및 약관 정보입니다.\n{rag_text}\n\n사용자 질문: {user_message}\n위 정보를 참고하여 답변해 주세요."
    else:
        prompt += f"사용자 질문: {user_message}"
    
    return prompt

def build_prompt_with_history(history, user_message, rag_results=None, emotion_data=None, persona_info=None):
    """대화 이력과 이중 검색 결과를 포함한 프롬프트 생성"""
    prompt = PERSONA_PROMPT.strip() + "\n\n"
    
    # 페르소나 정보 추가
    if persona_info:
        persona_context = f"""
# 고객 페르소나 정보

고객 프로필: {persona_info.get('성별', '')} {persona_info.get('연령대', '')}
가족 구성: {persona_info.get('가족구성', '')}
직업: {persona_info.get('직업', '')}
소득 수준: {persona_info.get('소득수준', '')}
거주 지역: {persona_info.get('거주지역', '')}
생활 패턴: {persona_info.get('생활패턴', '')}
가치관: {persona_info.get('가치관', '')}
보험 관심사: {persona_info.get('보험관심사', '')}
위험 인식도: {persona_info.get('위험인식도', '')}
디지털 친숙도: {persona_info.get('디지털친숙도', '')}
의사결정 스타일: {persona_info.get('의사결정스타일', '')}
커뮤니케이션 선호: {persona_info.get('커뮤니케이션선호', '')}

위 고객 정보를 바탕으로 고객의 상황과 특성에 맞는 맞춤형 상담을 제공해 주세요.
"""
        prompt += persona_context + "\n"
    
    if emotion_data:
        prompt += f"현재 사용자의 감정은 '{emotion_data.get('emotion', '중립')}'(강도 {emotion_data.get('intensity', 3)})입니다. 이 감정에 공감하며 안내해 주세요.\n\n"
    
    # 대화 이력 추가
    for turn in (history or []):
        if turn.get("role") == "user":
            prompt += f"User: {turn.get('content', '')}\n"
        elif turn.get("role") == "assistant":
            prompt += f"Assistant: {turn.get('content', '')}\n"
    
    # 이중 검색 결과 추가 (FAQ + 약관)
    if rag_results and len(rag_results) > 0:
        from backend.app.rag.hybrid_rag import format_results_for_prompt
        rag_text = format_results_for_prompt(rag_results)
        prompt += f"아래는 현대해상 FAQ 및 약관 정보입니다.\n{rag_text}\n"
    
    # 마지막 질문 추가
    prompt += f"User: {user_message}\nAssistant:"
    return prompt

def get_potensdot_answer(user_message: str, model_name: str = None, rag_results: List[Dict] = None, emotion_data: Dict = None, history: list = None, persona_info: Dict = None) -> str:
    api_key = os.environ.get("POTENSDOT_API_KEY")
    url = "https://ai.potens.ai/api/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    prompt = build_prompt_with_history(history, user_message, rag_results, emotion_data, persona_info)
    data = {"prompt": prompt}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=15)
        if resp.status_code == 200:
            result = resp.json()
            return result.get("message") or result.get("content") or "답변을 생성하지 못했습니다."
        else:
            print(f"[Potens.AI API] status_code: {resp.status_code}")
            print(f"[Potens.AI API] response: {resp.text}")
            return f"챗봇 응답에 문제가 발생했습니다. (상태코드: {resp.status_code}) 관리자에게 문의해 주세요."
    except Exception as e:
        print(f"[Potens.AI API] Exception: {e}")
        return f"챗봇 응답에 일시적 문제가 발생했습니다. (에러: {e}) 관리자에게 문의해 주세요."

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
    answer = get_potensdot_answer(user_message, model_name, rag_results, emotion_data, history, persona_info)
    return JSONResponse(content={"answer": answer}) 