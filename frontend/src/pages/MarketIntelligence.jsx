import { useEffect, useState } from 'react';
import {
  LineChart as LineChartIcon,
  Lightbulb,
  AlertTriangle,
  Compass,
  Building2,
  Shield,
  Loader2,
} from 'lucide-react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
  Legend,
} from 'recharts';
import { getMarketOverview } from '../api/client';

export default function MarketIntelligence() {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMarketOverview()
      .then(setMarketData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-900 animate-spin" />
      </div>
    );
  }

  const positioningData = marketData?.positioning || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl lg:text-2xl font-bold text-slate-900 tracking-tight">
          Market Intelligence & Landscape Analysis
        </h1>
        <p className="text-xs lg:text-sm text-slate-500 mt-1">
          Cross-competitor opportunity detection, risk distribution, and competitive landscape
          positioning based on collected web signals.
        </p>
      </div>

      {/* Positioning Matrix Chart */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
        <div className="mb-4">
          <h2 className="text-sm font-bold text-slate-800 tracking-tight">
            Competitive Positioning Matrix
          </h2>
          <p className="text-xs text-slate-500">
            X-Axis: AI & Technology Adoption Signal | Y-Axis: Product Velocity Signal
          </p>
        </div>

        <div className="h-72 w-full">
          {positioningData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 10, left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis
                  type="number"
                  dataKey="ai_tech_adoption"
                  name="AI Adoption"
                  domain={[30, 100]}
                  unit=" pts"
                  tick={{ fontSize: 11, fill: '#64748b' }}
                />
                <YAxis
                  type="number"
                  dataKey="product_velocity"
                  name="Velocity"
                  domain={[30, 100]}
                  unit=" pts"
                  tick={{ fontSize: 11, fill: '#64748b' }}
                />
                <ZAxis range={[100, 200]} />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ payload }) => {
                    if (payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white border border-slate-200 p-2.5 rounded-lg shadow-xs text-xs">
                          <p className="font-bold text-slate-900">{data.company_name}</p>
                          <p className="text-slate-500">AI Tech Adoption: {data.ai_tech_adoption}</p>
                          <p className="text-slate-500">Product Velocity: {data.product_velocity}</p>
                          <p className="text-slate-500">Market Presence: {data.market_presence}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter name="Competitors" data={positioningData} fill="#1e3a8a" />
              </ScatterChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-400 text-xs">
              No positioning data available yet. Analyze competitors to plot the market matrix.
            </div>
          )}
        </div>
      </div>

      {/* Opportunities & Risks Two-Column Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Market Opportunities */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs flex flex-col">
          <div className="flex items-center gap-2 mb-3 text-emerald-800">
            <Lightbulb className="w-5 h-5 text-emerald-600" />
            <h2 className="text-sm font-bold text-slate-900 tracking-tight">
              Cross-Competitor Market Opportunities
            </h2>
          </div>
          <div className="space-y-3 flex-1 overflow-y-auto">
            {marketData?.opportunities?.length > 0 ? (
              marketData.opportunities.map((opp, idx) => (
                <div key={idx} className="p-3.5 rounded-lg bg-emerald-50/50 border border-emerald-100 text-xs space-y-1">
                  <span className="font-bold text-emerald-950">{opp.company_name}</span>
                  <p className="text-slate-600 leading-relaxed">{opp.summary}</p>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-xs py-8 text-center">No opportunities recorded yet.</p>
            )}
          </div>
        </div>

        {/* Potential Risks */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs flex flex-col">
          <div className="flex items-center gap-2 mb-3 text-red-800">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h2 className="text-sm font-bold text-slate-900 tracking-tight">
              Identified Risks & Vulnerabilities
            </h2>
          </div>
          <div className="space-y-3 flex-1 overflow-y-auto">
            {marketData?.risks?.length > 0 ? (
              marketData.risks.map((r, idx) => (
                <div key={idx} className="p-3.5 rounded-lg bg-red-50/50 border border-red-100 text-xs space-y-1">
                  <span className="font-bold text-red-950">{r.company_name}</span>
                  <p className="text-slate-600 leading-relaxed">{r.summary}</p>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-xs py-8 text-center">No risks recorded yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
