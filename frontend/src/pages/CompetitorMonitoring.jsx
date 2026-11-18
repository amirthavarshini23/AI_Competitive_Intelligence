import { useEffect, useState } from 'react';
import {
  Activity,
  Plus,
  RefreshCw,
  Clock,
  AlertCircle,
  CheckCircle2,
  ExternalLink,
  Loader2,
  Calendar,
} from 'lucide-react';
import {
  getMonitoringJobs,
  addMonitoringJob,
  checkCompetitorNow,
  getDetectedChanges,
  getAvailableCompetitors,
} from '../api/client';

export default function CompetitorMonitoring() {
  const [jobs, setJobs] = useState([]);
  const [changes, setChanges] = useState([]);
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading] = useState(true);

  // Add Job Form
  const [selectedCompId, setSelectedCompId] = useState('');
  const [intervalMin, setIntervalMin] = useState(60);
  const [adding, setAdding] = useState(false);
  const [checkingId, setCheckingId] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      getMonitoringJobs(),
      getDetectedChanges(),
      getAvailableCompetitors(),
    ])
      .then(([j, c, comps]) => {
        setJobs(j);
        setChanges(c);
        setCompetitors(comps);
        if (comps.length > 0 && !selectedCompId) {
          setSelectedCompId(comps[0].id);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const handleAddJob = async (e) => {
    e.preventDefault();
    if (!selectedCompId) return;
    setAdding(true);
    setMessage('');
    try {
      await addMonitoringJob(parseInt(selectedCompId), parseInt(intervalMin));
      setMessage('Competitor added to automated monitoring list.');
      loadData();
    } catch {
      setMessage('Failed to add competitor to monitoring.');
    } finally {
      setAdding(false);
    }
  };

  const handleCheckNow = async (competitorId) => {
    setCheckingId(competitorId);
    setMessage('');
    try {
      const res = await checkCompetitorNow(competitorId);
      setMessage(
        res.has_changed
          ? `Change detected for ${res.company_name}: ${res.change_summary}`
          : `No changes detected for ${res.company_name}. Site snapshot up to date.`
      );
      loadData();
    } catch {
      setMessage('Manual check encountered an error.');
    } finally {
      setCheckingId(null);
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
          Competitor Surface & Website Change Monitoring
        </h1>
        <p className="text-xs lg:text-sm text-slate-500 mt-1">
          Automated APScheduler checks track SHA-256 fingerprint modifications, new product sections,
          and emerging technology keywords.
        </p>
      </div>

      {message && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-900 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Add Competitor Form */}
      <form
        onSubmit={handleAddJob}
        className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-xs flex flex-wrap items-center gap-3"
      >
        <div className="flex items-center gap-2 text-xs font-bold text-slate-800 uppercase tracking-wider">
          <Activity className="w-4 h-4 text-blue-900" />
          Monitor New Competitor:
        </div>

        <select
          value={selectedCompId}
          onChange={(e) => setSelectedCompId(e.target.value)}
          className="py-2 px-3 rounded-lg border border-slate-300 text-xs bg-white text-slate-800 focus:ring-2 focus:ring-blue-600 outline-none"
        >
          {competitors.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name} ({c.website_url})
            </option>
          ))}
        </select>

        <div className="flex items-center gap-1.5 text-xs text-slate-600">
          <span>Interval:</span>
          <select
            value={intervalMin}
            onChange={(e) => setIntervalMin(e.target.value)}
            className="py-2 px-2.5 rounded-lg border border-slate-300 text-xs bg-white text-slate-800 focus:ring-2 focus:ring-blue-600 outline-none"
          >
            <option value="15">Every 15 min</option>
            <option value="60">Every 1 hour</option>
            <option value="360">Every 6 hours</option>
            <option value="1440">Every 24 hours</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={adding || !selectedCompId}
          className="inline-flex items-center gap-1.5 bg-blue-900 hover:bg-blue-800 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow-xs disabled:opacity-50 transition-colors"
        >
          {adding ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
          Add to Monitoring
        </button>
      </form>

      {/* Monitoring Jobs Table */}
      <div className="bg-white border border-slate-200/80 rounded-xl shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-800 tracking-tight">
            Active Competitor Monitoring Surfaces ({jobs.length})
          </h2>
          <span className="text-[11px] text-slate-400">Background Worker: Active</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/70 text-slate-500 font-semibold uppercase text-[10px]">
                <th className="text-left px-5 py-3">Competitor</th>
                <th className="text-left px-5 py-3 hidden md:table-cell">Target URL</th>
                <th className="text-left px-5 py-3">Last Checked</th>
                <th className="text-left px-5 py-3 hidden sm:table-cell">Next Check</th>
                <th className="text-left px-5 py-3">Changes</th>
                <th className="text-right px-5 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {jobs.length > 0 ? (
                jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-50/40">
                    <td className="px-5 py-3.5 font-bold text-slate-900">{job.company_name}</td>
                    <td className="px-5 py-3.5 text-slate-500 hidden md:table-cell max-w-xs truncate">
                      {job.website_url}
                    </td>
                    <td className="px-5 py-3.5 text-slate-500 whitespace-nowrap">
                      {job.last_checked || 'Initial check pending'}
                    </td>
                    <td className="px-5 py-3.5 text-slate-400 hidden sm:table-cell whitespace-nowrap">
                      {job.next_check || 'Scheduled'}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="px-2 py-0.5 rounded-full font-bold bg-slate-100 text-slate-700 text-[10px]">
                        {job.change_count || 0} events
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        onClick={() => handleCheckNow(job.competitor_id)}
                        disabled={checkingId === job.competitor_id}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs transition-colors disabled:opacity-50"
                      >
                        <RefreshCw
                          className={`w-3.5 h-3.5 ${
                            checkingId === job.competitor_id ? 'animate-spin text-blue-600' : ''
                          }`}
                        />
                        Check Now
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-slate-400">
                    No competitors currently monitored. Select a competitor above to start tracking.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detected Changes Log */}
      <div className="bg-white border border-slate-200/80 rounded-xl shadow-xs p-5">
        <h2 className="text-sm font-bold text-slate-800 tracking-tight mb-4">
          Historical Change Detection Log ({changes.length} events)
        </h2>

        {changes.length > 0 ? (
          <div className="space-y-3">
            {changes.map((c) => (
              <div
                key={c.id}
                className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900">{c.company_name}</span>
                    <span className="text-[10px] font-semibold text-blue-800 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded">
                      {c.change_type}
                    </span>
                    <span className="text-[11px] text-slate-400">• {c.detected_at}</span>
                  </div>
                  <p className="text-slate-600">{c.change_summary}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 py-4 text-center">
            No change alerts recorded yet. When a website content update is detected during checks,
            the diff and new keywords will appear here.
          </p>
        )}
      </div>
    </div>
  );
}
