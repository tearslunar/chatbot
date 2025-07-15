"""
GPU 상태 확인 API 라우터
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import torch

router = APIRouter(prefix="/gpu", tags=["GPU"])

@router.get("/status")
async def get_gpu_status() -> Dict[str, Any]:
    """GPU 상태 정보 반환"""
    try:
        from ..utils.gpu_manager import get_gpu_info, get_device
        
        device = get_device()
        gpu_info = get_gpu_info()
        
        # 전체 GPU 목록 정보
        all_gpus = []
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                memory_total = torch.cuda.get_device_properties(i).total_memory / 1024**3
                memory_allocated = torch.cuda.memory_allocated(i) / 1024**3
                memory_reserved = torch.cuda.memory_reserved(i) / 1024**3
                
                all_gpus.append({
                    'id': i,
                    'name': gpu_name,
                    'memory_total_gb': round(memory_total, 2),
                    'memory_allocated_gb': round(memory_allocated, 2),
                    'memory_reserved_gb': round(memory_reserved, 2),
                    'memory_usage_percent': round((memory_allocated / memory_total) * 100, 1)
                })
        
        return {
            'current_device': device,
            'cuda_available': torch.cuda.is_available(),
            'cuda_version': torch.version.cuda if torch.cuda.is_available() else None,
            'pytorch_version': torch.__version__,
            'selected_gpu': gpu_info,
            'all_gpus': all_gpus
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPU 상태 확인 실패: {str(e)}")

@router.post("/clear-memory")
async def clear_gpu_memory() -> Dict[str, str]:
    """GPU 메모리 정리"""
    try:
        from ..utils.gpu_manager import clear_gpu_memory
        clear_gpu_memory()
        return {"message": "GPU 메모리 캐시가 정리되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPU 메모리 정리 실패: {str(e)}")

@router.get("/test")
async def test_gpu_inference() -> Dict[str, Any]:
    """GPU 추론 테스트"""
    try:
        import torch
        from ..utils.gpu_manager import get_device
        
        device = get_device()
        
        # 간단한 텐서 연산으로 GPU 테스트
        if device != 'cpu':
            x = torch.randn(1000, 1000).to(device)
            y = torch.randn(1000, 1000).to(device)
            z = torch.mm(x, y)
            
            return {
                "device": device,
                "test_result": "success",
                "tensor_shape": list(z.shape),
                "computation_time": "GPU 연산 완료"
            }
        else:
            return {
                "device": device,
                "test_result": "cpu_mode",
                "message": "CPU 모드에서 실행 중"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPU 테스트 실패: {str(e)}") 