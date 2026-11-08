import { useEffect, useState, useRef } from 'react';

/**
 * Detects whether the user prefers reduced motion.
 */
export function useReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const listener = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', listener);
    } else {
      mediaQuery.addListener(listener);
    }

    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', listener);
      } else {
        mediaQuery.removeListener(listener);
      }
    };
  }, []);

  return prefersReducedMotion;
}

/**
 * Hook to animate numbers smoothly (count-up on mount, smooth transition on changes).
 * Uses cubic-bezier ease-out: 1 - Math.pow(1 - t, 3)
 */
export function useCountUp(
  targetValue: number,
  durationMs: number = 1000,
  decimals: number = 0
): number {
  const reducedMotion = useReducedMotion();
  const [displayValue, setDisplayValue] = useState<number>(() => targetValue);
  const startValueRef = useRef<number>(0);
  const targetValueRef = useRef<number>(targetValue);
  const startTimeRef = useRef<number | null>(null);
  const rafIdRef = useRef<number | null>(null);
  const isFirstMountRef = useRef<boolean>(true);

  useEffect(() => {
    if (reducedMotion) {
      setDisplayValue(targetValue);
      startValueRef.current = targetValue;
      targetValueRef.current = targetValue;
      return;
    }

    const startVal = isFirstMountRef.current ? 0 : displayValue;
    isFirstMountRef.current = false;

    // If target hasn't changed, do not re-run animation
    if (startVal === targetValue && targetValueRef.current === targetValue) {
      return;
    }

    startValueRef.current = startVal;
    targetValueRef.current = targetValue;
    startTimeRef.current = null;

    const animate = (currentTime: number) => {
      if (startTimeRef.current === null) {
        startTimeRef.current = currentTime;
      }

      const elapsed = currentTime - startTimeRef.current;
      const progress = Math.min(elapsed / Math.max(durationMs, 1), 1);

      // Ease-out cubic: 1 - (1 - t)^3
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = startValueRef.current + (targetValue - startValueRef.current) * easeOut;

      const factor = Math.pow(10, decimals);
      setDisplayValue(Math.round(current * factor) / factor);

      if (progress < 1) {
        rafIdRef.current = requestAnimationFrame(animate);
      } else {
        setDisplayValue(targetValue);
      }
    };

    rafIdRef.current = requestAnimationFrame(animate);

    return () => {
      if (rafIdRef.current !== null) {
        cancelAnimationFrame(rafIdRef.current);
      }
    };
  }, [targetValue, durationMs, decimals, reducedMotion]);

  return displayValue;
}

