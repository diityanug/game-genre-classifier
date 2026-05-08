import React, { useState } from 'react';
import { Gamepad2, FileText, Loader2, AlertCircle, X } from 'lucide-react';
import { usePredict } from '../hooks/usePredict';
import { useTypewriter } from '../hooks/useTypewriter';
import { PredictionResult } from './PredictionResult';
import { GAME_EXAMPLES } from '../utils/constants';

const GenreClassifier = ({ isOnline }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isInteracting, setIsInteracting] = useState(false);
  
  const { predictions, errorMsg, isLoading, predictGenre, setPredictions, setErrorMsg } = usePredict();
  const { titlePlaceholder, descPlaceholder, resetTypewriter } = useTypewriter(GAME_EXAMPLES, isInteracting);

  const handleSubmit = (e) => {
    e.preventDefault();
    predictGenre(title, description);
  };

  const handleClear = (setter) => {
    setter('');
    setPredictions(null);
    setErrorMsg(null);
  };

  const handleFocus = () => setIsInteracting(true);
  
  const handleBlur = () => {
    if (!title && !description) {
      setIsInteracting(false);
      resetTypewriter();
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-12 relative z-10">
      <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.05)] overflow-hidden">
        <div className="p-8 md:p-12">

          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="group space-y-3">
              <label className="flex items-center gap-2 text-base md:text-lg font-bold text-slate-900 tracking-wide group-focus-within:text-slate-600 transition-colors">
                <Gamepad2 className="w-5 h-5 text-slate-700" />
                Game Title
              </label>
              <div className="relative">
                <input 
                  type="text" 
                  required 
                  placeholder={titlePlaceholder} 
                  value={title} 
                  onChange={(e) => setTitle(e.target.value)}
                  onFocus={handleFocus}
                  onBlur={handleBlur}
                  className="w-full px-6 py-5 text-lg font-semibold rounded-xl border-2 border-slate-100 bg-slate-50/50 text-slate-900 placeholder-slate-300 focus:outline-none focus:border-slate-900 focus:bg-white transition-all shadow-inner focus:shadow-none"
                />
                {title && <X onClick={() => handleClear(setTitle)} className="absolute right-5 top-1/2 -translate-y-1/2 h-6 w-6 cursor-pointer text-slate-400 hover:text-slate-900" />}
              </div>
            </div>

            <div className="group space-y-3">
              <div className="flex justify-between items-end">
                <label className="flex items-center gap-2 text-base md:text-lg font-bold text-slate-900 tracking-wide group-focus-within:text-slate-600 transition-colors">
                  <FileText className="w-5 h-5 text-slate-700" />
                  Game Description
                </label>
              </div>
              <div className="relative">
                <textarea 
                  required 
                  placeholder={descPlaceholder} 
                  value={description} 
                  onChange={(e) => setDescription(e.target.value)}
                  onFocus={handleFocus}
                  onBlur={handleBlur}
                  className="w-full px-6 py-5 text-lg rounded-xl border-2 border-slate-100 bg-slate-50/50 text-slate-900 placeholder-slate-300 focus:outline-none focus:border-slate-900 focus:bg-white transition-all resize-none h-48 leading-relaxed shadow-inner focus:shadow-none"
                />
                {description && <X onClick={() => handleClear(setDescription)} className="absolute right-5 top-6 h-6 w-6 cursor-pointer text-slate-400 hover:text-slate-900" />}
              </div>
            </div>

            {errorMsg && (
              <div className="flex items-center gap-3 p-4 rounded-xl border border-red-200 bg-red-50 animate-in shake duration-500">
                <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
                <p className="text-sm text-red-700 font-semibold">{errorMsg}</p>
              </div>
            )}

            <div className="flex justify-center md:justify-start pt-4">
              <button 
                type="submit" 
                disabled={isLoading || isOnline === false} 
                className="px-12 py-5 rounded-2xl bg-slate-900 hover:bg-black disabled:bg-slate-200 disabled:text-slate-500 disabled:cursor-not-allowed text-white font-bold text-lg transition-all flex items-center justify-center gap-3 shadow-[0_15px_30px_-5px_rgba(0,0,0,0.2)] hover:shadow-[0_20px_40px_-5px_rgba(0,0,0,0.3)] active:scale-95 overflow-hidden"
              >
                {isLoading ? (
                  <><Loader2 className="w-6 h-6 animate-spin" /> Processing...</>
                ) : isOnline === false ? (
                  'System Offline'
                ) : (
                  'Analyze Genre'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      <PredictionResult predictions={predictions} />
    </div>
  );
};

export default GenreClassifier;