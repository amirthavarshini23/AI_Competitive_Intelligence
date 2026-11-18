import { useState, useEffect } from 'react';
import {
  Search,
  Sparkles,
  ExternalLink,
  BookOpen,
  HelpCircle,
  Loader2,
  Building2,
  Layers,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { searchSemantic, getAvailableCompetitors } from '../api/client';

const SAMPLE_QUESTIONS = [
  "What are the company's core AI and cloud capabilities?",
  "What major products and solutions are currently highlighted?",
  "What hiring, expansion, or technology trends are detectable?",
  "What enterprise security or compliance offerings are mentioned?",
];

export default function SemanticSearch() {
  const [competitors, setCompetitors] = useState([]);
  const [selectedCompId, setSelectedCompId] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getAvailableCompetitors()
      .then(setCompetitors)
      .catch(() => {});
  }, []);

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await searchSemantic(searchQuery.trim(), selectedCompId || null);
      setResult(res);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Search failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl lg:text-2xl font-bold text-slate-900 tracking-tight">
          RAG-Based Semantic Knowledge Search
        </h1>
        <p className="text-xs lg:text-sm text-slate-500 mt-1">
          Query indexed competitor website passages using vector similarity and evidence-grounded
          RAG question answering.
        </p>
      </div>

      {/* Search Input Bar */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="sm:w-56 shrink-0">
            <select
              value={selectedCompId}
              onChange={(e) => setSelectedCompId(e.target.value)}
              className="w-full py-2.5 px-3 rounded-lg border border-slate-300 text-xs bg-white text-slate-800 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 outline-none"
            >
              <option value="">Search All Competitors</option>
              {competitors.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Ask an intelligence question (e.g. 'What products are emphasized?')..."
              className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 text-xs text-slate-800 placeholder:text-slate-400 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 outline-none"
            />
          </div>

          <button
            onClick={() => handleSearch()}
            disabled={loading || !query.trim()}
            className="inline-flex items-center justify-center gap-2 bg-blue-900 hover:bg-blue-800 text-white px-5 py-2.5 rounded-lg text-xs font-semibold shadow-xs disabled:opacity-50 transition-all"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Ask RAG
          </button>
        </div>

        {/* Sample queries */}
        <div className="flex items-center gap-2 flex-wrap pt-1 border-t border-slate-100">
          <span className="text-[11px] font-semibold text-slate-400">Try asking:</span>
          {SAMPLE_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(q);
                handleSearch(q);
              }}
              className="text-[11px] bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200 px-2.5 py-1 rounded-md transition-colors text-left truncate max-w-xs"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3.5 bg-red-50 border border-red-200 rounded-lg text-xs text-red-800">
          {error}
        </div>
      )}

      {/* RAG Answer Output */}
      {result && (
        <div className="space-y-6">
          {/* Answer Card */}
          <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="inline-flex items-center gap-2 text-xs font-bold text-blue-900 uppercase tracking-wider">
                <Sparkles className="w-4 h-4 text-blue-600" />
                Synthesized Answer ({result.engine})
              </div>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
                Confidence: {result.confidence}
              </span>
            </div>

            <div className="prose prose-xs max-w-none text-slate-800 leading-relaxed">
              <ReactMarkdown>{result.answer}</ReactMarkdown>
            </div>
          </div>

          {/* Retrieved Evidence Passages */}
          <div className="space-y-3">
            <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Retrieved Grounding Passages ({result.sources?.length || 0} chunks)
            </h2>

            {result.sources?.map((source, idx) => (
              <div
                key={idx}
                className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-xs space-y-1.5"
              >
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-blue-900">[{idx + 1}]</span>
                    <span className="font-semibold text-slate-800">{source.company_name}</span>
                    <span className="text-slate-400">•</span>
                    <a
                      href={source.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline inline-flex items-center gap-1 text-[11px]"
                    >
                      {source.source_url} <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                  <span className="text-[10px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    Sim: {source.similarity_score}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed italic bg-slate-50/70 p-3 rounded border border-slate-100">
                  "{source.chunk_text}"
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
