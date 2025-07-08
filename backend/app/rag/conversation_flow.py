from typing import List, Dict, Tuple, Optional
import re
from datetime import datetime

class ConversationFlowAnalyzer:
    """대화 흐름 분석기 - 이전 대화 맥락을 분석하여 검색 쿼리를 개선합니다."""
    
    def __init__(self):
        # 보험 관련 주요 키워드 카테고리
        self.insurance_categories = {
            "자동차보험": ["자동차", "차량", "운전", "사고", "충돌", "접촉", "주행", "운전자"],
            "건강보험": ["건강", "질병", "상해", "치료", "입원", "수술", "의료비", "병원"],
            "화재보험": ["화재", "재물", "건물", "주택", "화재사고", "불", "연기"],
            "여행보험": ["여행", "해외", "국내여행", "휴대품", "도난", "분실"],
            "생명보험": ["생명", "사망", "암", "중대질병", "진단", "수술"],
            "배상책임": ["배상", "책임", "손해", "피해", "법률", "소송"]
        }
        
        # 대화 의도 패턴
        self.intent_patterns = {
            "가입문의": ["가입", "신청", "계약", "등록", "시작"],
            "보상문의": ["보상", "보험금", "청구", "지급", "받을", "처리"],
            "변경문의": ["변경", "수정", "갱신", "연장", "취소", "해지"],
            "조회문의": ["조회", "확인", "상태", "내역", "정보", "현황"],
            "문제해결": ["문제", "오류", "안됨", "안되", "실패", "에러"]
        }
        
        # 감정 키워드
        self.emotion_keywords = {
            "긴급": ["긴급", "급함", "빨리", "즉시", "당장", "응급"],
            "불만": ["불만", "화남", "짜증", "답답", "실망", "최악"],
            "불안": ["불안", "걱정", "두려움", "염려", "근심", "우려"],
            "만족": ["만족", "좋음", "감사", "고마움", "훌륭", "완벽"]
        }

    def analyze_conversation_flow(self, history: List[Dict], current_message: str) -> Dict:
        """대화 흐름 분석"""
        # 현재 메시지 분석
        current_analysis = self._analyze_single_message(current_message)
        
        if not history:
            return {
                "context": {},
                "current": current_analysis,
                "flow_pattern": "initial_inquiry",
                "continuation_topics": [],
                "unresolved_issues": [],
                "conversation_stage": "greeting"
            }
        
        # 대화 맥락 분석
        context = self._extract_conversation_context(history)
        
        # 대화 흐름 패턴 분석
        flow_pattern = self._identify_flow_pattern(history, current_message)
        
        return {
            "context": context,
            "current": current_analysis,
            "flow_pattern": flow_pattern,
            "continuation_topics": self._find_continuation_topics(history, current_message),
            "unresolved_issues": self._find_unresolved_issues(history),
            "conversation_stage": self._determine_conversation_stage(history, current_message)
        }

    def _analyze_single_message(self, message: str) -> Dict:
        """단일 메시지 분석"""
        return {
            "categories": self._extract_categories(message),
            "intents": self._extract_intents(message),
            "emotions": self._extract_emotions(message),
            "entities": self._extract_entities(message),
            "keywords": self._extract_keywords(message)
        }

    def _extract_conversation_context(self, history: List[Dict]) -> Dict:
        """대화 전체 맥락 추출"""
        all_messages = []
        user_messages = []
        assistant_messages = []
        
        for turn in history:
            content = turn.get('content', '')
            if turn.get('role') == 'user':
                user_messages.append(content)
            elif turn.get('role') == 'assistant':
                assistant_messages.append(content)
            all_messages.append(content)
        
        combined_text = ' '.join(all_messages)
        
        return {
            "dominant_categories": self._get_dominant_categories(combined_text),
            "recurring_intents": self._get_recurring_intents(user_messages),
            "conversation_topics": self._extract_conversation_topics(all_messages),
            "mentioned_entities": self._extract_entities(combined_text),
            "emotional_progression": self._analyze_emotional_progression(user_messages)
        }

    def _identify_flow_pattern(self, history: List[Dict], current_message: str) -> str:
        """대화 흐름 패턴 식별"""
        if len(history) < 2:
            return "initial_inquiry"
        
        recent_user_messages = [
            turn.get('content', '') for turn in history[-3:] 
            if turn.get('role') == 'user'
        ]
        
        # 후속 질문 패턴
        if any(word in current_message for word in ["그럼", "그러면", "그런데", "추가로", "또", "더"]):
            return "follow_up_question"
        
        # 상세 문의 패턴
        if any(word in current_message for word in ["자세히", "구체적으로", "정확히", "어떻게", "방법"]):
            return "detail_inquiry"
        
        # 문제 해결 패턴
        if any(word in current_message for word in ["문제", "안됨", "오류", "실패", "도움"]):
            return "problem_solving"
        
        # 새로운 주제 패턴
        current_categories = self._extract_categories(current_message)
        recent_categories = set()
        for msg in recent_user_messages:
            recent_categories.update(self._extract_categories(msg))
        
        if not any(cat in recent_categories for cat in current_categories):
            return "topic_change"
        
        return "topic_continuation"

    def _find_continuation_topics(self, history: List[Dict], current_message: str) -> List[str]:
        """연속된 주제 찾기"""
        if not history:
            return []
        
        recent_messages = [
            turn.get('content', '') for turn in history[-5:] 
            if turn.get('role') == 'user'
        ]
        
        topics = []
        for msg in recent_messages:
            topics.extend(self._extract_categories(msg))
        
        current_topics = self._extract_categories(current_message)
        continuation_topics = [topic for topic in topics if topic in current_topics]
        
        return list(set(continuation_topics))

    def _find_unresolved_issues(self, history: List[Dict]) -> List[str]:
        """미해결 이슈 찾기"""
        unresolved = []
        
        for i, turn in enumerate(history):
            if turn.get('role') == 'user':
                content = turn.get('content', '')
                
                # 문제 표현 키워드
                if any(word in content for word in ["문제", "안됨", "오류", "실패", "어려움"]):
                    # 다음 턴에서 해결되었는지 확인
                    if i + 1 < len(history):
                        next_turn = history[i + 1]
                        if next_turn.get('role') == 'assistant':
                            next_content = next_turn.get('content', '')
                            if not any(word in next_content for word in ["해결", "처리", "완료", "가능"]):
                                unresolved.append(content[:50] + "...")
        
        return unresolved

    def _determine_conversation_stage(self, history: List[Dict], current_message: str) -> str:
        """대화 단계 판단"""
        if not history:
            return "greeting"
        
        if len(history) <= 2:
            return "initial_inquiry"
        elif len(history) <= 6:
            return "information_gathering"
        elif len(history) <= 10:
            return "detailed_discussion"
        else:
            return "extended_consultation"

    def _extract_categories(self, text: str) -> List[str]:
        """보험 카테고리 추출"""
        found_categories = []
        text_lower = text.lower()
        
        for category, keywords in self.insurance_categories.items():
            if any(keyword in text_lower for keyword in keywords):
                found_categories.append(category)
        
        return found_categories

    def _extract_intents(self, text: str) -> List[str]:
        """의도 추출"""
        found_intents = []
        text_lower = text.lower()
        
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                found_intents.append(intent)
        
        return found_intents

    def _extract_emotions(self, text: str) -> List[str]:
        """감정 키워드 추출"""
        found_emotions = []
        text_lower = text.lower()
        
        for emotion, keywords in self.emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_emotions.append(emotion)
        
        return found_emotions

    def _extract_entities(self, text: str) -> List[str]:
        """개체명 추출 (간단한 패턴 기반)"""
        entities = []
        
        # 금액 패턴
        money_pattern = r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:원|만원|억원|천원)'
        money_matches = re.findall(money_pattern, text)
        entities.extend([f"{match}원" for match in money_matches])
        
        # 날짜 패턴
        date_pattern = r'(\d{4}년\s*\d{1,2}월\s*\d{1,2}일|\d{1,2}월\s*\d{1,2}일|\d{4}-\d{1,2}-\d{1,2})'
        date_matches = re.findall(date_pattern, text)
        entities.extend(date_matches)
        
        # 전화번호 패턴
        phone_pattern = r'(\d{3}-\d{4}-\d{4}|\d{4}-\d{4})'
        phone_matches = re.findall(phone_pattern, text)
        entities.extend(phone_matches)
        
        return entities

    def _extract_keywords(self, text: str) -> List[str]:
        """핵심 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 기법 사용 가능)
        keywords = []
        
        # 명사 추출 (간단한 패턴)
        noun_pattern = r'[가-힣]{2,}(?:보험|상품|서비스|계약|담보|특약|할인|혜택)'
        noun_matches = re.findall(noun_pattern, text)
        keywords.extend(noun_matches)
        
        return list(set(keywords))

    def _get_dominant_categories(self, text: str) -> List[str]:
        """주요 카테고리 추출"""
        category_counts = {}
        
        for category, keywords in self.insurance_categories.items():
            count = sum(1 for keyword in keywords if keyword in text.lower())
            if count > 0:
                category_counts[category] = count
        
        # 빈도순 정렬
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        return [cat for cat, count in sorted_categories[:3]]

    def _get_recurring_intents(self, messages: List[str]) -> List[str]:
        """반복되는 의도 찾기"""
        intent_counts = {}
        
        for message in messages:
            intents = self._extract_intents(message)
            for intent in intents:
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        # 2회 이상 나타난 의도만 반환
        return [intent for intent, count in intent_counts.items() if count >= 2]

    def _extract_conversation_topics(self, messages: List[str]) -> List[str]:
        """대화 주제 추출"""
        topics = set()
        
        for message in messages:
            topics.update(self._extract_categories(message))
            topics.update(self._extract_keywords(message))
        
        return list(topics)

    def _analyze_emotional_progression(self, user_messages: List[str]) -> Dict:
        """감정 변화 분석"""
        emotions_over_time = []
        
        for message in user_messages:
            emotions = self._extract_emotions(message)
            emotions_over_time.append(emotions)
        
        return {
            "progression": emotions_over_time,
            "current_emotions": emotions_over_time[-1] if emotions_over_time else [],
            "emotional_trend": self._determine_emotional_trend(emotions_over_time)
        }

    def _determine_emotional_trend(self, emotions_over_time: List[List[str]]) -> str:
        """감정 트렌드 판단"""
        if not emotions_over_time:
            return "neutral"
        
        recent_emotions = emotions_over_time[-2:] if len(emotions_over_time) >= 2 else emotions_over_time
        
        negative_emotions = ["불만", "불안"]
        positive_emotions = ["만족"]
        
        has_negative = any(any(emotion in turn for emotion in negative_emotions) for turn in recent_emotions)
        has_positive = any(any(emotion in turn for emotion in positive_emotions) for turn in recent_emotions)
        
        if has_negative and not has_positive:
            return "deteriorating"
        elif has_positive and not has_negative:
            return "improving"
        elif has_negative and has_positive:
            return "mixed"
        else:
            return "stable"


class ContextAwareQueryBuilder:
    """컨텍스트 인식 쿼리 빌더 - 대화 흐름 분석 결과를 바탕으로 검색 쿼리를 개선합니다."""
    
    def __init__(self, flow_analyzer: ConversationFlowAnalyzer):
        self.flow_analyzer = flow_analyzer

    def build_enhanced_query(self, history: List[Dict], current_message: str) -> Dict:
        """향상된 검색 쿼리 생성"""
        
        # 대화 흐름 분석
        flow_analysis = self.flow_analyzer.analyze_conversation_flow(history, current_message)
        
        # 기본 쿼리 (현재 메시지)
        base_query = current_message.strip()
        
        # 컨텍스트 강화 쿼리 생성
        enhanced_queries = self._generate_enhanced_queries(flow_analysis, base_query)
        
        return {
            "base_query": base_query,
            "enhanced_queries": enhanced_queries,
            "search_strategy": self._determine_search_strategy(flow_analysis),
            "context_weights": self._calculate_context_weights(flow_analysis),
            "flow_analysis": flow_analysis
        }

    def _generate_enhanced_queries(self, flow_analysis: Dict, base_query: str) -> List[Dict]:
        """강화된 쿼리들 생성"""
        enhanced_queries = []
        
        # 1. 기본 쿼리
        enhanced_queries.append({
            "query": base_query,
            "type": "base",
            "weight": 1.0,
            "description": "현재 메시지"
        })
        
        # 2. 컨텍스트 확장 쿼리
        context_query = self._build_context_query(flow_analysis, base_query)
        if context_query != base_query:
            enhanced_queries.append({
                "query": context_query,
                "type": "context_expanded",
                "weight": 0.8,
                "description": "대화 맥락 포함"
            })
        
        # 3. 주제 연속성 쿼리
        continuation_query = self._build_continuation_query(flow_analysis, base_query)
        if continuation_query:
            enhanced_queries.append({
                "query": continuation_query,
                "type": "topic_continuation",
                "weight": 0.7,
                "description": "주제 연속성 반영"
            })
        
        # 4. 미해결 이슈 쿼리
        unresolved_query = self._build_unresolved_query(flow_analysis, base_query)
        if unresolved_query:
            enhanced_queries.append({
                "query": unresolved_query,
                "type": "unresolved_issues",
                "weight": 0.6,
                "description": "미해결 이슈 관련"
            })
        
        return enhanced_queries

    def _build_context_query(self, flow_analysis: Dict, base_query: str) -> str:
        """컨텍스트 확장 쿼리 생성"""
        context = flow_analysis.get("context", {})
        current = flow_analysis.get("current", {})
        
        # 주요 카테고리 추가
        dominant_categories = context.get("dominant_categories", [])
        current_categories = current.get("categories", [])
        
        all_categories = list(set(dominant_categories + current_categories))
        
        # 반복되는 의도 추가
        recurring_intents = context.get("recurring_intents", [])
        current_intents = current.get("intents", [])
        
        all_intents = list(set(recurring_intents + current_intents))
        
        # 쿼리 확장
        query_parts = [base_query]
        
        if all_categories:
            category_text = " ".join(all_categories)
            query_parts.append(category_text)
        
        if all_intents:
            intent_keywords = {
                "가입문의": "가입 신청",
                "보상문의": "보험금 청구",
                "변경문의": "계약 변경",
                "조회문의": "정보 확인",
                "문제해결": "문제 해결"
            }
            
            intent_text = " ".join([intent_keywords.get(intent, intent) for intent in all_intents])
            query_parts.append(intent_text)
        
        return " ".join(query_parts)

    def _build_continuation_query(self, flow_analysis: Dict, base_query: str) -> Optional[str]:
        """주제 연속성 쿼리 생성"""
        continuation_topics = flow_analysis.get("continuation_topics", [])
        
        if not continuation_topics:
            return None
        
        topic_text = " ".join(continuation_topics)
        return f"{base_query} {topic_text}"

    def _build_unresolved_query(self, flow_analysis: Dict, base_query: str) -> Optional[str]:
        """미해결 이슈 쿼리 생성"""
        unresolved_issues = flow_analysis.get("unresolved_issues", [])
        
        if not unresolved_issues:
            return None
        
        # 미해결 이슈에서 키워드 추출
        issue_keywords = []
        for issue in unresolved_issues:
            # 간단한 키워드 추출
            words = issue.split()
            issue_keywords.extend([word for word in words if len(word) > 1])
        
        if issue_keywords:
            keyword_text = " ".join(list(set(issue_keywords))[:5])  # 최대 5개 키워드
            return f"{base_query} {keyword_text}"
        
        return None

    def _determine_search_strategy(self, flow_analysis: Dict) -> str:
        """검색 전략 결정"""
        flow_pattern = flow_analysis.get("flow_pattern", "initial_inquiry")
        conversation_stage = flow_analysis.get("conversation_stage", "greeting")
        
        if flow_pattern == "follow_up_question":
            return "context_heavy"
        elif flow_pattern == "detail_inquiry":
            return "precision_focused"
        elif flow_pattern == "problem_solving":
            return "solution_oriented"
        elif flow_pattern == "topic_change":
            return "broad_search"
        elif conversation_stage == "extended_consultation":
            return "comprehensive"
        else:
            return "balanced"

    def _calculate_context_weights(self, flow_analysis: Dict) -> Dict:
        """컨텍스트 가중치 계산"""
        flow_pattern = flow_analysis.get("flow_pattern", "initial_inquiry")
        conversation_stage = flow_analysis.get("conversation_stage", "greeting")
        
        weights = {
            "current_message": 1.0,
            "recent_context": 0.5,
            "overall_context": 0.3,
            "emotional_context": 0.2
        }
        
        # 흐름 패턴에 따른 가중치 조정
        if flow_pattern == "follow_up_question":
            weights["recent_context"] = 0.8
            weights["overall_context"] = 0.6
        elif flow_pattern == "topic_change":
            weights["recent_context"] = 0.2
            weights["overall_context"] = 0.1
        
        # 대화 단계에 따른 가중치 조정
        if conversation_stage == "extended_consultation":
            weights["overall_context"] = 0.7
            weights["emotional_context"] = 0.4
        
        return weights 