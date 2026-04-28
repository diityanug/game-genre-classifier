import React, { useState, useEffect } from 'react';
import '../style/global.css';
import GenreClassifier from './components/GenreClassifier';
import { Gamepad2, Keyboard, Monitor, Mouse } from 'lucide-react';

const FloatingIcon = ({ Icon, size, top, left, duration, delay, isDark }) => (
  <div
    className={`absolute pointer-events-none select-none transition-colors duration-500 opacity-0 ${
      isDark ? 'text-red-500' : 'text-slate-300'
    }`}
    style={{
      top,
      left,
      animation: `floatFade ${duration} linear infinite`,
      animationDelay: delay,
    }}
  >
    <Icon size={size} strokeWidth={1.5} />
  </div>
);

function App() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    if (isDark) {
      document.body.classList.add('dark-theme');
      document.body.style.backgroundColor = '#0f172a';
    } else {
      document.body.classList.remove('dark-theme');
      document.body.style.backgroundColor = '#FDFBF7';
    }
  }, [isDark]);

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
    <div className={`relative min-h-screen py-10 overflow-hidden transition-colors duration-500 ${isDark ? 'bg-[#0f172a]' : 'bg-[#FDFBF7]'}`}>
      
      <style>
        {`
          @keyframes floatFade {
            0% { transform: translateY(0px) rotate(0deg); opacity: 0; }
            20% { opacity: 0.2; } 
            50% { transform: translateY(-40px) rotate(10deg); opacity: 0.4; }
            80% { opacity: 0.2; }
            100% { transform: translateY(-80px) rotate(-10deg); opacity: 0; }
          }
        `}
      </style>

      <div className="absolute inset-0 z-0 select-none pointer-events-none overflow-hidden">
        {backgroundIcons.map((iconData, index) => (
          <FloatingIcon
            key={index}
            Icon={iconData.Icon}
            size={iconData.size}
            top={iconData.top}
            left={iconData.left}
            duration={iconData.duration}
            delay={iconData.delay}
            isDark={isDark}
          />
        ))}
      </div>

      <div className="relative z-10 container mx-auto">
        <GenreClassifier isDark={isDark} setIsDark={setIsDark} />
      </div>
    </div>
  );
}

export default App;