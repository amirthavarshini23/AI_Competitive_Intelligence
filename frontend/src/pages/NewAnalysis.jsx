import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Globe,
  Building2,
  Rocket,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Cpu,
  ShieldCheck,
  HelpCircle,
} from 'lucide-react';
import { runAnalysis, getStoredConfig } from '../api/client';

const PIPELINE_STAGES = [
  {
    key: 'scrape',
    title: 'Website Intelligence Collection',
    desc: 'Multi-page domain crawl, HTML noise stripping, headings & product extraction',
    icon: Globe,
  },
  {
    key: 'news',
    title: 'News & Press Aggregation',
    desc: 'Public technology RSS feeds (Google News, HackerNews, TechCrunch) + VADER sentiment',
    icon: Building2,
  },
  {
    key: 'nlp',
    title: 'Local NLP & AI Analysis',
    desc: 'TF-IDF semantic analysis, entity extraction & local Ollama / rule-based reasoning',
    icon: Cpu,
  },
  {
    key: 'report',
    title: 'Strategic Dossier & SWOT Matrix',
    desc: 'Synthesizing 6 pillars, 4-quadrant SWOT, and analytical indicators',
    icon: Rocket,
  },
];

export default function NewAnalysis() {
  const navigate = useNavigate();
  const config = getStoredConfig();

  const [form, setForm] = useState({ company_name: '', website_url: '' });
  const [running, setRunning] = useState(false);
  const [currentStage, setCurrentStage] = useState(-1);
  const [stageMessage, setStageMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!form.company_name.trim()) return setError('Please enter a competitor name.');
    if (!form.website_url.trim()) return setError('Please enter a company website URL.');

    setRunning(true);
    setCurrentStage(0);
    setStageMessage('Crawling website pages and extracting clean content...');

    // Progress updates corresponding to real stages
    const timer1 = setTimeout(() => {
      setCurrentStage(1);
      setStageMessage('Collecting recent public news and computing sentiment scores...');
    }, 2500);

    const timer2 = setTimeout(() => {
      setCurrentStage(2);
      setStageMessage('Running local NLP term extraction and SWOT synthesis...');
    }, 5500);

    try {
      const result = await runAnalysis({
        company_name: form.company_name.trim(),
        website_url: form.website_url.trim(),
        gemini_key: config.gemini_key || '',
        news_key: config.news_key || '',
        use_ollama: config.use_ollama,
        ollama_model: config.ollama_model,
      });

      clearTimeout(timer1);
      clearTimeout(timer2);
      setCurrentStage(3);
      setStageMessage('Dossier generated successfully! Redirecting...');

      setTimeout(() => {
        navigate(`/report/${result.analysis_id}`);
      }, 700);
    } catch (err) {
      clearTimeout(timer1);
      clearTimeout(timer2);
      setRunning(false);
      setCurrentStage(-1);
      const msg = err.response?.data?.detail || err.message || 'Analysis pipeline encountered an error.';
      setError(msg);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-xl lg:text-2xl font-bold text-slate-900 tracking-tight">
          New Competitor Analysis
        </h1>
        <p className="text-xs lg:text-sm text-slate-500 mt-1">
          Collects public web data, parses news via independent RSS, and synthesizes 6-pillar
          strategic intelligence and SWOT analysis.
        </p>
      </div>

      {/* Form Card */}
      <form
        onSubmit={handleSubmit}
        className="bg-white border border-slate-200/80 rounded-xl p-6 lg:p-7 shadow-xs space-y-6"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Competitor Name */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Competitor Name
            </label>
            <div className="relative">
              <Building2 className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={form.company_name}
                onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                placeholder="e.g. Microsoft, Anthropic, Cohere"
                disabled={running}
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 text-xs text-slate-800 placeholder:text-slate-400 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 outline-none disabled:bg-slate-50 transition-colors"
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-1.5">
              Exact company or organization name used for news syndication matching.
            </p>
          </div>

          {/* Website URL */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Company Website URL
            </label>
            <div className="relative">
              <Globe className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={form.website_url}
                onChange={(e) => setForm({ ...form, website_url: e.target.value })}
                placeholder="e.g. https://www.microsoft.com"
                disabled={running}
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 text-xs text-slate-800 placeholder:text-slate-400 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 outline-none disabled:bg-slate-50 transition-colors"
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-1.5">
              Domain will be sanitized and crawled securely (domain-scoped, SSRF safe).
            </p>
          </div>
        </div>

        {/* Engine Notification Banner */}
        <div className="flex items-start gap-3 p-3.5 rounded-lg bg-slate-50 border border-slate-200/80 text-xs">
          <ShieldCheck className="w-4 h-4 text-blue-800 shrink-0 mt-0.5" />
          <div className="text-slate-600 leading-relaxed">
            <span className="font-semibold text-slate-900">Zero Paid API Dependency:</span>{' '}
            Uses local multi-page BeautifulSoup scraping, public RSS feeds (Google News &
            TechCrunch), local NLTK VADER sentiment analysis, and Ollama / rule-based NLP.
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="flex items-start gap-2.5 p-3 rounded-lg bg-red-50 border border-red-200 text-xs text-red-800">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
            <p>{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={running}
          className="w-full flex items-center justify-center gap-2 bg-blue-900 hover:bg-blue-800 text-white py-3 rounded-lg text-xs font-bold tracking-wide shadow-xs disabled:opacity-60 disabled:cursor-not-allowed transition-all"
        >
          {running ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Executing Pipeline...
            </>
          ) : (
            <>
              <Rocket className="w-4 h-4" />
              Start Competitive Analysis
            </>
          )}
        </button>
      </form>

      {/* 4 Pipeline Stages Progress Card */}
      {running && (
        <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Pipeline Execution Status
            </h3>
            <span className="text-xs font-medium text-blue-700 animate-pulse">
              {stageMessage}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {PIPELINE_STAGES.map((stage, idx) => {
              const Icon = stage.icon;
              const isDone = currentStage > idx;
              const isActive = currentStage === idx;
              const isPending = currentStage < idx;

              return (
                <div
                  key={stage.key}
                  className={`p-3.5 rounded-lg border transition-all ${
                    isDone
                      ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900'
                      : isActive
                      ? 'bg-blue-50 border-blue-300 text-blue-950 ring-2 ring-blue-500/20'
                      : 'bg-slate-50/60 border-slate-200/60 text-slate-400'
                  }`}
                >
                  <div className="flex items-center gap-2.5 mb-1">
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : isActive ? (
                      <Loader2 className="w-4 h-4 text-blue-600 animate-spin shrink-0" />
                    ) : (
                      <Icon className="w-4 h-4 text-slate-400 shrink-0" />
                    )}
                    <span className="text-xs font-bold tracking-tight">
                      {idx + 1}. {stage.title}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 ml-6 leading-relaxed">
                    {stage.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
