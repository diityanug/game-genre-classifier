import React, { useState, useEffect } from 'react';
import '../style/global.css';
import GenreClassifier from './pages/genre-classifier/components/GenreClassifier';
import FloatingBackground from './components/FloatingBackground';

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

  return (
    <div className={`relative min-h-screen py-10 overflow-hidden transition-colors duration-500 ${isDark ? 'bg-[#0f172a]' : 'bg-[#FDFBF7]'}`}>
      
      <FloatingBackground isDark={isDark} />

      <div className="relative z-10 container mx-auto">
        <GenreClassifier isDark={isDark} setIsDark={setIsDark} />
      </div>
    </div>
  );
}

export default App;