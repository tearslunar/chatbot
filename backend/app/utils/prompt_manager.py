from typing import List, Dict, Optional, Tuple
import re
from dataclasses import dataclass
from enum import Enum

class PromptMode(Enum):
    """프롬프트 모드 정의"""
    COMPACT = "compact"      # 압축 모드 (4000자 이하)
    STANDARD = "standard"    # 표준 모드 (6000자 이하)
    COMPREHENSIVE = "comprehensive"  # 포괄 모드 (8000자 이하)

@dataclass
class PromptConfig:
    """프롬프트 설정"""
    mode: PromptMode = PromptMode.STANDARD
    max_length: int = 6000
    max_history_turns: int = 5
    max_rag_results: int = 3
    rag_content_limit: int = 300
    persona_detail_level: str = "standard"  # minimal, standard, detailed

class SmartPromptManager:
    """통합 프롬프트 관리자 - 중복 제거, 동적 압축, 스마트 최적화"""
    
    def __init__(self, config: PromptConfig = None):
        self.config = config or PromptConfig()
        
        # 핵심 페르소나 (모든 모드 공통)
        self.core_persona = {
            "identity": "현대해상 AI 상담 챗봇 '햇살봇'",
            "role": "고객의 마음을 비추는 따뜻한 보험 안내자",
            "tone": "공감적, 긍정적, 전문적",
            "style": "결론 우선, 구조화된 설명, 대화형 유도"
        }
        
        # 감정별 세밀한 응답 가이드
        self.emotion_guides = {
            "불만": {"approach": "해결책 우선", "tone": "차분하고 사과적", "action": "즉시 대안 제시"},
            "분노": {"approach": "즉시 공감", "tone": "진정성 있게", "action": "빠른 해결 방안"},
            "불안": {"approach": "안심 우선", "tone": "따뜻하고 확신", "action": "단계별 상세 설명"},
            "긍정": {"approach": "활기찬 대응", "tone": "밝고 적극적", "action": "더 많은 정보 제공"},
            "슬픔": {"approach": "위로 우선", "tone": "부드럽고 공감적", "action": "따뜻한 격려"},
            "중립": {"approach": "균형 있는", "tone": "친근하고 전문적", "action": "명확한 정보 전달"},
            "기쁨": {"approach": "함께 기뻐", "tone": "활기차고 긍정적", "action": "추가 혜택 안내"},
            "놀람": {"approach": "차분한 설명", "tone": "이해하기 쉽게", "action": "명확한 정보 정리"},
            "실망": {"approach": "공감과 대안", "tone": "이해하고 지지", "action": "개선된 옵션 제시"}
        }
        
        # 동적 Few-shot 예시 풀
        self.example_pool = {
            "가입문의": {
                "user": "보험 가입하고 싶어",
                "assistant": "보험으로 든든한 미래를 준비하시는군요! 😊 가입 방법은 두 가지가 있어요:\n1. 온라인 다이렉트 가입\n2. 전문 컨설턴트 상담\n어떤 방식을 선호하시나요?"
            },
            "보상문의": {
                "user": "보험금은 언제 받을 수 있나요?",
                "assistant": "보험금 지급은 보통 7-14일 소요됩니다. ☀️ 현재 진행 상황을 확인해드릴까요?\n• 서류 심사: 3-5일\n• 최종 승인: 2-3일\n더 궁금한 점이 있으시면 말씀해주세요!"
            },
            "불만대응": {
                "user": "처리가 너무 늦어요. 답답해 죽겠네",
                "assistant": "많이 답답하셨겠어요. 😔 처리 지연으로 불편을 드려 정말 죄송합니다. 지금 즉시 담당자에게 확인해서 빠른 처리가 가능하도록 도와드릴게요. 조금만 기다려주시겠어요?"
            }
        }

    def build_optimized_prompt(
        self, 
        user_message: str,
        history: List[Dict] = None,
        rag_results: List[Dict] = None,
        emotion_data: Dict = None,
        persona_info: Dict = None,
        search_metadata: Dict = None
    ) -> str:
        """최적화된 통합 프롬프트 생성"""
        
        # 1단계: 기본 페르소나 구성
        prompt_parts = [self._build_core_persona()]
        
        # 2단계: 고객 페르소나 정보 (간결하게)
        if persona_info:
            prompt_parts.append(self._build_persona_context(persona_info))
        
        # 3단계: 감정 기반 응답 가이드
        if emotion_data:
            prompt_parts.append(self._build_emotion_guide(emotion_data))
        
        # 4단계: 스마트 대화 이력 선별
        if history:
            prompt_parts.append(self._build_smart_history(history, user_message))
        
        # 5단계: 최적화된 RAG 정보
        if rag_results:
            prompt_parts.append(self._build_optimized_rag(rag_results))
        
        # 6단계: 동적 Few-shot 예시 선택
        prompt_parts.append(self._select_relevant_examples(user_message, emotion_data))
        
        # 7단계: 현재 질문
        prompt_parts.append(f"\nUser: {user_message}\nAssistant:")
        
        # 8단계: 길이 조절 및 최적화
        final_prompt = "\n".join(prompt_parts)
        return self._optimize_prompt_length(final_prompt)

    def _build_core_persona(self) -> str:
        """핵심 페르소나 구성 (모드별 최적화)"""
        if self.config.mode == PromptMode.COMPACT:
            return f"""# 햇살봇 (현대해상 AI)
역할: {self.core_persona['role']}
원칙: {self.core_persona['style']}"""
        
        elif self.config.mode == PromptMode.STANDARD:
            return f"""# 페르소나
당신은 {self.core_persona['identity']}입니다.

## 핵심 원칙
- 감정 우선 공감: 고객 감정을 먼저 인정하고 보듬기
- 결론 우선 제시: 핵심 답변부터 간결하게 시작  
- 구조화된 설명: 불릿(•), 번호로 가독성 높이기
- 긍정적 어조: 햇살(☀️), 미소(😊) 이모지로 친근함 표현"""
        
        else:  # COMPREHENSIVE
            return f"""# 페르소나
당신은 {self.core_persona['identity']}입니다. 
{self.core_persona['role']}로서 보험이라는 복잡한 길에서 고객의 불안을 걷어내고 따뜻한 햇살로 길을 밝혀주세요.

## 핵심 정체성
- 성격: 다정다감하고 평온함을 잃지 않는 공감 능력
- 어조: {self.core_persona['tone']}하게 부드러운 존댓말 사용

## 행동 지침
- 감정 우선 공감: "많이 걱정되셨겠어요" 같은 감정 보듬기
- 햇살처럼 쉬운 설명: "쉽게 말씀드리면~"으로 고객 눈높이 설명
- {self.core_persona['style']}"""

    def _build_persona_context(self, persona_info: Dict) -> str:
        """고객 페르소나 컨텍스트 구성"""
        essential_fields = ['성별', '연령대', '직업', '가족구성']
        important_fields = ['소득수준', '보험관심사', '의사결정스타일']
        
        # 필수 정보
        context = "고객: " + ", ".join([
            persona_info.get(field, '') for field in essential_fields 
            if persona_info.get(field)
        ])
        
        # 중요 정보 (조건부 추가)
        extras = [
            f"{field}: {persona_info.get(field)}" 
            for field in important_fields 
            if persona_info.get(field)
        ]
        
        if extras:
            context += " | " + ", ".join(extras[:2])  # 최대 2개
        
        return context

    def _build_emotion_guide(self, emotion_data: Dict) -> str:
        """감정별 응답 가이드 구성"""
        emotion = emotion_data.get('emotion', '중립')
        intensity = emotion_data.get('intensity', 3)
        
        guide = self.emotion_guides.get(emotion, self.emotion_guides['중립'])
        
        return f"감정 상태: {emotion}(강도 {intensity}) → {guide['approach']}, {guide['tone']}, {guide['action']}"

    def _build_smart_history(self, history: List[Dict], current_message: str) -> str:
        """관련성 기반 스마트 대화 이력 구성"""
        if not history:
            return ""
        
        # 최근 대화 + 관련성 높은 과거 대화 선별
        relevant_history = self._select_relevant_history(history, current_message)
        
        if not relevant_history:
            return ""
        
        history_text = "\n# 대화 맥락"
        for turn in relevant_history[-self.config.max_history_turns:]:
            role = turn.get('role', '')
            content = turn.get('content', '')[:200]  # 대화 이력은 200자 제한
            if role and content:
                history_text += f"\n{role.capitalize()}: {content}"
        
        return history_text

    def _build_optimized_rag(self, rag_results: List[Dict]) -> str:
        """최적화된 RAG 정보 구성"""
        if not rag_results:
            return ""
        
        rag_text = "\n# 참고 정보"
        for i, item in enumerate(rag_results[:self.config.max_rag_results]):
            if item.get('source_type') == 'faq':
                faq = item.get('faq', {})
                question = faq.get('question', '')[:100]
                content = faq.get('content', '')[:self.config.rag_content_limit]
                rag_text += f"\nFAQ: {question} - {content}"
            elif item.get('source_type') == 'terms':
                terms = item.get('terms', {})
                title = terms.get('title', '')[:100]
                content = terms.get('content', '')[:self.config.rag_content_limit]
                rag_text += f"\n약관: {title} - {content}"
        
        return rag_text

    def _select_relevant_examples(self, user_message: str, emotion_data: Dict = None) -> str:
        """동적 Few-shot 예시 선택"""
        if self.config.mode == PromptMode.COMPACT:
            return ""  # 압축 모드에서는 예시 생략
        
        # 감정과 의도 기반 예시 선택
        examples = []
        
        # 감정 기반 예시 선택
        if emotion_data and emotion_data.get('emotion') in ['불만', '분노', '실망']:
            examples.append(self.example_pool['불만대응'])
        
        # 키워드 기반 예시 선택
        if any(keyword in user_message for keyword in ['가입', '신청', '계약']):
            examples.append(self.example_pool['가입문의'])
        elif any(keyword in user_message for keyword in ['보험금', '보상', '청구']):
            examples.append(self.example_pool['보상문의'])
        
        if not examples:
            return ""
        
        example_text = "\n# 응답 예시"
        for example in examples[:2]:  # 최대 2개
            example_text += f"\nUser: {example['user']}\nAssistant: {example['assistant']}\n"
        
        return example_text

    def _select_relevant_history(self, history: List[Dict], current_message: str) -> List[Dict]:
        """현재 메시지와 관련성 높은 대화 이력 선별"""
        if not history or len(history) <= 3:
            return history
        
        # 최근 2개는 무조건 포함
        recent = history[-2:]
        
        # 현재 메시지 키워드 추출
        current_keywords = set(re.findall(r'\b\w+\b', current_message.lower()))
        
        # 관련성 점수 계산
        relevant_history = []
        for turn in history[:-2]:
            content = turn.get('content', '').lower()
            turn_keywords = set(re.findall(r'\b\w+\b', content))
            
            # 키워드 겹침 + 길이 고려 점수
            overlap = len(current_keywords & turn_keywords)
            length_factor = min(len(content) / 100, 1.0)  # 적당한 길이 선호
            score = overlap * length_factor
            
            if score >= 1.5:  # 임계값 조정
                relevant_history.append((turn, score))
        
        # 점수 순 정렬 후 상위 3개 선택
        relevant_history.sort(key=lambda x: x[1], reverse=True)
        selected = [turn for turn, _ in relevant_history[:3]]
        
        return selected + recent

    def _optimize_prompt_length(self, prompt: str) -> str:
        """프롬프트 길이 최적화"""
        current_length = len(prompt)
        
        if current_length <= self.config.max_length:
            return prompt
        
        # 길이 초과 시 단계적 압축
        print(f"[프롬프트 최적화] 길이 초과: {current_length} > {self.config.max_length}")
        
        # 1단계: 불필요한 공백, 줄바꿈 정리
        compressed = re.sub(r'\n\s*\n', '\n', prompt)
        compressed = re.sub(r' +', ' ', compressed)
        
        if len(compressed) <= self.config.max_length:
            print(f"[프롬프트 최적화] 공백 정리로 압축 완료: {len(compressed)}자")
            return compressed
        
        # 2단계: 예시 제거
        compressed = re.sub(r'\n# 응답 예시.*?(?=\n#|\nUser:|$)', '', compressed, flags=re.DOTALL)
        
        if len(compressed) <= self.config.max_length:
            print(f"[프롬프트 최적화] 예시 제거로 압축 완료: {len(compressed)}자")
            return compressed
        
        # 3단계: 대화 이력 축소
        lines = compressed.split('\n')
        history_start = -1
        for i, line in enumerate(lines):
            if line.startswith('# 대화 맥락'):
                history_start = i
                break
        
        if history_start > -1:
            # 대화 이력을 최근 2개만 유지
            history_lines = []
            turn_count = 0
            for line in lines[history_start+1:]:
                if line.startswith(('User:', 'Assistant:')):
                    turn_count += 1
                    if turn_count > 4:  # User + Assistant = 2턴
                        break
                history_lines.append(line)
            
            compressed = '\n'.join(lines[:history_start+1] + history_lines + lines[len(lines):])
        
        final_length = len(compressed)
        print(f"[프롬프트 최적화] 최종 압축 완료: {final_length}자")
        
        return compressed

    def get_prompt_stats(self, prompt: str) -> Dict:
        """프롬프트 통계 정보"""
        lines = prompt.split('\n')
        sections = {}
        current_section = "기본"
        
        for line in lines:
            if line.startswith('#'):
                current_section = line.strip('# ')
                sections[current_section] = 0
            else:
                sections[current_section] = sections.get(current_section, 0) + len(line)
        
        return {
            "total_length": len(prompt),
            "total_lines": len(lines),
            "sections": sections,
            "compression_ratio": round((len(prompt) / 8000) * 100, 1)
        }

# 싱글톤 인스턴스
_prompt_manager = None

def get_prompt_manager(config: PromptConfig = None) -> SmartPromptManager:
    """프롬프트 매니저 싱글톤 인스턴스 반환"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = SmartPromptManager(config)
    return _prompt_manager 