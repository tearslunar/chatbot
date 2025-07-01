from dotenv import load_dotenv
load_dotenv()
import json
import pickle
import os
import numpy as np
from typing import List, Dict

# 파일 경로
FAQ_JSON_PATH = os.path.join(os.path.dirname(__file__), 'hi_faq.json')
EMBEDDINGS_PATH = os.path.join(os.path.dirname(__file__), 'faq_embeddings.pkl')

# 1. FAQ 데이터 로딩
def load_faq_data():
    with open(FAQ_JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# 2. 임베딩 생성/저장/모델 로딩 (운영 서버에서는 사용하지 않음)
def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

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

def search_faqs(query: str, top_n: int = 3) -> List[Dict]:
    """
    query: 사용자의 질문
    top_n: 반환할 FAQ 개수
    return: [{'faq': ..., 'score': ...}, ...]
    """
    # 운영 서버에서는 미리 생성된 임베딩만 사용
    # query 임베딩은 별도 API/서비스에서 생성해 전달받거나, 간단한 키워드 매칭 등으로 대체 가능
    # 여기서는 임시로 모든 FAQ에 대해 0점(랜덤) 유사도 반환 (실제 운영 시 query 임베딩 필요)
    faq_embeddings = load_embeddings()
    # TODO: query 임베딩 생성이 필요하면 별도 서비스/API로 분리
    # 현재는 유사도 계산 없이 FAQ만 반환 (임시)
    scored = [
        {'faq': item['faq'], 'score': 1.0}  # score는 임시로 1.0
        for item in faq_embeddings[:top_n]
    ]
    return scored

if __name__ == "__main__":
    create_and_save_embeddings() 