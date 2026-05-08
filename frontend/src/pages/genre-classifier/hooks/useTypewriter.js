import { useState, useEffect } from 'react';

export const useTypewriter = (examples, isInteracting) => {
  const [titlePlaceholder, setTitlePlaceholder] = useState('');
  const [descPlaceholder, setDescPlaceholder] = useState('');
  const [exampleIdx, setExampleIdx] = useState(0);
  const [charIdx, setCharIdx] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

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
  }, [charIdx, isDeleting, exampleIdx, isInteracting, examples]);

  const resetTypewriter = () => {
    setCharIdx(0);
    setIsDeleting(false);
  };

  return { titlePlaceholder, descPlaceholder, resetTypewriter };
};