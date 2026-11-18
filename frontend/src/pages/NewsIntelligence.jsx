import { useEffect, useState } from 'react';
import {
  Newspaper,
  Search,
  ExternalLink,
  Filter,
  TrendingUp,
  Smile,
  Meh,
  Frown,
  Loader2,
  Calendar,
} from 'lucide-react';
import { getNewsArticles, getNewsStats, getAvailableCompetitors } from '../api/client';

export default function NewsIntelligence() {
  const [articles, setArticles] = useState([]);
  const [stats, setStats] = useState(null);
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [competitorFilter, setCompetitorFilter] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('');
  const [searchFilter, setSearchFilter] = useState('');

  useEffect(() => {
    Promise.all([
      getAvailableCompetitors(),
      getNewsStats(),
    ])
      .then(([comps, st]) => {
        setCompetitors(comps);
        setStats(st);
      })
      .catch(() => {});
    loadArticles();
  }, []);

  const loadArticles = (params = {}) => {
    setLoading(true);
    getNewsArticles(params)
      .then(setArticles)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const handleApplyFilter = () => {
    const params = {};
    if (competitorFilter) params.competitor_id = competitorFilter;
    if (sentimentFilter) params.sentiment = sentimentFilter;
    if (searchFilter) params.search = searchFilter;
    loadArticles(params);
  };

  const handleReset = () => {
    setCompetitorFilter('');
    setSentimentFilter('');
    setSearchFilter('');
    loadArticles({});
  };

  const sentDist = stats?.sentiment_distribution || { positive: 0, neutral: 0, negative: 0 };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl lg:text-2xl font-bold text-slate-900 tracking-tight">
          News Intelligence & Sentiment Analysis
        </h1>
        <p className="text-xs lg:text-sm text-slate-500 mt-1">
          Aggregates public RSS technology feeds (Google News, HackerNews, TechCrunch) with local
          NLTK VADER sentiment classification.
        </p>
      </div>

      {/* Top Sentiment Distribution Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-xs">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Total Articles
          </span>
          <p className="text-xl font-bold text-slate-900 mt-1">{stats?.total_articles || 0}</p>
        </div>
        <div className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-emerald-600 uppercase tracking-wider">
              Positive Sentiment
            </span>
            <Smile className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-xl font-bold text-emerald-700 mt-1">{sentDist.positive}</p>
        </div>
        <div className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              Neutral Sentiment
            </span>
            <Meh className="w-4 h-4 text-slate-500" />
          </div>
          <p className="text-xl font-bold text-slate-700 mt-1">{sentDist.neutral}</p>
        </div>
        <div className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-red-600 uppercase tracking-wider">
              Negative Sentiment
            </span>
            <Frown className="w-4 h-4 text-red-600" />
          </div>
          <p className="text-xl font-bold text-red-700 mt-1">{sentDist.negative}</p>
        </div>
      </div>

      {/* Filter Strip */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-xs flex flex-wrap items-center gap-3">
        {/* Competitor filter */}
        <select
          value={competitorFilter}
          onChange={(e) => setCompetitorFilter(e.target.value)}
          className="py-2 px-3 rounded-lg border border-slate-300 text-xs bg-white text-slate-800 focus:ring-2 focus:ring-blue-600 outline-none"
        >
          <option value="">All Competitors</option>
          {competitors.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>

        {/* Sentiment filter */}
        <select
          value={sentimentFilter}
          onChange={(e) => setSentimentFilter(e.target.value)}
          className="py-2 px-3 rounded-lg border border-slate-300 text-xs bg-white text-slate-800 focus:ring-2 focus:ring-blue-600 outline-none"
        >
          <option value="">All Sentiments</option>
          <option value="positive">Positive</option>
          <option value="neutral">Neutral</option>
          <option value="negative">Negative</option>
        </select>

        {/* Search input */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
          <input
            type="text"
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleApplyFilter()}
            placeholder="Search headline or keyword..."
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-xs text-slate-800 focus:ring-2 focus:ring-blue-600 outline-none"
          />
        </div>

        <button
          onClick={handleApplyFilter}
          className="bg-blue-900 hover:bg-blue-800 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow-xs transition-colors"
        >
          Apply Filters
        </button>
        <button
          onClick={handleReset}
          className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-lg text-xs font-semibold transition-colors"
        >
          Reset
        </button>
      </div>

      {/* Articles Feed */}
      <div className="space-y-3">
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <Loader2 className="w-6 h-6 text-blue-900 animate-spin" />
          </div>
        ) : articles.length === 0 ? (
          <div className="bg-white border border-slate-200/80 rounded-xl p-10 text-center text-slate-400 text-xs">
            <Newspaper className="w-8 h-8 mx-auto mb-2 text-slate-300" />
            No articles found matching the current filters.
          </div>
        ) : (
          articles.map((art) => {
            const isPos = art.sentiment === 'positive';
            const isNeg = art.sentiment === 'negative';
            return (
              <div
                key={art.id}
                className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-xs hover:border-slate-300 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-[11px] font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                        {art.company_name || 'Competitor'}
                      </span>
                      <span className="text-[11px] text-slate-400 font-medium">
                        {art.source}
                      </span>
                      <span className="text-slate-300">•</span>
                      <span className="text-[11px] text-slate-400">
                        {art.published_date || art.timestamp?.slice(0, 10)}
                      </span>
                      <span
                        className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          isPos
                            ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                            : isNeg
                            ? 'bg-red-50 text-red-800 border border-red-200'
                            : 'bg-slate-50 text-slate-600 border border-slate-200'
                        }`}
                      >
                        {isPos ? 'Positive' : isNeg ? 'Negative' : 'Neutral'} (
                        {art.sentiment_score ?? 0.0})
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-slate-900 leading-snug">
                      {art.title}
                    </h3>

                    <p className="text-xs text-slate-600 leading-relaxed line-clamp-2">
                      {art.description}
                    </p>
                  </div>

                  {art.url && art.url !== '#' && (
                    <a
                      href={art.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 p-2 text-slate-400 hover:text-blue-600 hover:bg-slate-50 rounded-lg transition-colors"
                      title="Open source article"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      <p className="text-[11px] text-slate-400 text-center italic">
        Disclaimer: News sentiment reflects public reporting and tone, and does not represent
        audited financial performance or internal company operations.
      </p>
    </div>
  );
}
