"""
캐싱 데코레이터
함수 결과를 자동으로 캐싱
"""

import functools
import hashlib
import json
import asyncio
from typing import Any, Callable, Optional, Union

from .memory_cache import get_memory_cache


def _generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """캐시 키 생성"""
    # 함수 이름과 인수들을 조합하여 유니크한 키 생성
    key_data = {
        'func': func_name,
        'args': args,
        'kwargs': kwargs
    }
    
    # JSON으로 직렬화 후 해시
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_result(
    ttl: int = 300,
    cache_instance: Optional[Any] = None,
    key_prefix: str = ""
):
    """
    동기 함수 결과 캐싱 데코레이터
    
    Args:
        ttl: 캐시 생존 시간 (초)
        cache_instance: 사용할 캐시 인스턴스
        key_prefix: 캐시 키 접두사
    """
    def decorator(func: Callable) -> Callable:
        cache = cache_instance or get_memory_cache()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{key_prefix}{_generate_cache_key(func.__name__, args, kwargs)}"
            
            # 캐시에서 조회
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 함수 실행 및 결과 캐싱
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        # 캐시 무효화 메소드 추가
        def invalidate(*args, **kwargs):
            cache_key = f"{key_prefix}{_generate_cache_key(func.__name__, args, kwargs)}"
            cache.delete(cache_key)
        
        wrapper.invalidate = invalidate
        wrapper.cache = cache
        
        return wrapper
    
    return decorator


def cache_async_result(
    ttl: int = 300,
    cache_instance: Optional[Any] = None,
    key_prefix: str = ""
):
    """
    비동기 함수 결과 캐싱 데코레이터
    
    Args:
        ttl: 캐시 생존 시간 (초)
        cache_instance: 사용할 캐시 인스턴스
        key_prefix: 캐시 키 접두사
    """
    def decorator(func: Callable) -> Callable:
        cache = cache_instance or get_memory_cache()
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{key_prefix}{_generate_cache_key(func.__name__, args, kwargs)}"
            
            # 캐시에서 조회
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 함수 실행 및 결과 캐싱
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        # 캐시 무효화 메소드 추가
        def invalidate(*args, **kwargs):
            cache_key = f"{key_prefix}{_generate_cache_key(func.__name__, args, kwargs)}"
            cache.delete(cache_key)
        
        wrapper.invalidate = invalidate
        wrapper.cache = cache
        
        return wrapper
    
    return decorator


def cache_method_result(ttl: int = 300, key_prefix: str = ""):
    """
    클래스 메소드 결과 캐싱 데코레이터
    인스턴스별로 캐시를 분리
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # 인스턴스 ID를 포함한 캐시 키
            instance_id = id(self)
            full_key_prefix = f"{key_prefix}_{instance_id}_"
            
            cache = get_memory_cache()
            cache_key = f"{full_key_prefix}{_generate_cache_key(func.__name__, args, kwargs)}"
            
            # 캐시에서 조회
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 메소드 실행 및 결과 캐싱
            result = func(self, *args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator


def conditional_cache(
    condition_func: Callable,
    ttl: int = 300,
    cache_instance: Optional[Any] = None
):
    """
    조건부 캐싱 데코레이터
    특정 조건을 만족할 때만 캐싱
    """
    def decorator(func: Callable) -> Callable:
        cache = cache_instance or get_memory_cache()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 조건 확인
            if not condition_func(*args, **kwargs):
                return func(*args, **kwargs)
            
            # 조건을 만족하면 캐싱 로직 실행
            cache_key = _generate_cache_key(func.__name__, args, kwargs)
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator