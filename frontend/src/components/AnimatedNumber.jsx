import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

function AnimatedNumber({ value, duration = 1.5, className = '' }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const startValue = 0;
    const endValue = value;
    const startTime = Date.now();

    const animate = () => {
      const now = Date.now();
      const elapsed = (now - startTime) / 1000; // Convert to seconds
      const progress = Math.min(elapsed / duration, 1);

      // Easing function for smooth animation
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const currentValue = Math.floor(startValue + (endValue - startValue) * easeOutQuart);

      setDisplayValue(currentValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setDisplayValue(endValue);
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  return (
    <motion.span
      className={className}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      {displayValue.toLocaleString()}
    </motion.span>
  );
}

export default AnimatedNumber;







