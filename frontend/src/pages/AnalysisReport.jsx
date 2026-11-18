import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import {
  ArrowLeft,
  Download,
  Building2,
  Globe,
  Calendar,
  Target,
  TrendingUp,
  Lightbulb,
  AlertTriangle,
  Compass,
  Newspaper,
  ExternalLink,
  Loader2,
  Layers,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { getAnalysisDetails, getPdfUrl } from '../api/client';

const SECTIONS = [
  { key: 'company_overview', label: 'Company Overview', icon: Building2, color: 'blue' },
  { key: 'current_business_focus', label: 'Business Focus', icon: Target, color: 'emerald' },
  { key: 'hiring_product_trends', label: 'Trends & Launches', icon: TrendingUp, color: 'violet' },
  { key: 'market_opportunities', label: 'Market Opportunities', icon: Lightbulb, color: 'amber' },
  { key: 'potential_risks', label: 'Potential Risks', icon: AlertTriangle, color: 'red' },
  { key: 'predicted_future_direction', label: 'Future Direction', icon: Compass, color: 'indigo' },
];

export default function AnalysisReport() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('company_overview');

  useEffect(() => {
    getAnalysisDetails(id)
      .then(setData)
      .catch((e) => setError(e.response?.data?.detail || 'Failed to load report.'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-900 animate-spin" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto mb-3" />
        <h2 className="text-base font-bold text-slate-800 mb-1">Error Loading Report</h2>
        <p className="text-xs text-slate-500 mb-4">{error || 'Record not found.'}</p>
        <Link to="/history" className="text-blue-600 font-semibold text-xs hover:underline">
          ← Return to History
        </Link>
      </div>
    );
  }

  const { company_name, website_url, analysis, news, swot, scores, engine_used, timestamp } = data;
  const activeSection = SECTIONS.find((s) => s.key === activeTab);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Top Breadcrumb & Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <Link
          to="/history"
          className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 font-semibold"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to History
        </Link>
        <a
          href={getPdfUrl(id)}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 bg-blue-900 hover:bg-blue-800 text-white px-4 py-2.5 rounded-lg text-xs font-bold shadow-xs transition-all self-start"
        >
          <Download className="w-4 h-4" />
          Download Corporate PDF Report
        </a>
      </div>

      {/* Header Profile Card */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-900 flex items-center justify-center text-white font-bold text-lg shadow-xs">
              {company_name?.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-slate-900 tracking-tight">{company_name}</h1>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-900 border border-blue-200">
                  {engine_used || 'Extractive NLP'}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5 text-xs text-slate-500">
                <a
                  href={website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 inline-flex items-center gap-1 truncate max-w-xs"
                >
                  <Globe className="w-3.5 h-3.5" />
                  {website_url}
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
                <span className="inline-flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {timestamp}
                </span>
                <span className="inline-flex items-center gap-1">
                  <Newspaper className="w-3.5 h-3.5" />
                  {news?.length || 0} news articles
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Tabbed Container */}
      <div className="bg-white border border-slate-200/80 rounded-xl shadow-xs overflow-hidden">
        {/* Tab Headers */}
        <div className="border-b border-slate-200 overflow-x-auto bg-slate-50/50">
          <div className="flex min-w-max">
            {SECTIONS.map((sec) => {
              const Icon = sec.icon;
              const isActive = activeTab === sec.key;
              return (
                <button
                  key={sec.key}
                  onClick={() => setActiveTab(sec.key)}
                  className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-all whitespace-nowrap ${
                    isActive
                      ? 'border-blue-900 text-blue-900 bg-white font-bold'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {sec.label}
                </button>
              );
            })}

            {/* SWOT Matrix Tab */}
            <button
              onClick={() => setActiveTab('swot')}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-all whitespace-nowrap ${
                activeTab === 'swot'
                  ? 'border-blue-900 text-blue-900 bg-white font-bold'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              SWOT Analysis
            </button>

            {/* News Coverage Tab */}
            <button
              onClick={() => setActiveTab('news')}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-all whitespace-nowrap ${
                activeTab === 'news'
                  ? 'border-blue-900 text-blue-900 bg-white font-bold'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Newspaper className="w-3.5 h-3.5" />
              News Coverage ({news?.length || 0})
            </button>
          </div>
        </div>

        {/* Tab Content Body */}
        <div className="p-6 lg:p-8">
          {activeTab === 'swot' ? (
            <SwotMatrixView swot={swot} companyName={company_name} />
          ) : activeTab === 'news' ? (
            <NewsTabContent articles={news} />
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2.5">
                  {activeSection && <activeSection.icon className="w-5 h-5 text-blue-900" />}
                  <h2 className="text-base font-bold text-slate-900 tracking-tight">
                    {activeSection?.label}
                  </h2>
                </div>
                <span className="text-[11px] font-semibold text-slate-400">
                  Grounding: Scraped Web Data & Signal Processing
                </span>
              </div>
              <div className="prose prose-sm max-w-none text-slate-700 leading-relaxed">
                <ReactMarkdown>{analysis?.[activeTab] || 'Section details unavailable.'}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SwotMatrixView({ swot, companyName }) {
  if (!swot || !swot.strengths) {
    return (
      <div className="text-center py-8 text-slate-400 text-xs">
        SWOT matrix data unavailable for this record.
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-sm font-bold text-slate-900 tracking-tight">
          Strategic SWOT Matrix for {companyName}
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Internal capabilities (Strengths & Weaknesses) and external market factors (Opportunities & Threats)
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Strengths */}
        <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/50 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-blue-950 uppercase tracking-wider">
              Strengths (Internal)
            </span>
            <span className="text-[10px] font-semibold text-blue-700 bg-blue-100 px-2 py-0.5 rounded">
              {swot.strengths?.confidence || 'High'}
            </span>
          </div>
          <ul className="space-y-1.5 text-xs text-slate-700">
            {swot.strengths?.points?.map((p, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-blue-700 font-bold">•</span>
                <span>{p}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Weaknesses */}
        <div className="p-4 rounded-xl border border-red-200 bg-red-50/50 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-red-950 uppercase tracking-wider">
              Weaknesses (Internal)
            </span>
            <span className="text-[10px] font-semibold text-red-700 bg-red-100 px-2 py-0.5 rounded">
              {swot.weaknesses?.confidence || 'Medium'}
            </span>
          </div>
          <ul className="space-y-1.5 text-xs text-slate-700">
            {swot.weaknesses?.points?.map((p, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-red-700 font-bold">•</span>
                <span>{p}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Opportunities */}
        <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/50 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-950 uppercase tracking-wider">
              Opportunities (External)
            </span>
            <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
              {swot.opportunities?.confidence || 'Medium'}
            </span>
          </div>
          <ul className="space-y-1.5 text-xs text-slate-700">
            {swot.opportunities?.points?.map((p, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-emerald-700 font-bold">•</span>
                <span>{p}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Threats */}
        <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/50 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-amber-950 uppercase tracking-wider">
              Threats (External)
            </span>
            <span className="text-[10px] font-semibold text-amber-700 bg-amber-100 px-2 py-0.5 rounded">
              {swot.threats?.confidence || 'Medium'}
            </span>
          </div>
          <ul className="space-y-1.5 text-xs text-slate-700">
            {swot.threats?.points?.map((p, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-amber-700 font-bold">•</span>
                <span>{p}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function NewsTabContent({ articles }) {
  if (!articles || articles.length === 0) {
    return (
      <div className="text-center py-10 text-slate-400 text-xs">
        <Newspaper className="w-8 h-8 mx-auto mb-2 text-slate-300" />
        No news articles collected for this company.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <h2 className="text-sm font-bold text-slate-900 tracking-tight">
          Recent Public Press & Media Coverage
        </h2>
        <span className="text-xs text-slate-400">Aggregated via Public RSS Feeds</span>
      </div>

      <div className="space-y-3">
        {articles.map((art, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-1 min-w-0">
                <div className="flex items-center gap-2 text-[11px] text-slate-400">
                  <span className="font-semibold text-slate-700">{art.source}</span>
                  <span>•</span>
                  <span>{art.published_date || art.date}</span>
                  {art.sentiment && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-700">
                      {art.sentiment}
                    </span>
                  )}
                </div>
                <h3 className="text-xs font-bold text-slate-900 leading-snug">{art.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed line-clamp-2">
                  {art.description}
                </p>
              </div>

              {art.url && art.url !== '#' && (
                <a
                  href={art.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="shrink-0 p-1.5 text-slate-400 hover:text-blue-600 rounded transition-colors"
                  title="Open source article"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
