import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Building2,
  FileText,
  Newspaper,
  Activity,
  PlusCircle,
  ArrowRight,
  TrendingUp,
  AlertCircle,
  Layers,
  Search,
  ExternalLink,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { getDashboardStats } from '../api/client';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats()
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const chartData = stats?.competitor_activity_chart || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-blue-900 via-slate-900 to-blue-950 text-white rounded-xl p-6 lg:p-7 shadow-xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-500/20 text-blue-200 border border-blue-400/20">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
              Strategic AI Platform
            </div>
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight">
              Competitive Intelligence & Market Strategy Dashboard
            </h1>
            <p className="text-slate-300 text-xs lg:text-sm max-w-2xl leading-relaxed">
              Automated multi-page web scraping, free RSS news aggregation, local NLP,
              RAG semantic retrieval, and multi-competitor strategy comparison.
            </p>
          </div>
          <div className="flex flex-wrap gap-2.5">
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-lg text-xs font-semibold shadow-xs transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              Analyze Competitor
            </Link>
            <Link
              to="/compare"
              className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/15 text-white border border-white/20 px-4 py-2.5 rounded-lg text-xs font-semibold transition-all"
            >
              Compare Competitors
            </Link>
          </div>
        </div>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Building2}
          label="Competitors Analyzed"
          value={loading ? '—' : stats?.total_competitors || 0}
          color="blue"
        />
        <StatCard
          icon={FileText}
          label="Reports Generated"
          value={loading ? '—' : stats?.total_analyses || 0}
          color="indigo"
        />
        <StatCard
          icon={Newspaper}
          label="Articles Aggregated"
          value={loading ? '—' : stats?.total_news_articles || 0}
          color="emerald"
        />
        <StatCard
          icon={Activity}
          label="Monitored Competitors"
          value={loading ? '—' : stats?.active_monitoring_jobs || 0}
          color="amber"
        />
      </div>

      {/* Main Grid: Chart & Detected Changes */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Competitor Activity Chart */}
        <div className="lg:col-span-2 bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-800 tracking-tight">
                Competitor Strategic Indicator Comparison
              </h2>
              <p className="text-xs text-slate-500">
                AI Adoption, Product Velocity, and Market Presence signals (0–100 scale)
              </p>
            </div>
            <Link to="/compare" className="text-xs text-blue-600 hover:text-blue-700 font-semibold">
              Deep Compare →
            </Link>
          </div>

          <div className="h-64 w-full">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Bar dataKey="ai_tech" name="AI Adoption" fill="#1e3a8a" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="velocity" name="Velocity" fill="#2563eb" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="presence" name="Presence" fill="#059669" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs">
                <Layers className="w-8 h-8 mb-2 stroke-1 text-slate-300" />
                <p>Run your first competitor analysis to generate activity metrics.</p>
              </div>
            )}
          </div>
        </div>

        {/* Latest Detected Changes */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs flex flex-col">
          <div className="flex items-center justify-between mb-3.5">
            <h2 className="text-sm font-bold text-slate-800 tracking-tight">
              Website Change Alerts
            </h2>
            <Link
              to="/monitoring"
              className="text-xs text-blue-600 hover:text-blue-700 font-semibold"
            >
              Monitor All →
            </Link>
          </div>

          <div className="flex-1 space-y-2.5 overflow-y-auto">
            {stats?.recent_changes?.length > 0 ? (
              stats.recent_changes.map((change) => (
                <div
                  key={change.id}
                  className="p-3 rounded-lg border border-slate-100 bg-slate-50/70 hover:bg-slate-100/60 transition-colors"
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-xs font-bold text-slate-800 truncate">
                      {change.company_name}
                    </span>
                    <span className="text-[10px] text-slate-400 shrink-0">
                      {change.detected_at?.slice(5, 16)}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                    {change.change_summary}
                  </p>
                </div>
              ))
            ) : (
              <div className="h-44 flex flex-col items-center justify-center text-slate-400 text-xs text-center p-4">
                <Activity className="w-6 h-6 mb-1.5 stroke-1 text-slate-300" />
                <p>No changes detected yet.</p>
                <Link to="/monitoring" className="text-blue-600 font-semibold mt-1">
                  Add to monitoring
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Analyses Table */}
      <div className="bg-white border border-slate-200/80 rounded-xl shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-800 tracking-tight">
            Recent Intelligence Analyses
          </h2>
          <Link
            to="/history"
            className="text-xs text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
          >
            All records <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/60 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                <th className="text-left px-5 py-3">Competitor</th>
                <th className="text-left px-5 py-3 hidden md:table-cell">Website</th>
                <th className="text-left px-5 py-3">Engine Used</th>
                <th className="text-left px-5 py-3">Timestamp</th>
                <th className="text-right px-5 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {stats?.recent_analyses?.length > 0 ? (
                stats.recent_analyses.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-5 py-3.5 font-bold text-slate-900">{item.company_name}</td>
                    <td className="px-5 py-3.5 text-slate-500 hidden md:table-cell max-w-xs truncate">
                      {item.website_url}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200/60">
                        {item.engine_used || 'Extractive NLP'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-slate-500 whitespace-nowrap">
                      {item.timestamp}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        to={`/report/${item.id}`}
                        className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 font-bold text-xs"
                      >
                        View Report →
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-slate-400">
                    No competitor analyses recorded yet. Click 'Analyze Competitor' to begin.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-800 border-blue-100',
    indigo: 'bg-indigo-50 text-indigo-800 border-indigo-100',
    emerald: 'bg-emerald-50 text-emerald-800 border-emerald-100',
    amber: 'bg-amber-50 text-amber-800 border-amber-100',
  };

  return (
    <div className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-xs">
      <div className="flex items-center gap-3">
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center border ${colorMap[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
        <div className="min-w-0">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider truncate">
            {label}
          </p>
          <p className="text-xl font-bold text-slate-900 tracking-tight leading-tight mt-0.5">
            {value}
          </p>
        </div>
      </div>
    </div>
  );
}
