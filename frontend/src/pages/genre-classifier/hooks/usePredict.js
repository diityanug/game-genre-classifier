import { useState } from 'react';

export const usePredict = () => {
  const [predictions, setPredictions] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const predictGenre = async (title, description) => {
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
      setErrorMsg("Server offline. Backend didn't respond.");
    } finally {
      setIsLoading(false);
    }
  };

  return { predictions, errorMsg, isLoading, predictGenre, setPredictions, setErrorMsg };
};