import React from 'react';
import { Gamepad2, Keyboard, Monitor, Mouse } from 'lucide-react';

const FloatingIcon = ({ Icon, size, top, left, duration, delay }) => (
  <div
    className="absolute pointer-events-none select-none text-slate-300"
    style={{ 
      top, left, 
      animation: `floatFade ${duration} linear infinite`, 
      animationDelay: delay,
      opacity: 0 
    }}
  >
    <Icon size={size} strokeWidth={1.5} />
  </div>
);

const FloatingBackground = () => {
  const backgroundIcons = [
    { Icon: Gamepad2, size: 80, top: '80%', left: '10%', duration: '15s', delay: '0s' },
    { Icon: Keyboard, size: 100, top: '90%', left: '80%', duration: '18s', delay: '-5s' },
    { Icon: Monitor, size: 70, top: '70%', left: '15%', duration: '16s', delay: '-10s' },
    { Icon: Gamepad2, size: 90, top: '85%', left: '75%', duration: '14s', delay: '-2s' },
    { Icon: Mouse, size: 60, top: '95%', left: '40%', duration: '20s', delay: '-15s' },
    { Icon: Keyboard, size: 80, top: '75%', left: '5%', duration: '17s', delay: '-12s' },
    { Icon: Gamepad2, size: 70, top: '80%', left: '90%', duration: '19s', delay: '-3s' },
  ];

  return (
    <div className="fixed inset-0 z-0 select-none pointer-events-none overflow-hidden">
      {backgroundIcons.map((iconData, index) => (
        <FloatingIcon key={index} {...iconData} />
      ))}
    </div>
  );
};

export default FloatingBackground;