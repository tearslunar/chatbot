import { useRef, useCallback } from 'react';

/**
 * 스로틀 훅
 * 함수 호출 빈도를 제한하여 성능 최적화
 */
export function useThrottle(callback, delay) {
  const lastRun = useRef(Date.now());

  return useCallback((...args) => {
    if (Date.now() - lastRun.current >= delay) {
      callback(...args);
      lastRun.current = Date.now();
    }
  }, [callback, delay]);
}