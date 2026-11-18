import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Clock,
  Search,
  Trash2,
  Eye,
  Download,
  FileText,
  Loader2,
  PlusCircle,
} from 'lucide-react';
import { getAnalyses, deleteAnalysis, getPdfUrl } from '../api/client';

export default function History() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  const fetchRecords = () => {
    setLoading(true);
    getAnalyses()
      .then(setAnalyses)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(fetchRecords, []);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete the analysis for "${name}"?`)) return;
    setDeletingId(id);
    try {
      await deleteAnalysis(id);
      setAnalyses((prev) => prev.filter((a) => a.id !== id));
    } catch {
      alert('Failed to delete analysis record.');
    } finally {
      setDeletingId(null);
    }
  };

  const filtered = analyses.filter(
    (a) =>
      a.company_name?.toLowerCase().includes(search.toLowerCase()) ||
      a.website_url?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl lg:text-2xl font-bold text-slate-900 tracking-tight">
            Analysis History & Dossier Repository
          </h1>
          <p className="text-xs lg:text-sm text-slate-500 mt-1">
            Browse, inspect, and export all previously compiled competitive intelligence dossiers.
          </p>
        </div>
        <Link
          to="/analyze"
          className="inline-flex items-center gap-2 bg-blue-900 hover:bg-blue-800 text-white px-4 py-2.5 rounded-lg text-xs font-semibold shadow-xs transition-colors self-start"
        >
          <PlusCircle className="w-4 h-4" />
          New Analysis
        </Link>
      </div>

      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by company name or website domain..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-xs text-slate-800 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 outline-none shadow-xs"
        />
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="w-8 h-8 text-blue-900 animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white border border-slate-200/80 rounded-xl p-12 text-center text-slate-400 text-xs shadow-xs">
          <FileText className="w-10 h-10 mx-auto mb-2 text-slate-300" />
          <p className="font-semibold text-slate-600">
            {search ? 'No matching competitor records found.' : 'No analyses generated yet.'}
          </p>
          <p className="mt-1">
            {search
              ? 'Try clearing the search term.'
              : 'Run your first analysis to populate the repository.'}
          </p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200/80 rounded-xl shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/70 text-slate-500 font-semibold uppercase text-[10px]">
                  <th className="text-left px-5 py-3 w-12">#</th>
                  <th className="text-left px-5 py-3">Competitor</th>
                  <th className="text-left px-5 py-3 hidden md:table-cell">Target Website</th>
                  <th className="text-left px-5 py-3">Intelligence Engine</th>
                  <th className="text-left px-5 py-3">Timestamp</th>
                  <th className="text-right px-5 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {filtered.map((item, idx) => (
                  <tr key={item.id} className="hover:bg-slate-50/40">
                    <td className="px-5 py-3.5 text-slate-400 font-mono text-[11px]">{idx + 1}</td>
                    <td className="px-5 py-3.5 font-bold text-slate-900">{item.company_name}</td>
                    <td className="px-5 py-3.5 text-slate-500 hidden md:table-cell max-w-xs truncate">
                      {item.website_url}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-blue-800 border border-blue-200">
                        {item.engine_used || 'Extractive NLP'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-slate-500 whitespace-nowrap">
                      {item.timestamp}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Link
                          to={`/report/${item.id}`}
                          className="p-1.5 rounded-lg hover:bg-blue-50 text-slate-500 hover:text-blue-700 transition-colors"
                          title="View dossier"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                        <a
                          href={getPdfUrl(item.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 rounded-lg hover:bg-emerald-50 text-slate-500 hover:text-emerald-700 transition-colors"
                          title="Download PDF"
                        >
                          <Download className="w-4 h-4" />
                        </a>
                        <button
                          onClick={() => handleDelete(item.id, item.company_name)}
                          disabled={deletingId === item.id}
                          className="p-1.5 rounded-lg hover:bg-red-50 text-slate-500 hover:text-red-700 transition-colors disabled:opacity-50"
                          title="Delete record"
                        >
                          {deletingId === item.id ? (
                            <Loader2 className="w-4 h-4 animate-spin text-red-600" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-5 py-3 border-t border-slate-100 bg-slate-50/50 text-[11px] text-slate-400">
            Showing {filtered.length} of {analyses.length} total recorded dossiers
          </div>
        </div>
      )}
    </div>
  );
}
