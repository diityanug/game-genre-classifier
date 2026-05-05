import React, { useState, useEffect } from 'react';
import { Gamepad2, FileText, Loader2, AlertCircle, X } from 'lucide-react';
import { usePredict } from '../hooks/usePredict';
import { PredictionResult } from './PredictionResult';

const examples = [
  {
    title: "Star Wars Jedi: Fallen Order",
    desc: "A story-driven action-adventure where a surviving Jedi explores planets, fights enemies with lightsaber combat, and uses Force abilities to restore hope."
  },
  {
    title: "Grand Theft Auto V",
    desc: "An open-world action game where players control multiple characters to complete missions, heists, and explore a dynamic modern city"
  },
  {
    title: "Cyberpunk 2077",
    desc: "A futuristic open-world RPG set in a dystopian city where players customize their character and navigate story-driven missions involving technology and power."
  }
];

const GenreClassifier = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  
  const [titlePlaceholder, setTitlePlaceholder] = useState('');
  const [descPlaceholder, setDescPlaceholder] = useState('');
  const [isInteracting, setIsInteracting] = useState(false);
  const [exampleIdx, setExampleIdx] = useState(0);
  const [charIdx, setCharIdx] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  const { predictions, errorMsg, isLoading, predictGenre, setPredictions, setErrorMsg } = usePredict();

  useEffect(() => {
    if (isInteracting) {
      setTitlePlaceholder('Enter game title...');
      setDescPlaceholder('Describe the game mechanics, story, and gameplay...');
      return;
    }

    const currentExample = examples[exampleIdx];
    const fullTitle = currentExample.title;
    const fullDesc = currentExample.desc;
    const maxLen = Math.max(fullTitle.length, fullDesc.length);

    const typeSpeed = isDeleting ? 20 : 40;
    const delay = isDeleting && charIdx === 0 ? 500 : (!isDeleting && charIdx === maxLen ? 2000 : typeSpeed);

    const timer = setTimeout(() => {
      if (!isDeleting) {
        if (charIdx < maxLen) {
          setTitlePlaceholder(fullTitle.substring(0, charIdx + 1));
          setDescPlaceholder(fullDesc.substring(0, charIdx + 1));
          setCharIdx(prev => prev + 1);
        } else {
          setIsDeleting(true);
        }
      } else {
        if (charIdx > 0) {
          setTitlePlaceholder(fullTitle.substring(0, charIdx - 1));
          setDescPlaceholder(fullDesc.substring(0, charIdx - 1));
          setCharIdx(prev => prev - 1);
        } else {
          setIsDeleting(false);
          setExampleIdx((prev) => (prev + 1) % examples.length);
        }
      }
    }, delay);

    return () => clearTimeout(timer);
  }, [charIdx, isDeleting, exampleIdx, isInteracting]);

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
      setCharIdx(0);
      setIsDeleting(false);
    }
  };

  return (
    <div className="font-sans text-slate-900">
      
      {/* Header */}
      <div className="w-full px-8 py-5 flex items-center gap-4 border-b border-slate-200 bg-[#FDFBF7] relative z-10">
        <div className="bg-slate-900 p-2.5 rounded-xl">
          <Gamepad2 className="w-7 h-7 text-white" strokeWidth={2} />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-wide">Genre Game Classifier</h1>
          <p className="text-slate-500 text-xs mt-0.5">Game genre classification system based on text using Naive Bayes.</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-10 relative z-10">
        <div className="p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            
            <div className="space-y-3">
              <label className="flex items-center gap-2 text-base md:text-lg font-bold text-slate-900 tracking-wide">
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
                  className="w-full px-5 py-4 text-base md:text-lg rounded-xl border border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900 transition-all shadow-sm"
                />
                {title && <X onClick={() => handleClear(setTitle)} className="absolute right-4 top-4 h-6 w-6 cursor-pointer text-slate-400 hover:text-slate-900" />}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-end">
                <label className="flex items-center gap-2 text-base md:text-lg font-bold text-slate-900 tracking-wide">
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
                  className="w-full px-5 py-4 text-base md:text-lg rounded-xl border border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900 transition-all resize-none h-40 leading-relaxed shadow-sm"
                />
                {description && <X onClick={() => handleClear(setDescription)} className="absolute right-4 top-4 h-6 w-6 cursor-pointer text-slate-400 hover:text-slate-900" />}
              </div>
            </div>

            {errorMsg && (
              <div className="flex items-start gap-3 p-4 rounded-xl border border-red-200 bg-red-50">
                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 shrink-0" />
                <p className="text-sm text-red-700 font-medium">{errorMsg}</p>
              </div>
            )}

            <div className="flex justify-center pt-2">
              <button 
                type="submit" disabled={isLoading} 
                className="px-14 py-4 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 disabled:text-slate-500 text-white font-bold text-lg transition-all flex items-center justify-center gap-3 shadow-md hover:shadow-lg"
              >
                {isLoading ? <><Loader2 className="w-6 h-6 animate-spin" /> Processing...</> : 'Analyze Genre'}
              </button>
            </div>
          </form>
        </div>

        <PredictionResult predictions={predictions} />
      </div>
    </div>
  );
};

export default GenreClassifier;