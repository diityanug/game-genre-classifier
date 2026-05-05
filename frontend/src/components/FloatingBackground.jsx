import React from 'react';
import { Gamepad2, Keyboard, Monitor, Mouse } from 'lucide-react';

const FloatingIcon = ({ Icon, size, top, left, duration, delay, isDark }) => (
  <div
    className={`absolute pointer-events-none select-none transition-colors duration-500 opacity-0 ${
      isDark ? 'text-red-500' : 'text-slate-300'
    }`}
    style={{ top, left, animation: `floatFade ${duration} linear infinite`, animationDelay: delay }}
  >
    <Icon size={size} strokeWidth={1.5} />
  </div>
);

const FloatingBackground = ({ isDark }) => {
  const backgroundIcons = [
    { Icon: Gamepad2, size: 80, top: '10%', left: '10%', duration: '20s', delay: '0s' },
    { Icon: Keyboard, size: 100, top: '20%', left: '80%', duration: '25s', delay: '-5s' },
    { Icon: Monitor, size: 70, top: '70%', left: '15%', duration: '22s', delay: '-10s' },
    { Icon: Gamepad2, size: 90, top: '60%', left: '75%', duration: '18s', delay: '-2s' },
    { Icon: Mouse, size: 60, top: '85%', left: '40%', duration: '30s', delay: '-15s' },
    { Icon: Keyboard, size: 80, top: '45%', left: '5%', duration: '21s', delay: '-12s' },
    { Icon: Gamepad2, size: 70, top: '40%', left: '90%', duration: '24s', delay: '-3s' },
  ];

  return (
    <div className="absolute inset-0 z-0 select-none pointer-events-none overflow-hidden">
      {backgroundIcons.map((iconData, index) => (
        <FloatingIcon key={index} {...iconData} isDark={isDark} />
      ))}
    </div>
  );
};

export default FloatingBackground;