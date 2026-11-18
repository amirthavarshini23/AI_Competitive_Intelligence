import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  PlusCircle,
  Scale,
  LineChart,
  Search,
  TrendingUp,
  Newspaper,
  Activity,
  History as HistoryIcon,
  Settings,
  ShieldCheck,
  Menu,
  X,
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { getSystemStatus } from '../api/client';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/analyze', icon: PlusCircle, label: 'New Analysis' },
  { to: '/compare', icon: Scale, label: 'Competitor Comparison' },
  { to: '/market', icon: LineChart, label: 'Market Intelligence' },
  { to: '/search', icon: Search, label: 'Semantic Search' },
  { to: '/trends', icon: TrendingUp, label: 'Trend Analysis' },
  { to: '/news', icon: Newspaper, label: 'News Intelligence' },
  { to: '/monitoring', icon: Activity, label: 'Competitor Monitoring' },
  { to: '/history', icon: HistoryIcon, label: 'Analysis History' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    getSystemStatus()
      .then(setSystemStatus)
      .catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/30 backdrop-blur-xs z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-slate-200
          transform transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          flex flex-col shadow-xs
        `}
      >
        {/* Brand header */}
        <div className="h-16 flex items-center gap-3 px-5 border-b border-slate-100">
          <div className="w-9 h-9 rounded-lg bg-blue-900 flex items-center justify-center shadow-xs">
            <ShieldCheck className="w-5 h-5 text-blue-200" />
          </div>
          <div className="min-w-0">
            <h1 className="text-sm font-bold text-slate-900 tracking-tight leading-none">
              STRATINTEL AI
            </h1>
            <p className="text-[10.5px] font-medium text-slate-400 mt-1 uppercase tracking-wider">
              Market Strategy
            </p>
          </div>
          <button
            className="ml-auto lg:hidden text-slate-400 hover:text-slate-600 p-1"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 py-3 px-3 space-y-0.5 overflow-y-auto">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all duration-150 ${
                  isActive
                    ? 'bg-blue-900 text-white shadow-xs'
                    : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="truncate">{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Engine status footer */}
        <div className="p-3.5 border-t border-slate-100 bg-slate-50/60">
          <div className="bg-white border border-slate-200/80 rounded-lg p-2.5 text-xs">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                AI Engine
              </span>
              <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Active
              </span>
            </div>
            <p className="font-semibold text-slate-800 text-[11px] truncate">
              {systemStatus?.ollama_running
                ? `Ollama: ${systemStatus.selected_model || 'Local LLM'}`
                : 'Local NLP & RAG'}
            </p>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-slate-200/80 flex items-center justify-between px-5 lg:px-8 sticky top-0 z-20 shadow-2xs">
          <div className="flex items-center gap-3">
            <button
              className="lg:hidden p-1.5 rounded-lg hover:bg-slate-100 text-slate-600"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </button>
            <h2 className="text-sm font-bold text-slate-800 tracking-tight hidden sm:block">
              Competitive Intelligence & Market Strategy Platform
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-medium text-slate-500 bg-slate-100 border border-slate-200 px-2.5 py-1 rounded-full">
              Academic Presentation Demo
            </span>
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-7 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
