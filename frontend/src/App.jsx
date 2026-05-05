import React from 'react';
import '../style/global.css';
import GenreClassifier from './pages/genre-classifier/components/GenreClassifier';
import FloatingBackground from './components/FloatingBackground';
import { Github, Linkedin } from 'lucide-react';

function App() {
  return (
    <div className="relative min-h-screen bg-[#FDFBF7] overflow-hidden flex flex-col">
      <FloatingBackground />
      
      <div className="relative z-10 flex-1">
        <GenreClassifier />
      </div>

      {/* Footer */}
      <footer className="w-full relative z-10 border-t border-slate-200">
        <div className="max-w-4xl mx-auto px-6 py-6 flex flex-col md:flex-row justify-between items-center gap-4">
          
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