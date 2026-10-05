import React, { useState, useEffect } from 'react';

const AnimatedCounter = ({ value, duration = 500 }) => {
  const targetNumber = typeof value === 'number' ? value : parseInt(value, 10);
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (isNaN(targetNumber)) {
      return;
    }

    let startTimestamp = null;
    const startValue = 0;

    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);

      // Ease out quad
      const easeProgress = 1 - (1 - progress) * (1 - progress);
      const currentCount = Math.floor(easeProgress * (targetNumber - startValue) + startValue);

      setCount(currentCount);

      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        setCount(targetNumber);
      }
    };

    window.requestAnimationFrame(step);
  }, [targetNumber, duration]);

  if (isNaN(targetNumber)) {
    return <span>{value}</span>;
  }

  return <span>{count}</span>;
};

export default AnimatedCounter;
