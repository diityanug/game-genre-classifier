import React from 'react';
import { Trophy, Sparkles } from 'lucide-react';

const HighlightedDescription = ({ text, keywords }) => {
  if (!keywords || !text) return null;
  const regexPattern = new RegExp(`\\b(${keywords.join('|')})[a-z]*\\b`, 'gi');
  const parts = text.split(regexPattern);

  return (
    <div className="mt-5 pt-5 border-t border-[#1F2937]">
      <div className="flex flex-wrap gap-2 mb-3">
        <span className="text-xs font-bold text-[#00D8FF] flex items-center mr-2">
          <Sparkles className="w-3.5 h-3.5 mr-1" /> Key Keywords:
        </span>
        {keywords.map((kw, i) => (
          <span key={i} className="text-xs px-3 py-1 rounded-full bg-[#00D8FF]/10 border border-[#00D8FF]/30 text-[#00D8FF] font-medium">
            {kw}
          </span>
        ))}
      </div>
      <p className="text-sm leading-relaxed border-l-2 pl-3 border-[#1F2937] text-slate-300 italic">
        "{parts.map((part, i) => {
          const isMatch = keywords.some(k => part.toLowerCase().startsWith(k.toLowerCase()));
          return isMatch ? (
            <mark key={i} className="px-1 mx-0.5 rounded text-[#00D8FF] bg-[#00D8FF]/10 font-bold">
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
    <div className="mt-8 space-y-3 relative z-10">
      {predictions.map((pred, index) => {
        const isTopResult = index === 0;
        return (
          <div key={index} className={`flex flex-col p-5 rounded-2xl border transition-colors ${isTopResult ? 'bg-[#131826] border-[#00D8FF]/30' : 'bg-[#131826]/60 border-[#1F2937]'}`}>
            <div className="flex items-center w-full">
              {isTopResult && <Trophy className="w-5 h-5 text-[#00D8FF] mr-3" />}
              <span className={`w-32 truncate font-bold ${isTopResult ? 'text-white text-lg' : 'text-slate-300 text-sm'}`}>
                {pred.genre}
              </span>
              
              <div className="flex-1 mx-4 h-2 rounded-full bg-[#0B101A] overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ${isTopResult ? 'bg-[#00D8FF]' : 'bg-slate-600'}`}
                  style={{ width: `${pred.probability}%` }}
                ></div>
              </div>
              
              <span className={`w-16 text-right font-bold ${isTopResult ? 'text-[#00D8FF] text-xl' : 'text-slate-400 text-sm'}`}>
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