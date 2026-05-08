import React from 'react';
import { Trophy, Sparkles, CheckCircle2, Activity } from 'lucide-react';

const HighlightedDescription = ({ text, keywords }) => {
  if (!keywords || !text) return null;
  const regexPattern = new RegExp(`\\b(${keywords.join('|')})[a-z]*\\b`, 'gi');
  const parts = text.split(regexPattern);

  return (
    <div className="mt-6 pt-6 border-t border-slate-100">
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="text-xs font-bold text-slate-900 flex items-center mr-2 uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5 mr-1.5 text-yellow-500" /> Matches Found:
        </span>
        {keywords.map((kw, i) => (
          <span key={i} className="text-[11px] px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-700 font-bold uppercase tracking-widest shadow-sm">
            {kw}
          </span>
        ))}
      </div>
      <p className="text-sm leading-relaxed border-l-4 pl-4 border-slate-200 text-slate-600 italic bg-slate-50/50 py-3 pr-3 rounded-r-xl">
        "{parts.map((part, i) => {
          const isMatch = keywords.some(k => part.toLowerCase().startsWith(k.toLowerCase()));
          return isMatch ? (
            <mark key={i} className="px-1 mx-0.5 rounded text-slate-900 bg-yellow-200/60 font-black shadow-sm">
              {part}
            </mark>
          ) : part;
        })}"
      </p>
    </div>
  );
};

export const PredictionResult = ({ predictions }) => {
  if (!predictions || predictions.length === 0) return null;

  return (
    <div className="mt-8 relative z-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
      
      {/* Bento Box Wrapper */}
      <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.05)] overflow-hidden">
        <div className="p-8 md:p-12">
          
          {/* Section Header */}
          <div className="flex items-center gap-3 mb-8 pb-4 border-b border-slate-100">
            <h2 className="text-xs font-black text-slate-400 uppercase tracking-[0.25em]">Classification Report</h2>
          </div>

          <div className="space-y-4">
            {predictions.map((pred, index) => {
              const isTopResult = index === 0;
              return (
                <div 
                  key={index} 
                  className={`group flex flex-col p-6 rounded-3xl border transition-all duration-300 ${
                    isTopResult 
                    ? 'bg-white border-slate-200 shadow-[0_10px_30px_-10px_rgba(0,0,0,0.1)]' 
                    : 'bg-slate-50/50 border-slate-100 hover:border-slate-300 hover:bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between w-full gap-4">
                    
                    {/* Icon & Title */}
                    <div className="flex items-center min-w-[140px]">
                      <div className={`p-2.5 rounded-xl mr-4 ${isTopResult ? 'bg-slate-900 text-white' : 'bg-slate-200 text-slate-500'}`}>
                        {isTopResult ? <Trophy className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
                      </div>
                      <span className={`truncate font-black tracking-wide ${isTopResult ? 'text-slate-900 text-2xl' : 'text-slate-600 text-lg'}`}>
                        {pred.genre}
                      </span>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="flex-1 max-w-md hidden sm:block">
                      <div className="h-2.5 w-full rounded-full bg-slate-100 overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-1000 ease-out ${isTopResult ? 'bg-slate-900' : 'bg-slate-300 group-hover:bg-slate-400'}`}
                          style={{ width: `${pred.probability}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    {/* Percentage */}
                    <div className="min-w-[80px] text-right">
                      <span className={`font-black tracking-tighter ${isTopResult ? 'text-slate-900 text-3xl' : 'text-slate-400 text-xl'}`}>
                        {pred.probability}<span className="text-sm ml-0.5">%</span>
                      </span>
                    </div>

                  </div>

                  {/* Highlights Content */}
                  {isTopResult && pred.keywords && (
                    <HighlightedDescription text={pred.originalText} keywords={pred.keywords} />
                  )}
                </div>
              );
            })}
          </div>

        </div>
      </div>
    </div>
  );
};