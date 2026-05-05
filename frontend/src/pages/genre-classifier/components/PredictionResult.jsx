import React from 'react';
import { Trophy } from 'lucide-react';

const HighlightedDescription = ({ text, keywords, isDark }) => {
  if (!keywords || !text) return null;
  const regexPattern = new RegExp(`\\b(${keywords.join('|')})[a-z]*\\b`, 'gi');
  const parts = text.split(regexPattern);

  return (
    <div className={`mt-5 pt-5 border-t border-dashed transition-colors duration-300 ${isDark ? 'border-cyan-500/30' : 'border-blue-300/50'}`}>
      <div className="flex flex-wrap gap-2 mb-4">
        <span className={`text-[10px] font-bold uppercase tracking-[0.2em] flex items-center mr-2 ${isDark ? 'text-cyan-400' : 'text-blue-700'}`}>
          Trigger Nodes:
        </span>
        {keywords.map((kw, i) => (
          <span key={i} className={`text-xs px-3 py-1 rounded-md font-bold uppercase tracking-wider backdrop-blur-sm transition-all ${isDark ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-500/50 shadow-[0_0_10px_rgba(34,211,238,0.2)]' : 'bg-blue-100/80 text-blue-800 border border-blue-300 shadow-sm'}`}>
            {kw}
          </span>
        ))}
      </div>
      <p className={`text-sm leading-relaxed border-l-4 pl-4 py-1 italic font-medium ${isDark ? 'border-cyan-500/50 text-cyan-100/80' : 'border-blue-500/50 text-slate-700'}`}>
        "{parts.map((part, i) => {
          const isMatch = keywords.some(k => part.toLowerCase().startsWith(k.toLowerCase()));
          return isMatch ? (
            <mark key={i} className={`px-1.5 mx-0.5 rounded text-transparent bg-clip-text font-black transition-all ${isDark ? 'bg-gradient-to-r from-cyan-400 to-blue-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.6)]' : 'bg-gradient-to-r from-blue-600 to-indigo-600'}`}>
              {part}
            </mark>
          ) : part;
        })}"
      </p>
    </div>
  );
};

export const PredictionResult = ({ predictions, isDark, theme }) => {
  if (!predictions) return null;

  return (
    <div className={`mt-10 pt-8 border-t transition-colors duration-500 relative z-10 ${isDark ? 'border-cyan-500/20' : 'border-blue-200/50'}`}>
      <div className="flex items-center gap-3 mb-6">
        <Trophy className={`h-6 w-6 ${theme.iconPrimary}`} />
        <h2 className={`text-lg font-black uppercase tracking-[0.2em] ${theme.textMain}`}>
          System Output
        </h2>
      </div>
      
      <div className="space-y-3 relative">
        {isDark && <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-cyan-500/0 via-cyan-500/20 to-cyan-500/0 -z-10 hidden md:block"></div>}

        {predictions.map((pred, index) => {
          const isTopResult = index === 0;
          return (
            <div key={index} className={`flex flex-col p-4 rounded-xl transition-all duration-300 border backdrop-blur-sm ${isTopResult ? theme.resultTopCard : theme.resultCard}`}>
              <div className="flex items-center w-full">
                <span className={`w-28 md:w-32 truncate font-bold tracking-[0.15em] uppercase ${isTopResult ? `${theme.label} text-sm md:text-base` : `${theme.textMuted} text-xs md:text-sm`}`}>
                  {pred.genre}
                </span>
                
                <div className={`flex-1 mx-3 md:mx-5 h-1.5 md:h-2 rounded-full overflow-hidden ${theme.progressBg}`}>
                  <div 
                    className={`h-full rounded-full transition-all duration-1000 ease-out ${isTopResult ? theme.progressFill : (isDark ? 'bg-slate-700' : 'bg-blue-200')}`}
                    style={{ width: `${pred.probability}%` }}
                  ></div>
                </div>
                
                <span className={`w-16 text-right font-black ${isTopResult ? `${theme.label} text-sm md:text-base drop-shadow-md` : `${theme.textMuted} text-xs md:text-sm`}`}>
                  {pred.probability}%
                </span>
              </div>

              {isTopResult && pred.keywords && (
                <HighlightedDescription text={pred.originalText} keywords={pred.keywords} isDark={isDark} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};