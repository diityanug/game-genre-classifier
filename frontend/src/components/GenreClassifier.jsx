import React, { useState, useEffect } from 'react';
import { Gamepad2, FileText, Trophy, Loader2, AlertCircle, Sun, Moon, X } from 'lucide-react';

const HighlightedDescription = ({ text, keywords, isDark }) => {
  if (!keywords || keywords.length === 0 || !text) return <p className="text-sm italic mt-2 opacity-80">"{text}"</p>;

  const regexPattern = new RegExp(`\\b(${keywords.join('|')})[a-z]*\\b`, 'gi');
  const parts = text.split(regexPattern);

  return (
    <p className="text-sm mt-3 leading-relaxed border-l-2 pl-3 border-slate-500 opacity-90 italic">
      "
      {parts.map((part, i) => {
        const isMatch = keywords.some(k => part.toLowerCase().startsWith(k.toLowerCase()));
        if (isMatch) {
          return (
            <mark 
              key={i} 
              className={`px-1 mx-0.5 rounded-sm font-bold bg-transparent ${isDark ? 'text-red-400 bg-red-900/40' : 'text-slate-900 bg-slate-300/60'}`}
            >
              {part}
            </mark>
          );
        }
        return part;
      })}
      "
    </p>
  );
};

const GenreClassifier = ({ isDark, setIsDark }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [predictions, setPredictions] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    document.body.style.backgroundColor = isDark ? '#0f172a' : '#FDFBF7'; 
    document.body.style.transition = 'background-color 0.3s ease';
  }, [isDark]);

  const handlePredict = async (e) => {
    e.preventDefault(); 

    setIsLoading(true);
    setPredictions(null);
    setErrorMsg(null);

    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description })
      });

      if (!response.ok) throw new Error("Connection failed.");

      const result = await response.json();
      
      if (result.status === 'error') {
        setErrorMsg(result.message);
      } else {
        setPredictions(result.data);
      }
    } catch (error) {
      console.error("Error:", error);
      setErrorMsg("Server offline. Backend didn't response.");
    } finally {
      setIsLoading(false);
    }
  };

  const theme = {
    card: isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-[#EAE6DF]',
    textMain: isDark ? 'text-white' : 'text-slate-900',
    textMuted: isDark ? 'text-slate-400' : 'text-stone-500',
    label: isDark ? 'text-slate-300' : 'text-slate-800',
    inputBg: isDark 
      ? 'bg-slate-950 border-slate-800 text-white focus:border-red-600 focus:ring-1 focus:ring-red-600 placeholder-slate-600' 
      : 'bg-[#FDFBF7] border-[#EAE6DF] text-slate-900 focus:border-slate-900 focus:ring-1 focus:ring-slate-900 placeholder-stone-400',
    iconPrimary: isDark ? 'text-red-500' : 'text-slate-900',
    button: isDark 
      ? 'bg-red-700 hover:bg-red-800 text-white border border-red-700' 
      : 'bg-slate-900 hover:bg-slate-800 text-white border border-slate-900',
    resultCard: isDark ? 'bg-slate-800/50 hover:bg-slate-800' : 'bg-white hover:bg-stone-50 border border-transparent',
    resultTopCard: isDark ? 'bg-slate-800 border-red-500/30' : 'bg-[#F4F1EB] border-[#D8D3C8]',
    progressBg: isDark ? 'bg-slate-950' : 'bg-[#EAE6DF]',
    progressFill: isDark ? 'bg-red-600' : 'bg-slate-900',
  };

  return (
    <>
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Exo:ital,wght@0,100..900;1,100..900&display=swap');
        `}
      </style>

      <div 
        className={`max-w-2xl mx-auto p-6 md:p-10 rounded-none md:rounded-xl border my-6 md:mt-10 mx-4 md:mx-auto transition-colors duration-300 shadow-sm ${theme.card}`}
        style={{ fontFamily: "'Exo', sans-serif" }}
      >
        
        <div className="flex justify-between items-start mb-10">
          <div className="flex-1">
            <h1 className={`text-3xl md:text-4xl font-bold tracking-tight mb-2 transition-colors duration-300 ${theme.textMain}`}>
              Genre Game Classifier
            </h1>
            <p className={`text-sm md:text-base font-medium transition-colors duration-300 ${theme.textMuted}`}>
              Game genre classification system based on text using Naive Bayes.
            </p>
          </div>
          
          <button 
            type="button" 
            onClick={() => setIsDark(!isDark)}
            className={`p-3 rounded-md transition-all duration-300 focus:outline-none ${isDark ? 'bg-slate-800 text-red-400 hover:bg-slate-700' : 'bg-[#F4F1EB] text-slate-900 hover:bg-[#EAE6DF]'}`}
            title="Toggle Theme"
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>

        <form onSubmit={handlePredict} className="space-y-6">
          
          <div className="relative group">
            <label className={`block font-semibold mb-2 uppercase tracking-widest text-xs transition-colors duration-300 ${theme.label}`}>
              Game Title <span className="text-red-500">*</span>
            </label>
            
            <div className="relative flex items-center">
              <div className="absolute left-0 pl-4 pointer-events-none">
                <Gamepad2 className={`h-5 w-5 transition-colors duration-300 ${theme.iconPrimary}`} />
              </div>
              <input 
                type="text" 
                required 
                className={`w-full pl-12 pr-10 py-3.5 text-sm md:text-base rounded-md transition-all outline-none font-medium ${theme.inputBg}`}
                placeholder="Insert title..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              {title && (
                <button type="button" onClick={() => setTitle('')} className="absolute right-4 text-stone-400 hover:text-red-500 transition-colors">
                  <X className="h-5 w-5" />
                </button>
              )}
            </div>
          </div>

          <div className="relative group">
            <div className="flex justify-between items-end mb-2">
              <label className={`block font-semibold uppercase tracking-widest text-xs transition-colors duration-300 ${theme.label}`}>
                Description / Synopsis <span className="text-red-500">*</span>
              </label>
              
              <span className={`text-xs font-semibold ${description.length > 0 ? theme.iconPrimary : theme.textMuted}`}>
                {description.length} chr
              </span>
            </div>
            <div className="relative">
              <div className="absolute top-4 left-4 pointer-events-none">
                <FileText className={`h-5 w-5 transition-colors duration-300 ${theme.iconPrimary}`} />
              </div>
              <textarea 
                required 
                className={`w-full pl-12 pr-10 py-3.5 text-sm md:text-base rounded-md h-32 md:h-40 transition-all outline-none resize-none font-medium ${theme.inputBg}`}
                placeholder="Insert game description..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
              {description && (
                <button type="button" onClick={() => setDescription('')} className="absolute top-4 right-4 text-stone-400 hover:text-red-500 transition-colors">
                  <X className="h-5 w-5" />
                </button>
              )}
            </div>
          </div>

          {errorMsg && (
            <div className="flex items-start gap-3 p-4 bg-red-50 text-red-700 border border-red-200 rounded-md">
              <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
              <p className="text-sm font-semibold tracking-wide">{errorMsg}</p>
            </div>
          )}

          <button 
            type="submit" 
            disabled={isLoading}
            className={`w-full py-4 rounded-md font-bold text-base tracking-widest uppercase transition-all flex items-center justify-center gap-3
              ${isLoading 
                ? 'bg-stone-300 text-stone-500 cursor-not-allowed border-transparent' 
                : theme.button
              }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                Genre Analysis
              </>
            )}
          </button>
        </form>

        {predictions && !errorMsg && (
          <div className={`mt-10 pt-8 border-t transition-colors duration-300 ${isDark ? 'border-slate-800' : 'border-[#EAE6DF]'}`}>
            <div className="flex items-center gap-3 mb-6">
              <Trophy className={`h-6 w-6 ${theme.iconPrimary}`} />
              <h2 className={`text-xl font-bold uppercase tracking-widest transition-colors duration-300 ${theme.textMain}`}>
                Prediction Result
              </h2>
            </div>
            
            <div className="space-y-3">
              {predictions.map((pred, index) => {
                const isTopResult = index === 0;
                return (
                  <div key={index} className={`flex flex-col p-3 md:p-4 rounded-md transition-colors border ${isTopResult ? theme.resultTopCard : `${theme.resultCard}`}`}>
                    
                    <div className="flex items-center w-full">
                      <span className={`w-24 md:w-32 truncate font-bold tracking-wider uppercase ${isTopResult ? `${theme.label} text-base` : `${theme.textMuted} text-sm`}`}>
                        {pred.genre}
                      </span>
                      
                      <div className={`flex-1 mx-3 md:mx-5 h-2 rounded-sm overflow-hidden ${theme.progressBg}`}>
                        <div 
                          className={`h-full transition-all duration-700 ease-out ${isTopResult ? theme.progressFill : (isDark ? 'bg-slate-600' : 'bg-stone-300')}`}
                          style={{ width: `${pred.probability}%` }}
                        ></div>
                      </div>
                      
                      <span className={`w-16 text-right font-semibold ${isTopResult ? `${theme.label} text-base` : `${theme.textMuted} text-sm`}`}>
                        {pred.probability}%
                      </span>
                    </div>

                    {isTopResult && pred.keywords && pred.keywords.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-slate-500/20">
                        <p className={`text-xs font-bold uppercase tracking-widest mb-1 ${theme.iconPrimary}`}>
                          Decision Factors
                        </p>
                        <HighlightedDescription 
                          text={description} 
                          keywords={pred.keywords} 
                          isDark={isDark} 
                        />
                      </div>
                    )}

                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default GenreClassifier;