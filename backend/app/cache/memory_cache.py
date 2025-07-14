"""
메모리 캐시 구현
"""

import time
import threading
from typing import Any, Optional, Dict
from dataclasses import dataclass


@dataclass
class CacheItem:
    """캐시 아이템"""
    value: Any
    expiry: float
    created_at: float


class MemoryCache:
    """메모리 기반 캐시"""
    
    def __init__(self, default_ttl: int = 300):  # 기본 5분
        self._cache: Dict[str, CacheItem] = {}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            
            item = self._cache[key]
            
            # 만료 확인
            if time.time() > item.expiry:
                del self._cache[key]
                self.misses += 1
                return None
            
            self.hits += 1
            return item.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """캐시에 값 저장"""
        with self._lock:
            ttl = ttl or self.default_ttl
            expiry = time.time() + ttl
            
            self._cache[key] = CacheItem(
                value=value,
                expiry=expiry,
                created_at=time.time()
            )
    
    def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """캐시 전체 삭제"""
        with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0
    
    def cleanup_expired(self) -> int:
        """만료된 캐시 정리"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, item in self._cache.items()
                if current_time > item.expiry
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / max(total_requests, 1)
            
            return {
                "total_items": len(self._cache),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "memory_usage_estimate": sum(
                    len(str(item.value)) for item in self._cache.values()
                )
            }
    
    def exists(self, key: str) -> bool:
        """키 존재 여부 확인"""
        return self.get(key) is not None
    
    def get_or_set(self, key: str, default_func, ttl: Optional[int] = None) -> Any:
        """값 조회 또는 설정"""
        value = self.get(key)
        if value is None:
            value = default_func()
            self.set(key, value, ttl)
        return value


# 전역 메모리 캐시 인스턴스
memory_cache = MemoryCache()


def get_memory_cache() -> MemoryCache:
    """메모리 캐시 인스턴스 반환"""
    return memory_cache