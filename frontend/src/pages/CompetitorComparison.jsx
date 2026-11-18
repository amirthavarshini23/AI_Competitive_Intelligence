import { useEffect, useState } from 'react';
import {
  Scale,
  Check,
  AlertCircle,
  Loader2,
  TrendingUp,
  Shield,
  Layers,
  HelpCircle,
} from 'lucide-react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import { getAvailableCompetitors, compareCompetitors } from '../api/client';

const COLORS = ['#1e3a8a', '#2563eb', '#059669', '#d97706'];

export default function CompetitorComparison() {
  const [competitors, setCompetitors] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getAvailableCompetitors()
      .then((data) => {
        setCompetitors(data);
        // Pre-select first 2 competitors if available
        if (data && data.length >= 2) {
          const initial = [data[0].id, data[1].id];
          setSelectedIds(initial);
          handleRunCompare(initial);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const toggleSelect = (id) => {
    setError('');
    if (selectedIds.includes(id)) {
      if (selectedIds.length <= 2) {
        setError('Comparison requires at least 2 competitors.');
        return;
      }
      setSelectedIds(selectedIds.filter((item) => item !== id));
    } else {
      if (selectedIds.length >= 4) {
        setError('Maximum of 4 competitors can be compared simultaneously.');
        return;
      }
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleRunCompare = async (ids = selectedIds) => {
    if (ids.length < 2) {
      setError('Please select at least 2 competitors.');
      return;
    }
    setComparing(true);
    setError('');
    try {
      const res = await compareCompetitors(ids);
      setComparisonResult(res);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Comparison failed.');
    } finally {
      setComparing(false);
    }
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
          Competitor Benchmarking & Comparison
        </h1>
        <p className="text-xs lg:text-sm text-slate-500 mt-1">
          Select between 2 and 4 analyzed competitors to benchmark strategic dimensions,
          radar chart indicators, and differentiation vectors.
        </p>
      </div>

      {/* Competitor Selector Strip */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
          <div>
            <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Select Competitors ({selectedIds.length}/4 selected)
            </h2>
            <p className="text-[11px] text-slate-400">Click to select or deselect competitors</p>
          </div>
          <button
            onClick={() => handleRunCompare(selectedIds)}
            disabled={comparing || selectedIds.length < 2}
            className="inline-flex items-center gap-1.5 bg-blue-900 hover:bg-blue-800 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow-xs disabled:opacity-50 transition-all self-start"
          >
            {comparing ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Comparing...
              </>
            ) : (
              <>
                <Scale className="w-3.5 h-3.5" />
                Update Comparison
              </>
            )}
          </button>
        </div>

        {competitors.length === 0 ? (
          <div className="text-center py-6 text-slate-400 text-xs">
            No competitors analyzed yet. Run at least two analyses from the New Analysis page.
          </div>
        ) : (
          <div className="flex flex-wrap gap-2.5">
            {competitors.map((comp) => {
              const isSelected = selectedIds.includes(comp.id);
              return (
                <button
                  key={comp.id}
                  onClick={() => toggleSelect(comp.id)}
                  className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold border transition-all ${
                    isSelected
                      ? 'bg-blue-900 text-white border-blue-900 shadow-xs'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  <span
                    className={`w-4 h-4 rounded-full flex items-center justify-center border text-[10px] ${
                      isSelected ? 'bg-white text-blue-900 border-white' : 'border-slate-300'
                    }`}
                  >
                    {isSelected && <Check className="w-3 h-3 stroke-3" />}
                  </span>
                  {comp.name}
                </button>
              );
            })}
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 mt-3 p-2.5 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Comparison Results */}
      {comparisonResult && (
        <div className="space-y-6">
          {/* Radar Chart & Bar Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Strategic Radar Chart */}
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
              <h2 className="text-sm font-bold text-slate-800 tracking-tight mb-1">
                Strategic Capability Radar
              </h2>
              <p className="text-xs text-slate-400 mb-3">
                Multi-axial comparison across 6 core indicators
              </p>

              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart
                    cx="50%"
                    cy="50%"
                    outerRadius="75%"
                    data={comparisonResult.radar_data}
                  >
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: '#475569' }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 9 }} />
                    <Tooltip contentStyle={{ fontSize: '11px', borderRadius: '6px' }} />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }} />
                    {comparisonResult.competitors?.map((comp, idx) => (
                      <Radar
                        key={comp.company_name}
                        name={comp.company_name}
                        dataKey={comp.company_name}
                        stroke={COLORS[idx % COLORS.length]}
                        fill={COLORS[idx % COLORS.length]}
                        fillOpacity={0.25}
                      />
                    ))}
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Composite Analytical Score Bar Chart */}
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
              <h2 className="text-sm font-bold text-slate-800 tracking-tight mb-1">
                Composite Analytical Scores
              </h2>
              <p className="text-xs text-slate-400 mb-3">
                Weighted aggregate from presence, velocity, AI signals, and resilience
              </p>

              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={comparisonResult.competitors}
                    margin={{ top: 15, right: 20, left: -10, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="company_name" tick={{ fontSize: 11, fill: '#475569' }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#475569' }} />
                    <Tooltip contentStyle={{ fontSize: '11px', borderRadius: '6px' }} />
                    <Bar
                      dataKey="composite_analytical_score"
                      name="Composite Score"
                      fill="#1e3a8a"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Strategic Differentiation Callout */}
          <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-5 text-xs text-slate-700 space-y-2">
            <div className="flex items-center gap-2 text-blue-900 font-bold text-sm">
              <TrendingUp className="w-4 h-4" />
              Strategic Differentiation Insight
            </div>
            <div className="prose prose-xs max-w-none text-slate-700 leading-relaxed whitespace-pre-line">
              {comparisonResult.differentiation_summary}
            </div>
            <p className="text-[11px] text-slate-400 italic pt-1 border-t border-blue-200/60">
              {comparisonResult.indicator_disclaimer}
            </p>
          </div>

          {/* Side-by-side Dimension Table */}
          <div className="bg-white border border-slate-200/80 rounded-xl shadow-xs overflow-hidden">
            <div className="p-4 border-b border-slate-100">
              <h2 className="text-sm font-bold text-slate-800 tracking-tight">
                Side-by-Side Dimension Comparison
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50/70 text-slate-500 font-semibold uppercase text-[10px]">
                    <th className="text-left px-5 py-3 w-48">Strategic Dimension</th>
                    {comparisonResult.competitors?.map((comp) => (
                      <th key={comp.company_name} className="text-left px-5 py-3 font-bold text-slate-900">
                        {comp.company_name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {comparisonResult.dimension_matrix?.map((row) => (
                    <tr key={row.dimension} className="hover:bg-slate-50/40">
                      <td className="px-5 py-4 font-bold text-slate-900 bg-slate-50/30 align-top">
                        {row.dimension}
                      </td>
                      {comparisonResult.competitors?.map((comp) => (
                        <td key={comp.company_name} className="px-5 py-4 align-top leading-relaxed text-slate-600">
                          <p className="line-clamp-6">{row.values[comp.company_name]}</p>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
