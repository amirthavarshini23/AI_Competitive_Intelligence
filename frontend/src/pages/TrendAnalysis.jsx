import { useEffect, useState } from 'react';
import {
  TrendingUp,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Loader2,
  Calendar,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { getTrendCompetitors, getCompetitorTrends } from '../api/client';

export default function TrendAnalysis() {
  const [competitors, setCompetitors] = useState([]);
  const [selectedCompId, setSelectedCompId] = useState('');
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingTrends, setLoadingTrends] = useState(false);

  useEffect(() => {
    getTrendCompetitors()
      .then((data) => {
        setCompetitors(data);
        if (data && data.length > 0) {
          setSelectedCompId(data[0].id);
          fetchTrends(data[0].id);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const fetchTrends = (id) => {
    setLoadingTrends(true);
    getCompetitorTrends(id)
      .then(setTrendData)
      .catch(() => {})
      .finally(() => setLoadingTrends(false));
  };

  const handleSelect = (e) => {
    const id = e.target.value;
    setSelectedCompId(id);
    fetchTrends(id);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-900 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl lg:text-2xl font-bold text-slate-900 tracking-tight">
          Longitudinal Historical Trend Analysis
        </h1>
        <p className="text-xs lg:text-sm text-slate-500 mt-1">
          Track strategic shift over time, monitor emerging vs. declining topics, and measure
          keyword drift across sequential snapshots.
        </p>
      </div>

      {/* Competitor Selector */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Select Competitor:
          </label>
          <select
            value={selectedCompId}
            onChange={handleSelect}
            className="py-2 px-3 rounded-lg border border-slate-300 text-xs bg-white text-slate-800 font-semibold focus:ring-2 focus:ring-blue-600 outline-none"
          >
            {competitors.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} ({c.snapshot_count} snapshot{c.snapshot_count > 1 ? 's' : ''})
              </option>
            ))}
          </select>
        </div>

        {trendData && (
          <div className="text-xs text-slate-500">
            Total Snapshots Recorded:{' '}
            <span className="font-bold text-slate-900">{trendData.total_snapshots}</span>
          </div>
        )}
      </div>

      {loadingTrends ? (
        <div className="flex items-center justify-center h-48">
          <Loader2 className="w-6 h-6 text-blue-900 animate-spin" />
        </div>
      ) : trendData ? (
        <div className="space-y-6">
          {/* Summary Card */}
          <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Shift Assessment & Synthesis
              </h2>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-900 border border-blue-200">
                Strategic Drift Score: {trendData.shift_score}%
              </span>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed">{trendData.summary}</p>
          </div>

          {/* Indicator Trend Line Chart */}
          <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
            <h2 className="text-sm font-bold text-slate-800 tracking-tight mb-1">
              Indicator Trajectory Across Snapshots
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              Progression of AI Adoption, Product Velocity, and Market Presence signals over time
            </p>

            <div className="h-64 w-full">
              {trendData.timeline?.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendData.timeline} margin={{ top: 10, right: 20, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="timestamp" tick={{ fontSize: 11, fill: '#64748b' }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} />
                    <Tooltip contentStyle={{ fontSize: '11px', borderRadius: '6px' }} />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                    <Line
                      type="monotone"
                      dataKey="ai_tech_adoption"
                      name="AI Tech Adoption"
                      stroke="#1e3a8a"
                      strokeWidth={2}
                      activeDot={{ r: 5 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="product_velocity"
                      name="Product Velocity"
                      stroke="#2563eb"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="market_presence"
                      name="Market Presence"
                      stroke="#059669"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                  Insufficient chronological data to plot trajectory line.
                </div>
              )}
            </div>
          </div>

          {/* Emerging vs Declining Topics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Emerging */}
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
              <div className="flex items-center gap-2 mb-3 text-emerald-800 font-bold text-xs uppercase tracking-wider">
                <ArrowUpRight className="w-4 h-4 text-emerald-600" />
                Newly Emerging Topics
              </div>
              {trendData.emerging_topics?.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {trendData.emerging_topics.map((t, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200"
                    >
                      + {t}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No new topic emergence detected between snapshots.</p>
              )}
            </div>

            {/* Declining */}
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
              <div className="flex items-center gap-2 mb-3 text-slate-600 font-bold text-xs uppercase tracking-wider">
                <ArrowDownRight className="w-4 h-4 text-slate-400" />
                Declining / Deprioritized Topics
              </div>
              {trendData.declining_topics?.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {trendData.declining_topics.map((t, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200"
                    >
                      - {t}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No noticeable topic dropoff between snapshots.</p>
              )}
            </div>
          </div>

          {/* Keyword Evolution Table */}
          {trendData.keyword_comparison?.length > 0 && (
            <div className="bg-white border border-slate-200/80 rounded-xl shadow-xs overflow-hidden">
              <div className="p-4 border-b border-slate-100">
                <h2 className="text-sm font-bold text-slate-800 tracking-tight">
                  TF-IDF Term Importance Evolution
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/70 text-slate-500 font-semibold uppercase text-[10px]">
                      <th className="text-left px-5 py-3">Term / Phrase</th>
                      <th className="text-left px-5 py-3">Baseline TF-IDF Weight</th>
                      <th className="text-left px-5 py-3">Recent TF-IDF Weight</th>
                      <th className="text-right px-5 py-3">Trend Direction</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700">
                    {trendData.keyword_comparison.map((k, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/40">
                        <td className="px-5 py-3 font-semibold text-slate-900">{k.term}</td>
                        <td className="px-5 py-3 text-slate-500">{k.initial_importance ?? k.score}</td>
                        <td className="px-5 py-3 text-slate-500">{k.recent_importance ?? k.score}</td>
                        <td className="px-5 py-3 text-right">
                          <span
                            className={`inline-flex items-center gap-1 font-bold ${
                              k.trend === 'Rising'
                                ? 'text-emerald-700'
                                : k.trend === 'Falling'
                                ? 'text-amber-700'
                                : 'text-slate-500'
                            }`}
                          >
                            {k.trend === 'Rising' && <ArrowUpRight className="w-3.5 h-3.5" />}
                            {k.trend === 'Falling' && <ArrowDownRight className="w-3.5 h-3.5" />}
                            {k.trend === 'Stable' && <Minus className="w-3.5 h-3.5" />}
                            {k.trend || 'Baseline'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
