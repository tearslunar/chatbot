from dotenv import load_dotenv
load_dotenv()
import json
import pickle
from sentence_transformers import SentenceTransformer
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

# 2. 임베딩 모델 로딩 (한글 지원 다국어 모델)
def get_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 3. 임베딩 생성 및 저장
def create_and_save_embeddings():
    faqs = load_faq_data()
    model = get_model()
    # 질문+답변을 하나의 텍스트로 임베딩
    texts = [f"Q: {faq['question']}\nA: {faq['content']}" for faq in faqs]
    embeddings = model.encode(texts, show_progress_bar=True)
    # (FAQ, 임베딩) 쌍으로 저장
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

def embed_text(text: str, model=None):
    if model is None:
        model = get_model()
    return model.encode([text])[0]

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
    model = get_model()
    query_emb = embed_text(query, model)
    faq_embeddings = load_embeddings()
    scored = []
    for item in faq_embeddings:
        score = cosine_similarity(query_emb, item['embedding'])
        scored.append({'faq': item['faq'], 'score': score})
    # 유사도 내림차순 정렬 후 top_n 반환
    scored = sorted(scored, key=lambda x: x['score'], reverse=True)[:top_n]
    return scored

if __name__ == "__main__":
    create_and_save_embeddings() 