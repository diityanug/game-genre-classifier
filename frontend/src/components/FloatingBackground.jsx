import React from 'react';
import { 
  Gamepad2, Keyboard, Monitor, Mouse, 
  Headphones, Cpu, Sword, Target, Trophy, 
  Zap, Rocket, Ghost, Puzzle, Disc 
} from 'lucide-react';

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
    { Icon: Headphones, size: 85, top: '85%', left: '25%', duration: '22s', delay: '-7s' },
    { Icon: Cpu, size: 65, top: '75%', left: '60%', duration: '16s', delay: '-14s' },
    { Icon: Sword, size: 90, top: '95%', left: '50%', duration: '21s', delay: '-1s' },
    { Icon: Target, size: 75, top: '82%', left: '85%', duration: '17s', delay: '-9s' },
    { Icon: Trophy, size: 60, top: '88%', left: '18%', duration: '19s', delay: '-6s' },
    { Icon: Zap, size: 50, top: '72%', left: '35%', duration: '15s', delay: '-11s' },
    { Icon: Rocket, size: 110, top: '98%', left: '70%', duration: '24s', delay: '-4s' },
    { Icon: Ghost, size: 75, top: '78%', left: '45%', duration: '18s', delay: '-16s' },
    { Icon: Puzzle, size: 65, top: '85%', left: '55%', duration: '20s', delay: '-8s' },
    { Icon: Disc, size: 95, top: '92%', left: '30%', duration: '23s', delay: '-2s' },
    { Icon: Mouse, size: 55, top: '70%', left: '88%', duration: '14s', delay: '-13s' },
    { Icon: Monitor, size: 85, top: '90%', left: '8%', duration: '21s', delay: '-18s' },
    { Icon: Sword, size: 70, top: '77%', left: '68%', duration: '16s', delay: '-5s' },
    { Icon: Gamepad2, size: 65, top: '88%', left: '95%', duration: '19s', delay: '-10s' },
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