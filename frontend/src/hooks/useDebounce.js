import { useState, useEffect } from 'react';

/**
 * 디바운스 훅
 * 입력값 변경 시 지연된 업데이트로 성능 최적화
 */
export function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}