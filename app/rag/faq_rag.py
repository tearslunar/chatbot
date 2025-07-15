from dotenv import load_dotenv
load_dotenv()

import json
import pickle
import os
import numpy as np
from typing import List, Dict, Optional
import faiss
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 파일 경로
FAQ_JSON_PATH = os.path.join(os.path.dirname(__file__), 'hi_faq.json')
EMBEDDINGS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'faq_embeddings.pkl')

def check_dependencies():
    """AI 라이브러리 의존성 및 버전 체크"""
    try:
        import torch
        import transformers
        import packaging
        import sentence_transformers
        
        logger.info(f"[의존성 체크] torch: {torch.__version__}")
        logger.info(f"[의존성 체크] transformers: {transformers.__version__}")
        logger.info(f"[의존성 체크] packaging: {packaging.__version__}")
        logger.info(f"[의존성 체크] sentence-transformers: {sentence_transformers.__version__}")
        
        # 호환성 체크
        torch_version = tuple(map(int, torch.__version__.split('.')[:2]))
        if torch_version < (2, 0):
            logger.warning(f"⚠️ torch 버전이 낮습니다: {torch.__version__} (권장: 2.0+)")
        
        return True
    except ImportError as e:
        logger.error(f"❌ 필수 라이브러리 import 실패: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 의존성 체크 중 오류: {e}")
        return False

# 1. FAQ 데이터 로딩
def load_faq_data() -> Optional[List[Dict]]:
    """FAQ 데이터를 안전하게 로딩"""
    try:
        if not os.path.exists(FAQ_JSON_PATH):
            logger.error(f"FAQ 파일이 존재하지 않습니다: {FAQ_JSON_PATH}")
            return None
            
        with open(FAQ_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"FAQ 데이터 로딩 완료: {len(data)}개 항목")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"FAQ JSON 파싱 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"FAQ 데이터 로딩 중 오류: {e}")
        return None

# 2. 임베딩 생성/저장/모델 로딩 (운영 서버에서는 사용하지 않음)
def get_model():
    """SentenceTransformer 모델을 안전하게 로딩"""
    try:
        # 의존성 먼저 체크
        if not check_dependencies():
            raise ImportError("필수 의존성이 누락되었습니다")
            
        from sentence_transformers import SentenceTransformer
        import torch
        
        # CPU 사용 강제
        device = 'cpu'
        logger.info("CPU 사용으로 설정됨")
        
        logger.info(f"SentenceTransformer 모델 로딩 중... (device: {device})")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)
        logger.info("✅ SentenceTransformer 모델 로딩 완료")
        return model
        
    except ImportError as e:
        logger.error(f"❌ SentenceTransformer import 실패: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ 모델 로딩 실패: {e}")
        raise

def create_and_save_embeddings():
    """임베딩 생성 및 저장 (에러 처리 강화)"""
    try:
        faqs = load_faq_data()
        if not faqs:
            logger.error("FAQ 데이터가 없어 임베딩을 생성할 수 없습니다")
            return False
            
        model = get_model()
        if not model:
            logger.error("모델 로딩 실패로 임베딩을 생성할 수 없습니다")
            return False
            
        logger.info("임베딩 생성 중...")
        texts = [f"Q: {faq['question']}\nA: {faq['content']}" for faq in faqs]
        embeddings = model.encode(texts, show_progress_bar=True)
        
        faq_embeddings = [
            {
                'faq': faq,
                'embedding': emb
            }
            for faq, emb in zip(faqs, embeddings)
        ]
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(EMBEDDINGS_PATH), exist_ok=True)
        
        with open(EMBEDDINGS_PATH, 'wb') as f:
            pickle.dump(faq_embeddings, f)
        
        logger.info(f"✅ 임베딩 {len(faq_embeddings)}개 저장 완료: {EMBEDDINGS_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 임베딩 생성/저장 실패: {e}")
        return False

def load_embeddings() -> Optional[List[Dict]]:
    """임베딩을 안전하게 로딩"""
    try:
        if not os.path.exists(EMBEDDINGS_PATH):
            logger.warning(f"임베딩 파일이 존재하지 않습니다: {EMBEDDINGS_PATH}")
            return None
            
        with open(EMBEDDINGS_PATH, 'rb') as f:
            data = pickle.load(f)
            logger.info(f"임베딩 로딩 완료: {len(data)}개 항목")
            return data
    except Exception as e:
        logger.error(f"임베딩 로딩 실패: {e}")
        return None

def cosine_similarity(a, b):
    """코사인 유사도 계산 (안전한 구현)"""
    try:
        a = np.array(a)
        b = np.array(b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return np.dot(a, b) / (norm_a * norm_b)
    except Exception as e:
        logger.error(f"코사인 유사도 계산 오류: {e}")
        return 0.0

# 3. FAISS 인덱스 및 임베딩 메모리 캐싱
faq_embeddings = None
faq_list = None
faiss_index = None
model = None  # 모델도 전역으로 미리 로딩

def initialize_faq_system():
    """FAQ 시스템 초기화 (안전한 초기화)"""
    global faq_embeddings, faq_list, faiss_index, model
    
    try:
        # 의존성 체크
        if not check_dependencies():
            logger.error("의존성 체크 실패 - FAQ 시스템을 초기화할 수 없습니다")
            return False
        
        # 임베딩 로딩
        if os.path.exists(EMBEDDINGS_PATH):
            loaded = load_embeddings()
            if loaded:
                faq_list = [item['faq'] for item in loaded]
                faq_embeddings = np.array([item['embedding'] for item in loaded], dtype='float32')
                
                # FAISS 인덱스 생성
                faiss_index = faiss.IndexFlatL2(faq_embeddings.shape[1])
                faiss_index.add(faq_embeddings)
                
                # 모델 미리 로딩
                model = get_model()
                
                logger.info("✅ FAQ 시스템 초기화 완료")
                return True
            else:
                logger.error("임베딩 로딩 실패")
                return False
        else:
            logger.warning(f"FAQ 임베딩 파일이 존재하지 않습니다: {EMBEDDINGS_PATH}")
            return False
            
    except Exception as e:
        logger.error(f"FAQ 시스템 초기화 실패: {e}")
        return False

# query 임베딩 생성 함수 (실제 운영 시 외부 API로 대체 가능)
def get_query_embedding(query: str) -> Optional[np.ndarray]:
    """쿼리 임베딩 생성 (에러 처리 강화)"""
    global model
    
    try:
        if model is None:
            model = get_model()
            if model is None:
                logger.error("모델 로딩 실패")
                return None
        
        text = query.strip()
        if not text:
            logger.warning("빈 쿼리입니다")
            return None
            
        embedding = model.encode([text])[0].astype('float32')
        return embedding
        
    except Exception as e:
        logger.error(f"쿼리 임베딩 생성 실패: {e}")
        return None

def search_faqs(query: str, top_n: int = 3) -> List[Dict]:
    """
    FAQ 검색 (안전한 구현)
    query: 사용자의 질문
    top_n: 반환할 FAQ 개수
    return: [{'faq': ..., 'score': ...}, ...]
    """
    try:
        if faiss_index is None or faq_embeddings is None or faq_list is None:
            logger.warning("FAQ 시스템이 초기화되지 않았습니다")
            return []
        
        if not query or not query.strip():
            logger.warning("빈 쿼리로 검색할 수 없습니다")
            return []
        
        query_emb = get_query_embedding(query)
        if query_emb is None:
            logger.error("쿼리 임베딩 생성 실패")
            return []
            
        query_emb = query_emb.reshape(1, -1)
        D, I = faiss_index.search(query_emb, min(top_n, len(faq_list)))
        
        results = []
        for idx, score in zip(I[0], D[0]):
            if idx < 0 or idx >= len(faq_list):
                continue
            results.append({
                'faq': faq_list[idx],
                'score': float(-score)  # FAISS L2 거리이므로, -score로 유사도처럼 사용
            })
        
        logger.info(f"FAQ 검색 완료: 쿼리='{query}', 결과={len(results)}개")
        return results
        
    except Exception as e:
        logger.error(f"FAQ 검색 중 오류: {e}")
        return []

# 서버 시작 시 FAQ 시스템 초기화
try:
    success = initialize_faq_system()
    if success:
        logger.info("🚀 FAQ 시스템이 성공적으로 초기화되었습니다")
    else:
        logger.warning("⚠️ FAQ 시스템 초기화에 실패했습니다. 일부 기능이 제한될 수 있습니다")
except Exception as e:
    logger.error(f"❌ FAQ 시스템 초기화 중 치명적 오류: {e}")

if __name__ == "__main__":
    create_and_save_embeddings() 