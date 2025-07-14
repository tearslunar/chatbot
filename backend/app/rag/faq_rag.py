from dotenv import load_dotenv
load_dotenv()
import json
import pickle
import os
import numpy as np
from typing import List, Dict
import faiss
import torch
import transformers
import packaging
print(f"[버전 체크] torch: {torch.__version__}, transformers: {transformers.__version__}, packaging: {packaging.__version__}")

# 캐싱 시스템 import
try:
    from ..cache.decorators import cache_result
except ImportError:
    # 스탠드얼론 실행 시 캐싱 비활성화
    def cache_result(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# 파일 경로
FAQ_JSON_PATH = os.path.join(os.path.dirname(__file__), 'hi_faq.json')
EMBEDDINGS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'faq_embeddings.pkl')

# 1. FAQ 데이터 로딩
def load_faq_data():
    with open(FAQ_JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# 2. 임베딩 생성/저장/모델 로딩 (운영 서버에서는 사용하지 않음)
def get_model():
    from sentence_transformers import SentenceTransformer
    # GPU 메모리 부족 시 CPU 사용 강제
    device = 'cpu' if not torch.cuda.is_available() or torch.cuda.get_device_properties(0).total_memory < 2000000000 else 'cuda'
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)

def create_and_save_embeddings():
    faqs = load_faq_data()
    model = get_model()
    texts = [f"Q: {faq['question']}\nA: {faq['content']}" for faq in faqs]
    embeddings = model.encode(texts, show_progress_bar=True)
    faq_embeddings = [
        {
            'faq': faq,
            'embedding': emb
        }
        for faq, emb in zip(faqs, embeddings)
    ]
    with open(EMBEDDINGS_PATH, 'wb') as f:
        pickle.dump(faq_embeddings, f)
    print(f"임베딩 {len(faq_embeddings)}개 저장 완료: {EMBEDDINGS_PATH}")

def load_embeddings() -> List[Dict]:
    with open(EMBEDDINGS_PATH, 'rb') as f:
        return pickle.load(f)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 3. FAISS 인덱스 및 임베딩 메모리 캐싱
faq_embeddings = None
faq_list = None
faiss_index = None
model = None  # 모델도 전역으로 미리 로딩

# 서버 시작 시 임베딩 및 인덱스, 모델 메모리 적재
if os.path.exists(EMBEDDINGS_PATH):
    loaded = load_embeddings()
    faq_list = [item['faq'] for item in loaded]
    faq_embeddings = np.array([item['embedding'] for item in loaded], dtype='float32')
    faiss_index = faiss.IndexFlatL2(faq_embeddings.shape[1])
    faiss_index.add(faq_embeddings)
    # 모델도 미리 로딩
    model = get_model()
else:
    print(f"[경고] FAQ 임베딩 파일이 존재하지 않습니다: {EMBEDDINGS_PATH}")

# query 임베딩 생성 함수 (실제 운영 시 외부 API로 대체 가능)
def get_query_embedding(query: str):
    global model
    if model is None:
        model = get_model()
    text = query.strip()
    return model.encode([text])[0].astype('float32')

@cache_result(ttl=600, key_prefix="faq_search_")  # 10분 캐싱
def search_faqs(query: str, top_n: int = 3) -> List[Dict]:
    """
    query: 사용자의 질문
    top_n: 반환할 FAQ 개수
    return: [{'faq': ..., 'score': ...}, ...]
    """
    if faiss_index is None or faq_embeddings is None or faq_list is None:
        return []
    query_emb = get_query_embedding(query).reshape(1, -1)
    D, I = faiss_index.search(query_emb, top_n)
    results = []
    for idx, score in zip(I[0], D[0]):
        if idx < 0 or idx >= len(faq_list):
            continue
        results.append({
            'faq': faq_list[idx],
            'score': float(-score)  # FAISS L2 거리이므로, -score로 유사도처럼 사용
        })
    return results


@cache_result(ttl=1800, key_prefix="query_embedding_")  # 30분 캐싱
def get_query_embedding_cached(query: str):
    """캐싱된 쿼리 임베딩 생성"""
    return get_query_embedding(query)

if __name__ == "__main__":
    create_and_save_embeddings() 