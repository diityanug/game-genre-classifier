import React from 'react';
import { Trophy, Sparkles } from 'lucide-react';

const HighlightedDescription = ({ text, keywords }) => {
  if (!keywords || !text) return null;
  const regexPattern = new RegExp(`\\b(${keywords.join('|')})[a-z]*\\b`, 'gi');
  const parts = text.split(regexPattern);

  return (
    <div className="mt-5 pt-5 border-t border-slate-200">
      <div className="flex flex-wrap gap-2 mb-3">
        <span className="text-xs font-bold text-slate-900 flex items-center mr-2">
          <Sparkles className="w-3.5 h-3.5 mr-1 text-slate-700" /> Key Keywords:
        </span>
        {keywords.map((kw, i) => (
          <span key={i} className="text-xs px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-700 font-medium">
            {kw}
          </span>
        ))}
      </div>
      <p className="text-sm leading-relaxed border-l-2 pl-3 border-slate-300 text-slate-600 italic">
        "{parts.map((part, i) => {
          const isMatch = keywords.some(k => part.toLowerCase().startsWith(k.toLowerCase()));
          return isMatch ? (
            <mark key={i} className="px-1 mx-0.5 rounded text-slate-900 bg-slate-200 font-bold shadow-sm">
              {part}
            </mark>
          ) : part;
        })}"
      </p>
    </div>
  );
};

export const PredictionResult = ({ predictions }) => {
  if (!predictions) return null;

  return (
    <div className="mt-8 space-y-3 relative z-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {predictions.map((pred, index) => {
        const isTopResult = index === 0;
        return (
          <div key={index} className={`flex flex-col p-5 rounded-2xl border transition-colors ${isTopResult ? 'bg-white border-slate-300 shadow-sm' : 'bg-white/50 border-slate-200'}`}>
            <div className="flex items-center w-full">
              {isTopResult && <Trophy className="w-5 h-5 text-slate-900 mr-3" />}
              <span className={`w-32 truncate font-bold ${isTopResult ? 'text-slate-900 text-lg' : 'text-slate-500 text-sm'}`}>
                {pred.genre}
              </span>
              
              <div className="flex-1 mx-4 h-2.5 rounded-full bg-slate-100 overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ${isTopResult ? 'bg-slate-900' : 'bg-slate-300'}`}
                  style={{ width: `${pred.probability}%` }}
                ></div>
              </div>
              
              <span className={`w-16 text-right font-bold ${isTopResult ? 'text-slate-900 text-xl' : 'text-slate-400 text-sm'}`}>
                {pred.probability}%
              </span>
            </div>

            {isTopResult && pred.keywords && (
              <HighlightedDescription text={pred.originalText} keywords={pred.keywords} />
            )}
          </div>
        );
      })}
    </div>
  );
};