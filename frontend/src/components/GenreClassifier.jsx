import React, { useState } from 'react';

const GenreClassifier = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [predictions, setPredictions] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handlePredict = async () => {
    if (!title || !description) {
      alert("Judul dan Deskripsi tidak boleh kosong!");
      return;
    }

    setIsLoading(true);
    setPredictions(null);

    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description })
      });

      if (!response.ok) throw new Error("Gagal mengambil data dari server");

      const data = await response.json();
      setPredictions(data);
    } catch (error) {
      console.error("Error:", error);
      alert("Server Backend (FastAPI) belum menyala atau terjadi error.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-lg mt-10">
      <h1 className="text-3xl font-bold text-center text-indigo-600 mb-2">Game Genre AI Classifier</h1>
      <p className="text-center text-gray-500 mb-8">Tebak genre game berdasarkan judul dan deskripsi</p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Judul Game</label>
          <input 
            type="text" 
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            placeholder="Contoh: Cosmic Hoops"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Deskripsi Game</label>
          <textarea 
            className="w-full px-4 py-2 border border-gray-300 rounded-lg h-32 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            placeholder="Masukkan sinopsis atau deskripsi gameplay..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <button 
          onClick={handlePredict}
          disabled={isLoading}
          className={`w-full py-3 rounded-lg font-semibold transition-colors text-white 
            ${isLoading ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'}`}
        >
          {isLoading ? 'Sedang Menganalisa...' : 'Analisa Genre AI ✨'}
        </button>
      </div>

      {predictions && (
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Hasil Analisis:</h2>
          <div className="space-y-4">
            {predictions.map((pred, index) => (
              <div key={index} className="flex items-center">
                <span className="w-24 font-medium text-gray-700">{pred.genre}</span>
                <div className="flex-1 ml-4 bg-gray-200 rounded-full h-4 overflow-hidden">
                  <div 
                    className="bg-indigo-500 h-4 rounded-full transition-all duration-1000 ease-out"
                    style={{ width: `${pred.probability}%` }}
                  ></div>
                </div>
                <span className="w-16 text-right text-sm font-semibold text-indigo-600">
                  {pred.probability}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GenreClassifier;