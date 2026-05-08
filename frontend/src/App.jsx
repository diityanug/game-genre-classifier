import React, { useState, useEffect } from 'react';
import '../style/global.css';
import GenreClassifier from './pages/genre-classifier/components/GenreClassifier';
import FloatingBackground from './components/FloatingBackground';
import { Github, Linkedin, Gamepad2 } from 'lucide-react';

function App() {
  const [isOnline, setIsOnline] = useState(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/'); 
        setIsOnline(response.ok);
      } catch (error) {
        setIsOnline(false);
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative min-h-screen bg-[#FDFBF7] overflow-hidden flex flex-col">
      <FloatingBackground />

      {/* Header*/}
      <header className="w-full px-8 py-5 flex items-center justify-between border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-30">
        <div className="flex items-center gap-4">
          <div className="bg-slate-900 p-2.5 rounded-xl">
            <Gamepad2 className="w-7 h-7 text-white" strokeWidth={2} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-wide">Genre Game Classifier</h1>
            <p className="text-slate-500 text-xs mt-0.5">Game genre classification system based on text using Naive Bayes.</p>
          </div>
        </div>

        {/* Server Status */}
        <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-full border border-slate-100 bg-slate-50 shadow-inner">
          {isOnline === null ? (
            <>
              <div className="w-2 h-2 bg-slate-300 rounded-full animate-pulse" />
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Checking Node</span>
            </>
          ) : isOnline ? (
            <>
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
              <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider">System Ready</span>
            </>
          ) : (
            <>
              <div className="w-2 h-2 bg-red-500 rounded-full shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
              <span className="text-xs font-bold text-red-700 uppercase tracking-wider">Server Offline</span>
            </>
          )}
        </div>
      </header>
      
      <div className="relative z-10 flex-1">
        <GenreClassifier isOnline={isOnline} />
      </div>

      {/* Footer */}
      <footer className="w-full relative z-10 border-t border-slate-200 bg-white/50 backdrop-blur-sm">
        <div className="w-full px-8 py-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex flex-col md:flex-row items-center gap-2 md:gap-3 text-center md:text-left">
            <p className="text-slate-900 font-bold text-sm">
              Genre Game Classifier © 2024
            </p>
            <span className="hidden md:block text-slate-300">|</span>
            <p className="text-slate-500 text-sm font-medium">
              Aditya Nugraha Irwan
            </p>
          </div>

          <div className="flex gap-5">
            <a href="https://github.com/diityanug" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-slate-900 transition-colors">
              <Github className="w-6 h-6" strokeWidth={1.5} />
            </a>
            <a href="https://www.linkedin.com/in/diityanug" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-[#0A66C2] transition-colors">
              <Linkedin className="w-6 h-6" strokeWidth={1.5} />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;