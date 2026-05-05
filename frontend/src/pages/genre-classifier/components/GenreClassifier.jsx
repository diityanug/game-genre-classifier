import React, { useState, useEffect } from 'react';
import { Gamepad2, FileText, Loader2, AlertCircle, Sun, Moon, X } from 'lucide-react';
import { usePredict } from '../hooks/usePredict';
import { PredictionResult } from './PredictionResult';

const GenreClassifier = ({ isDark, setIsDark }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  
  const { predictions, errorMsg, isLoading, predictGenre, setPredictions, setErrorMsg } = usePredict();

  useEffect(() => {
    document.body.style.backgroundColor = isDark ? '#0f172a' : '#FDFBF7'; 
    document.body.style.transition = 'background-color 0.3s ease';
  }, [isDark]);

  const handleSubmit = (e) => {
    e.preventDefault();
    predictGenre(title, description);
  };

  const handleClear = (setter) => {
    setter('');
    setPredictions(null);
    setErrorMsg(null);
  };

  const theme = {
    card: isDark 
      ? 'bg-slate-900/60 backdrop-blur-xl border-cyan-500/30 shadow-[0_0_40px_rgba(8,145,178,0.15)]' 
      : 'bg-white/60 backdrop-blur-xl border-blue-300/40 shadow-[0_0_40px_rgba(59,130,246,0.15)]',
    textMain: isDark ? 'text-cyan-50' : 'text-slate-900',
    textMuted: isDark ? 'text-cyan-200/60' : 'text-slate-500',
    label: isDark ? 'text-cyan-400' : 'text-blue-600',
    inputBg: isDark 
      ? 'bg-slate-950/50 border-cyan-500/30 text-cyan-100 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 focus:shadow-[0_0_15px_rgba(34,211,238,0.2)] placeholder-slate-600' 
      : 'bg-white/50 border-blue-200 text-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:shadow-[0_0_15px_rgba(59,130,246,0.3)] placeholder-slate-400',
    iconPrimary: isDark ? 'text-cyan-400 drop-shadow-[0_0_5px_rgba(34,211,238,0.5)]' : 'text-blue-600',
    button: isDark 
      ? 'bg-cyan-600 hover:bg-cyan-400 text-slate-950 border-cyan-400 shadow-[0_0_20px_rgba(8,145,178,0.4)] hover:shadow-[0_0_30px_rgba(34,211,238,0.7)]' 
      : 'bg-blue-600 hover:bg-blue-500 text-white border-blue-500 shadow-[0_0_20px_rgba(37,99,235,0.4)] hover:shadow-[0_0_30px_rgba(59,130,246,0.6)]',
    resultCard: isDark 
      ? 'bg-slate-900/40 border-cyan-900/40 hover:border-cyan-500/50 hover:shadow-[0_0_15px_rgba(8,145,178,0.2)]' 
      : 'bg-white/50 border-blue-100 hover:border-blue-300 hover:shadow-md',
    resultTopCard: isDark 
      ? 'bg-slate-800/80 border-cyan-400/60 shadow-[0_0_20px_rgba(34,211,238,0.2)]' 
      : 'bg-blue-50/80 border-blue-400/60 shadow-[0_0_20px_rgba(59,130,246,0.2)]',
    progressBg: isDark ? 'bg-slate-950/80 shadow-inner' : 'bg-slate-200 shadow-inner',
    progressFill: isDark 
      ? 'bg-cyan-400 shadow-[0_0_12px_rgba(34,211,238,0.9)]' 
      : 'bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.7)]',
  };

  return (
    <>
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Exo:ital,wght@0,100..900;1,100..900&display=swap');`}
      </style>

      <div 
        className={`relative max-w-2xl mx-auto p-6 md:p-10 rounded-2xl border my-10 transition-all duration-500 ${theme.card} ring-1 ${isDark ? 'ring-cyan-500/10' : 'ring-blue-500/5'}`} 
        style={{ fontFamily: "'Exo', sans-serif" }}
      >
        
        <div className="flex justify-between items-start mb-10 relative z-10">
          <div>
            <h1 className={`text-3xl md:text-4xl font-black tracking-tighter mb-2 ${theme.textMain}`}>
              Genre Game Classifier
            </h1>
            <p className={`text-sm md:text-base font-medium tracking-wide ${theme.textMuted}`}>
              Game genre classification system based on text using Naive Bayes.
            </p>
          </div>
          <button 
            onClick={() => setIsDark(!isDark)} 
            className={`p-3 rounded-xl transition-all duration-300 backdrop-blur-md border ${isDark ? 'bg-slate-900/50 border-cyan-500/30 text-cyan-400 hover:bg-cyan-900/30 hover:shadow-[0_0_15px_rgba(34,211,238,0.3)]' : 'bg-white/50 border-blue-200 text-blue-600 hover:bg-blue-50 hover:shadow-md'}`}
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-7 relative z-10">
          <div className="relative group">
            <label className={`block font-bold mb-2 uppercase tracking-[0.2em] text-xs ${theme.label}`}>
              Game Title <span className={theme.iconPrimary}>*</span>
            </label>
            <div className="relative flex items-center">
              <Gamepad2 className={`absolute left-4 h-5 w-5 ${theme.iconPrimary}`} />
              <input 
                type="text" required placeholder="Insert title..." value={title} onChange={(e) => setTitle(e.target.value)}
                className={`w-full pl-12 pr-10 py-4 rounded-xl outline-none font-semibold transition-all duration-300 ${theme.inputBg}`}
              />
              {title && <X onClick={() => handleClear(setTitle)} className={`absolute right-4 h-5 w-5 cursor-pointer transition-colors ${isDark ? 'text-slate-500 hover:text-cyan-400' : 'text-slate-400 hover:text-blue-600'}`} />}
            </div>
          </div>

          <div className="relative group">
            <div className="flex justify-between items-end mb-2">
              <label className={`block font-bold uppercase tracking-[0.2em] text-xs ${theme.label}`}>
                Description <span className={theme.iconPrimary}>*</span>
              </label>
              <span className={`text-xs font-bold tracking-wider ${description.length > 0 ? theme.iconPrimary : theme.textMuted}`}>
                {description.length} chr
              </span>
            </div>
            <div className="relative">
              <FileText className={`absolute top-4 left-4 h-5 w-5 ${theme.iconPrimary}`} />
              <textarea 
                required placeholder="Insert game description..." value={description} onChange={(e) => setDescription(e.target.value)}
                className={`w-full pl-12 pr-10 py-4 rounded-xl h-36 outline-none resize-none font-semibold transition-all duration-300 ${theme.inputBg}`}
              />
              {description && <X onClick={() => handleClear(setDescription)} className={`absolute top-4 right-4 h-5 w-5 cursor-pointer transition-colors ${isDark ? 'text-slate-500 hover:text-cyan-400' : 'text-slate-400 hover:text-blue-600'}`} />}
            </div>
          </div>

          {errorMsg && (
            <div className={`flex items-start gap-3 p-4 rounded-xl backdrop-blur-md border ${isDark ? 'bg-red-950/50 text-red-400 border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.2)]' : 'bg-red-50 text-red-700 border-red-200'}`}>
              <AlertCircle className="h-5 w-5 mt-0.5 shrink-0" />
              <p className="text-sm font-semibold tracking-wide">{errorMsg}</p>
            </div>
          )}

          <button 
            type="submit" disabled={isLoading} 
            className={`w-full py-4 rounded-xl font-bold text-sm md:text-base tracking-[0.2em] uppercase flex justify-center gap-3 transition-all duration-300 ${isLoading ? (isDark ? 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed' : 'bg-slate-200 text-slate-400 cursor-not-allowed') : theme.button}`}
          >
            {isLoading ? <><Loader2 className="h-5 w-5 animate-spin" /> Processing...</> : 'Genre Analysis'}
          </button>
        </form>

        <PredictionResult predictions={predictions} isDark={isDark} theme={theme} />

      </div>
    </>
  );
};

export default GenreClassifier;