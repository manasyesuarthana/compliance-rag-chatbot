import React, { useState } from 'react';
import { BookOpen, Search, AlertCircle } from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Points to Nginx/Docker host, or localhost if running locally
      const res = await fetch('http://localhost:3000/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query })
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Failed to fetch response");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans text-gray-900">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8 border-b pb-4 flex items-center gap-2">
          <BookOpen className="text-blue-600" />
          <h1 className="text-2xl font-bold">Compliance Interpreter</h1>
        </header>

        <form onSubmit={handleSearch} className="mb-8 flex gap-2">
          <input 
            className="flex-1 p-3 border rounded shadow-sm"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="e.g., What are the penalties for GDPR violation?"
          />
          <button disabled={loading} className="bg-blue-600 text-white px-6 rounded font-semibold hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Analyzing...' : 'Ask'}
          </button>
        </form>

        {result && (
          <div className="grid gap-6 md:grid-cols-3">
            <div className="md:col-span-2 bg-white p-6 rounded shadow border">
              <h2 className="text-lg font-bold mb-4 text-blue-900">Analysis</h2>
              <p className="leading-relaxed whitespace-pre-wrap">{result.answer}</p>
            </div>
            
            <div className="md:col-span-1 space-y-4">
              <h3 className="text-sm font-bold uppercase text-gray-500 tracking-wider">Citations</h3>
              {result.citations.map((cite, idx) => (
                <div key={idx} className="bg-white p-3 rounded border border-l-4 border-l-blue-400 text-sm shadow-sm">
                  <div className="font-bold text-gray-700 mb-1">{cite.source}</div>
                  <div className="text-xs bg-gray-100 inline-block px-2 py-1 rounded mb-2">Page {cite.page}</div>
                  <p className="text-gray-500 italic text-xs line-clamp-3">"{cite.context}"</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}