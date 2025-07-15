from dotenv import load_dotenv
load_dotenv()
import json
import pickle
import os
import numpy as np
from typing import List, Dict, Tuple
import faiss
import glob

# GPU 매니저 import
try:
    from ..utils.gpu_manager import get_device, get_gpu_info, clear_gpu_memory
except ImportError:
    # GPU 매니저가 없으면 CPU 사용
    def get_device():
        return 'cpu'
    def get_gpu_info():
        return {'device': 'cpu'}
    def clear_gpu_memory():
        pass

# 파일 경로
TERMS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', '현대해상_약관_fixed_txt')
TERMS_EMBEDDINGS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'terms_embeddings.pkl')

def load_terms_data() -> List[Dict]:
    """약관 텍스트 파일들을 로딩하여 청크 단위로 분할"""
    terms_data = []
    
    # 모든 하위 폴더의 txt 파일 검색
    txt_files = glob.glob(os.path.join(TERMS_DIR, '**', '*.txt'), recursive=True)
    
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 파일 경로에서 카테고리 정보 추출
            rel_path = os.path.relpath(file_path, TERMS_DIR)
            path_parts = rel_path.split(os.sep)
            category = path_parts[0] if len(path_parts) > 0 else '기타'
            subcategory = path_parts[1] if len(path_parts) > 1 else ''
            filename = os.path.basename(file_path).replace('.txt', '')
            
            # 내용을 청크 단위로 분할 (조항 기준)
            chunks = split_terms_content(content, file_path)
            
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:  # 최소 길이 확인
                    terms_data.append({
                        'id': f"{category}_{subcategory}_{filename}_{i}",
                        'category': category,
                        'subcategory': subcategory,
                        'filename': filename,
                        'chunk_index': i,
                        'content': chunk.strip(),
                        'file_path': file_path
                    })
        except Exception as e:
            print(f"파일 읽기 오류 {file_path}: {e}")
            continue
    
    return terms_data

def split_terms_content(content: str, file_path: str) -> List[str]:
    """약관 텍스트를 의미 있는 청크로 분할"""
    chunks = []
    
    # 페이지 구분자로 1차 분할
    pages = content.split('--- Page ')
    
    for page in pages:
        if not page.strip():
            continue
            
        # 조항 구분자로 2차 분할
        sections = []
        
        # "제N조", "제N장" 패턴으로 분할
        import re
        section_pattern = r'(제\s*\d+\s*[조장])'
        parts = re.split(section_pattern, page)
        
        current_section = ""
        for i, part in enumerate(parts):
            if re.match(section_pattern, part):
                if current_section:
                    sections.append(current_section)
                current_section = part
            else:
                current_section += part
        
        if current_section:
            sections.append(current_section)
        
        # 섹션이 없으면 길이 기반 분할
        if not sections:
            sections = [page[i:i+1000] for i in range(0, len(page), 800)]
        
        for section in sections:
            if len(section.strip()) > 100:  # 최소 길이
                chunks.append(section.strip())
    
    return chunks

def get_model():
    """임베딩 모델 로딩"""
    from sentence_transformers import SentenceTransformer
    import torch
    # GPU 매니저를 통한 디바이스 선택
    device = get_device()
    print(f"[약관 모델] 디바이스: {device}")
    if device != 'cpu':
        gpu_info = get_gpu_info()
        print(f"[약관 모델] GPU 정보: {gpu_info}")
    
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)

def create_and_save_terms_embeddings():
    """약관 텍스트 임베딩 생성 및 저장"""
    print("약관 텍스트 데이터 로딩 중...")
    terms_data = load_terms_data()
    print(f"로딩된 약관 청크: {len(terms_data)}개")
    
    if not terms_data:
        print("약관 데이터가 없습니다.")
        return
    
    print("임베딩 모델 로딩 중...")
    model = get_model()
    
    print("임베딩 생성 중...")
    texts = [item['content'] for item in terms_data]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    terms_embeddings = [
        {
            'terms': terms,
            'embedding': emb
        }
        for terms, emb in zip(terms_data, embeddings)
    ]
    
    print("임베딩 저장 중...")
    with open(TERMS_EMBEDDINGS_PATH, 'wb') as f:
        pickle.dump(terms_embeddings, f)
    
    print(f"약관 임베딩 {len(terms_embeddings)}개 저장 완료: {TERMS_EMBEDDINGS_PATH}")

def load_terms_embeddings() -> List[Dict]:
    """저장된 약관 임베딩 로딩"""
    with open(TERMS_EMBEDDINGS_PATH, 'rb') as f:
        return pickle.load(f)

# 글로벌 변수
terms_embeddings = None
terms_list = None
terms_faiss_index = None
terms_model = None

# 서버 시작 시 약관 임베딩 및 인덱스 로딩
if os.path.exists(TERMS_EMBEDDINGS_PATH):
    print("약관 임베딩 로딩 중...")
    loaded = load_terms_embeddings()
    terms_list = [item['terms'] for item in loaded]
    terms_embeddings = np.array([item['embedding'] for item in loaded], dtype='float32')
    terms_faiss_index = faiss.IndexFlatL2(terms_embeddings.shape[1])
    terms_faiss_index.add(terms_embeddings)
    
    # 모델도 미리 로딩
    terms_model = get_model()
    print(f"약관 인덱스 로딩 완료: {len(terms_list)}개 청크")
else:
    print(f"[경고] 약관 임베딩 파일이 존재하지 않습니다: {TERMS_EMBEDDINGS_PATH}")
    print("python -m backend.app.rag.terms_rag 명령으로 임베딩을 생성하세요.")

def get_query_embedding(query: str):
    """쿼리 임베딩 생성"""
    global terms_model
    if terms_model is None:
        terms_model = get_model()
    text = query.strip()
    return terms_model.encode([text])[0].astype('float32')

def search_terms(query: str, top_n: int = 5) -> List[Dict]:
    """
    약관 텍스트에서 검색
    query: 사용자의 질문
    top_n: 반환할 약관 청크 개수
    return: [{'terms': ..., 'score': ...}, ...]
    """
    if terms_faiss_index is None or terms_embeddings is None or terms_list is None:
        return []
    
    query_emb = get_query_embedding(query).reshape(1, -1)
    D, I = terms_faiss_index.search(query_emb, top_n)
    
    results = []
    for idx, score in zip(I[0], D[0]):
        if idx < 0 or idx >= len(terms_list):
            continue
        results.append({
            'terms': terms_list[idx],
            'score': float(-score),  # FAISS L2 거리이므로, -score로 유사도처럼 사용
            'source': 'terms'
        })
    
    return results

if __name__ == "__main__":
    create_and_save_terms_embeddings() 