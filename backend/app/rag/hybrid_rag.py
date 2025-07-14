from typing import List, Dict, Tuple
from .faq_rag import search_faqs
from .terms_rag import search_terms

def normalize_scores(results: List[Dict], source_type: str) -> List[Dict]:
    """점수 정규화 및 소스 타입 추가"""
    if not results:
        return results
    
    # 점수 범위 정규화 (0-1)
    scores = [r['score'] for r in results]
    if len(scores) > 1:
        min_score, max_score = min(scores), max(scores)
        if max_score != min_score:
            for r in results:
                r['normalized_score'] = (r['score'] - min_score) / (max_score - min_score)
        else:
            for r in results:
                r['normalized_score'] = 1.0
    else:
        for r in results:
            r['normalized_score'] = 1.0
    
    # 소스 타입 추가
    for r in results:
        r['source_type'] = source_type
    
    return results

def apply_source_weights(faq_results: List[Dict], terms_results: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """소스별 가중치 적용"""
    # FAQ는 즉답성이 높으므로 약간의 가중치 부여
    FAQ_WEIGHT = 1.2
    TERMS_WEIGHT = 1.0
    
    for r in faq_results:
        r['weighted_score'] = r['normalized_score'] * FAQ_WEIGHT
    
    for r in terms_results:
        r['weighted_score'] = r['normalized_score'] * TERMS_WEIGHT
    
    return faq_results, terms_results

def merge_and_rank_results(faq_results: List[Dict], terms_results: List[Dict], 
                          max_results: int = 5) -> List[Dict]:
    """검색 결과 통합 및 최종 랭킹"""
    
    # 점수 정규화
    faq_normalized = normalize_scores(faq_results, 'faq')
    terms_normalized = normalize_scores(terms_results, 'terms')
    
    # 가중치 적용
    faq_weighted, terms_weighted = apply_source_weights(faq_normalized, terms_normalized)
    
    # 모든 결과 통합
    all_results = faq_weighted + terms_weighted
    
    # 가중치 점수로 정렬
    all_results.sort(key=lambda x: x['weighted_score'], reverse=True)
    
    # 최대 결과 수 제한
    return all_results[:max_results]

def search_hybrid(query: str, faq_top_n: int = 3, terms_top_n: int = 5, 
                 max_results: int = 5) -> List[Dict]:
    """
    이중 검색: FAQ + 약관 텍스트 동시 검색
    
    Args:
        query: 검색 쿼리
        faq_top_n: FAQ에서 가져올 최대 결과 수
        terms_top_n: 약관에서 가져올 최대 결과 수
        max_results: 최종 반환할 최대 결과 수
    
    Returns:
        통합 및 랭킹된 검색 결과 리스트
    """
    
    # 병렬 검색 실행
    faq_results = search_faqs(query, faq_top_n)
    terms_results = search_terms(query, terms_top_n)
    
    # 결과 통합 및 랭킹
    merged_results = merge_and_rank_results(faq_results, terms_results, max_results)
    
    return merged_results

def format_results_for_prompt(results: List[Dict]) -> str:
    """프롬프트에 포함할 수 있는 형태로 결과 포맷팅"""
    if not results:
        return ""
    
    formatted_parts = []
    
    for i, result in enumerate(results, 1):
        source_type = result.get('source_type', 'unknown')
        
        if source_type == 'faq':
            # FAQ 결과 포맷팅
            faq_data = result.get('faq', {})
            formatted_parts.append(
                f"[FAQ] Q: {faq_data.get('question', '')}\n"
                f"A: {faq_data.get('content', '')}"
            )
        elif source_type == 'terms':
            # 약관 결과 포맷팅
            terms_data = result.get('terms', {})
            category = terms_data.get('category', '')
            filename = terms_data.get('filename', '')
            content = terms_data.get('content', '')[:500]  # 내용 제한
            
            formatted_parts.append(
                f"[약관-{category}] {filename}\n"
                f"{content}..."
            )
    
    return "\n\n".join(formatted_parts)

def get_search_summary(results: List[Dict]) -> Dict:
    """검색 결과 요약 정보"""
    if not results:
        return {"total": 0, "faq_count": 0, "terms_count": 0}
    
    faq_count = sum(1 for r in results if r.get('source_type') == 'faq')
    terms_count = sum(1 for r in results if r.get('source_type') == 'terms')
    
    return {
        "total": len(results),
        "faq_count": faq_count,
        "terms_count": terms_count,
        "sources": list(set(r.get('source_type') for r in results))
    }

# 테스트용 함수
def test_hybrid_search():
    """이중 검색 테스트"""
    test_queries = [
        "자동차 사고가 났을 때 보험금 청구하는 방법",
        "의료실비보험 보장 범위",
        "보험료 납입 중단하면 어떻게 되나요",
        "화재보험 가입 조건"
    ]
    
    for query in test_queries:
        print(f"\n=== 검색 쿼리: {query} ===")
        results = search_hybrid(query, max_results=3)
        summary = get_search_summary(results)
        
        print(f"검색 결과 요약: {summary}")
        
        for i, result in enumerate(results, 1):
            source_type = result.get('source_type', 'unknown')
            score = result.get('weighted_score', 0)
            print(f"{i}. [{source_type.upper()}] 점수: {score:.3f}")
            
            if source_type == 'faq':
                faq_data = result.get('faq', {})
                print(f"   Q: {faq_data.get('question', '')}")
            elif source_type == 'terms':
                terms_data = result.get('terms', {})
                print(f"   파일: {terms_data.get('filename', '')}")
                print(f"   카테고리: {terms_data.get('category', '')}")

if __name__ == "__main__":
    test_hybrid_search() 