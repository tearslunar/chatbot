from typing import List, Dict, Tuple, Optional
from .hybrid_rag import search_hybrid, merge_and_rank_results
from .conversation_flow import ConversationFlowAnalyzer, ContextAwareQueryBuilder
from .faq_rag import search_faqs
from .terms_rag import search_terms
import time

class EnhancedHybridRAG:
    """대화 흐름을 인식하는 향상된 하이브리드 RAG 검색 엔진"""
    
    def __init__(self):
        self.flow_analyzer = ConversationFlowAnalyzer()
        self.query_builder = ContextAwareQueryBuilder(self.flow_analyzer)
        
        # 검색 전략별 설정
        self.search_strategies = {
            "context_heavy": {
                "faq_weight": 1.2,
                "terms_weight": 1.0,
                "context_boost": 0.8,
                "max_results": 7
            },
            "precision_focused": {
                "faq_weight": 1.5,
                "terms_weight": 0.8,
                "context_boost": 0.3,
                "max_results": 5
            },
            "solution_oriented": {
                "faq_weight": 1.4,
                "terms_weight": 1.2,
                "context_boost": 0.6,
                "max_results": 6
            },
            "broad_search": {
                "faq_weight": 1.0,
                "terms_weight": 1.0,
                "context_boost": 0.2,
                "max_results": 8
            },
            "comprehensive": {
                "faq_weight": 1.3,
                "terms_weight": 1.1,
                "context_boost": 0.9,
                "max_results": 10
            },
            "balanced": {
                "faq_weight": 1.2,
                "terms_weight": 1.0,
                "context_boost": 0.5,
                "max_results": 5
            }
        }

    def search_with_conversation_flow(self, 
                                    history: List[Dict], 
                                    current_message: str,
                                    faq_top_n: int = 3,
                                    terms_top_n: int = 5,
                                    max_results: int = 5) -> Dict:
        """대화 흐름을 고려한 향상된 검색"""
        
        start_time = time.time()
        
        # 1. 대화 흐름 분석 및 쿼리 생성
        query_info = self.query_builder.build_enhanced_query(history, current_message)
        
        # 2. 검색 전략 결정
        search_strategy = query_info["search_strategy"]
        strategy_config = self.search_strategies.get(search_strategy, self.search_strategies["balanced"])
        
        # 3. 다중 쿼리 검색 실행
        all_results = []
        search_details = []
        
        for query_item in query_info["enhanced_queries"]:
            query = query_item["query"]
            query_type = query_item["type"]
            query_weight = query_item["weight"]
            
            # 각 쿼리로 검색 실행
            if query_type == "base":
                # 기본 검색 (더 많은 결과)
                results = search_hybrid(query, faq_top_n + 2, terms_top_n + 2, max_results + 3)
            else:
                # 컨텍스트 검색 (적은 결과)
                results = search_hybrid(query, faq_top_n, terms_top_n, max_results)
            
            # 쿼리 가중치 적용
            for result in results:
                result["query_weight"] = query_weight
                result["query_type"] = query_type
                result["original_score"] = result.get("weighted_score", 0)
                result["weighted_score"] = result["weighted_score"] * query_weight
            
            all_results.extend(results)
            search_details.append({
                "query": query,
                "type": query_type,
                "weight": query_weight,
                "results_count": len(results)
            })
        
        # 4. 결과 통합 및 중복 제거
        deduplicated_results = self._deduplicate_results(all_results)
        
        # 5. 검색 전략에 따른 재랭킹
        final_results = self._rerank_with_strategy(
            deduplicated_results, 
            strategy_config, 
            query_info["flow_analysis"]
        )
        
        # 6. 최종 결과 제한
        final_results = final_results[:strategy_config["max_results"]]
        
        search_time = time.time() - start_time
        
        return {
            "results": final_results,
            "search_metadata": {
                "search_strategy": search_strategy,
                "conversation_flow": query_info["flow_analysis"]["flow_pattern"],
                "conversation_stage": query_info["flow_analysis"]["conversation_stage"],
                "queries_used": search_details,
                "total_candidates": len(all_results),
                "deduplicated_count": len(deduplicated_results),
                "final_count": len(final_results),
                "search_time": search_time
            },
            "flow_analysis": query_info["flow_analysis"]
        }

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """검색 결과 중복 제거"""
        seen = set()
        deduplicated = []
        
        # 점수 기준으로 정렬 (높은 점수 우선)
        sorted_results = sorted(results, key=lambda x: x.get("weighted_score", 0), reverse=True)
        
        for result in sorted_results:
            # FAQ와 약관 구분하여 중복 체크
            if result.get("source_type") == "faq":
                faq_data = result.get("faq", {})
                identifier = f"faq_{faq_data.get('question', '')}"
            elif result.get("source_type") == "terms":
                terms_data = result.get("terms", {})
                identifier = f"terms_{terms_data.get('id', '')}"
            else:
                identifier = f"unknown_{str(result)[:50]}"
            
            if identifier not in seen:
                seen.add(identifier)
                deduplicated.append(result)
        
        return deduplicated

    def _rerank_with_strategy(self, 
                            results: List[Dict], 
                            strategy_config: Dict, 
                            flow_analysis: Dict) -> List[Dict]:
        """검색 전략에 따른 재랭킹"""
        
        for result in results:
            original_score = result.get("weighted_score", 0)
            
            # 소스 타입별 가중치 적용
            if result.get("source_type") == "faq":
                source_weight = strategy_config["faq_weight"]
            elif result.get("source_type") == "terms":
                source_weight = strategy_config["terms_weight"]
            else:
                source_weight = 1.0
            
            # 컨텍스트 부스트 적용
            context_boost = strategy_config["context_boost"]
            query_type = result.get("query_type", "base")
            
            if query_type != "base":
                context_multiplier = 1.0 + context_boost
            else:
                context_multiplier = 1.0
            
            # 대화 흐름 기반 추가 부스트
            flow_boost = self._calculate_flow_boost(result, flow_analysis)
            
            # 최종 점수 계산
            final_score = original_score * source_weight * context_multiplier * flow_boost
            result["final_score"] = final_score
            result["source_weight"] = source_weight
            result["context_multiplier"] = context_multiplier
            result["flow_boost"] = flow_boost
        
        # 최종 점수로 정렬
        return sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)

    def _calculate_flow_boost(self, result: Dict, flow_analysis: Dict) -> float:
        """대화 흐름 기반 부스트 계산"""
        boost = 1.0
        
        # 주제 연속성 부스트
        continuation_topics = flow_analysis.get("continuation_topics", [])
        if continuation_topics:
            content = ""
            if result.get("source_type") == "faq":
                faq_data = result.get("faq", {})
                content = f"{faq_data.get('question', '')} {faq_data.get('content', '')}"
            elif result.get("source_type") == "terms":
                terms_data = result.get("terms", {})
                content = terms_data.get("content", "")
            
            topic_matches = sum(1 for topic in continuation_topics if topic in content.lower())
            if topic_matches > 0:
                boost += 0.2 * topic_matches
        
        # 감정 상태 기반 부스트
        emotional_progression = flow_analysis.get("context", {}).get("emotional_progression", {})
        current_emotions = emotional_progression.get("current_emotions", [])
        
        if "긴급" in current_emotions:
            # FAQ 우선 부스트
            if result.get("source_type") == "faq":
                boost += 0.3
        elif "불만" in current_emotions or "불안" in current_emotions:
            # 해결 방안 관련 부스트
            content = ""
            if result.get("source_type") == "faq":
                faq_data = result.get("faq", {})
                content = faq_data.get("content", "")
            elif result.get("source_type") == "terms":
                terms_data = result.get("terms", {})
                content = terms_data.get("content", "")
            
            if any(word in content for word in ["해결", "처리", "방법", "절차"]):
                boost += 0.25
        
        return boost

    def get_search_explanation(self, search_result: Dict) -> str:
        """검색 결과에 대한 설명 생성"""
        metadata = search_result.get("search_metadata", {})
        flow_analysis = search_result.get("flow_analysis", {})
        
        strategy = metadata.get("search_strategy", "balanced")
        flow_pattern = metadata.get("conversation_flow", "initial_inquiry")
        stage = metadata.get("conversation_stage", "greeting")
        
        explanation_parts = []
        
        # 검색 전략 설명
        strategy_descriptions = {
            "context_heavy": "이전 대화 내용을 중점적으로 고려하여",
            "precision_focused": "정확한 정보에 집중하여",
            "solution_oriented": "문제 해결에 특화하여",
            "broad_search": "폭넓은 관점에서",
            "comprehensive": "종합적인 관점에서",
            "balanced": "균형잡힌 방식으로"
        }
        
        explanation_parts.append(strategy_descriptions.get(strategy, ""))
        
        # 대화 흐름 설명
        flow_descriptions = {
            "follow_up_question": "이전 질문의 연장선에서",
            "detail_inquiry": "상세한 정보 요청에 대해",
            "problem_solving": "문제 해결을 위해",
            "topic_change": "새로운 주제에 대해",
            "topic_continuation": "기존 주제를 이어서"
        }
        
        if flow_pattern in flow_descriptions:
            explanation_parts.append(flow_descriptions[flow_pattern])
        
        explanation_parts.append("검색했습니다.")
        
        return " ".join(explanation_parts)

# 전역 인스턴스 생성
enhanced_rag = EnhancedHybridRAG()

def search_with_conversation_context(history: List[Dict], 
                                   current_message: str,
                                   faq_top_n: int = 3,
                                   terms_top_n: int = 5,
                                   max_results: int = 5) -> Dict:
    """대화 컨텍스트를 고려한 검색 (메인 API)"""
    return enhanced_rag.search_with_conversation_flow(
        history, current_message, faq_top_n, terms_top_n, max_results
    )

def get_search_explanation(search_result: Dict) -> str:
    """검색 설명 생성 (헬퍼 함수)"""
    return enhanced_rag.get_search_explanation(search_result) 