"""
GPU 관리 유틸리티
2080Ti GPU 우선 선택 및 GPU 메모리 관리
"""

import torch
import logging
from typing import Optional, Tuple
from ..config.settings import settings

logger = logging.getLogger(__name__)

class GPUManager:
    """GPU 관리 클래스"""
    
    def __init__(self):
        self.device = None
        self.gpu_id = None
        self._setup_device()
    
    def _setup_device(self):
        """GPU 설정 및 디바이스 선택"""
        if not settings.use_gpu or not torch.cuda.is_available():
            self.device = 'cpu'
            logger.info("CPU 사용으로 설정됨")
            return
        
        try:
            # 2080Ti GPU 찾기
            preferred_gpu_id = self._find_preferred_gpu()
            
            if preferred_gpu_id is not None:
                self.gpu_id = preferred_gpu_id
                self.device = f'cuda:{preferred_gpu_id}'
                logger.info(f"선택된 GPU: {torch.cuda.get_device_name(preferred_gpu_id)} (ID: {preferred_gpu_id})")
            else:
                # 2080Ti가 없으면 첫 번째 사용 가능한 GPU 사용
                self.gpu_id = 0
                self.device = 'cuda:0'
                logger.info(f"기본 GPU 사용: {torch.cuda.get_device_name(0)}")
            
            # GPU 메모리 설정
            self._setup_gpu_memory()
            
        except Exception as e:
            logger.warning(f"GPU 설정 실패: {e}")
            if settings.fallback_to_cpu:
                self.device = 'cpu'
                logger.info("CPU로 폴백됨")
            else:
                raise
    
    def _find_preferred_gpu(self) -> Optional[int]:
        """선호하는 GPU (2080Ti) 찾기"""
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            if settings.preferred_gpu_name.lower() in gpu_name.lower():
                return i
        return None
    
    def _setup_gpu_memory(self):
        """GPU 메모리 설정"""
        if self.device == 'cpu':
            return
        
        try:
            # GPU 메모리 캐시 정리
            torch.cuda.empty_cache()
            
            # 메모리 사용량 제한 설정
            total_memory = torch.cuda.get_device_properties(self.gpu_id).total_memory
            allocated_memory = int(total_memory * settings.gpu_memory_fraction)
            
            logger.info(f"GPU 메모리 설정: {allocated_memory / 1024**3:.2f}GB / {total_memory / 1024**3:.2f}GB")
            
        except Exception as e:
            logger.warning(f"GPU 메모리 설정 실패: {e}")
    
    def get_device(self) -> str:
        """현재 디바이스 반환"""
        return self.device
    
    def get_gpu_info(self) -> dict:
        """GPU 정보 반환"""
        if self.device == 'cpu':
            return {'device': 'cpu', 'gpu_count': 0}
        
        info = {
            'device': self.device,
            'gpu_id': self.gpu_id,
            'gpu_name': torch.cuda.get_device_name(self.gpu_id),
            'gpu_count': torch.cuda.device_count(),
            'memory_allocated': torch.cuda.memory_allocated(self.gpu_id) / 1024**3,
            'memory_reserved': torch.cuda.memory_reserved(self.gpu_id) / 1024**3,
            'memory_total': torch.cuda.get_device_properties(self.gpu_id).total_memory / 1024**3
        }
        return info
    
    def clear_memory(self):
        """GPU 메모리 정리"""
        if self.device != 'cpu':
            torch.cuda.empty_cache()
            logger.debug("GPU 메모리 캐시 정리됨")

# 전역 GPU 매니저 인스턴스
gpu_manager = GPUManager()

def get_device() -> str:
    """현재 디바이스 반환 (편의 함수)"""
    return gpu_manager.get_device()

def get_gpu_info() -> dict:
    """GPU 정보 반환 (편의 함수)"""
    return gpu_manager.get_gpu_info()

def clear_gpu_memory():
    """GPU 메모리 정리 (편의 함수)"""
    gpu_manager.clear_memory() 