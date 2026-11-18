import { useState, useEffect } from 'react';
import {
  Key,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Save,
  Cpu,
  Database,
  Radio,
  Clock,
  HelpCircle,
  ExternalLink,
  Loader2,
} from 'lucide-react';
import {
  getSystemStatus,
  getSettings,
  updateSettings,
  getStoredConfig,
  saveStoredConfig,
} from '../api/client';

export default function Settings() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  // Stored form state
  const stored = getStoredConfig();
  const [geminiKey, setGeminiKey] = useState(stored.gemini_key);
  const [newsKey, setNewsKey] = useState(stored.news_key);
  const [ollamaModel, setOllamaModel] = useState(stored.ollama_model);
  const [useOllama, setUseOllama] = useState(stored.use_ollama);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getSystemStatus()
      .then(setSystemStatus)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = () => {
    saveStoredConfig({
      gemini_key: geminiKey.trim(),
      news_key: newsKey.trim(),
      ollama_model: ollamaModel.trim(),
      use_ollama: useOllama,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl lg:text-2xl font-bold text-slate-900 tracking-tight">
          System Status & Engine Configuration
        </h1>
        <p className="text-xs lg:text-sm text-slate-500 mt-1">
          Monitor offline AI engines, database connectivity, and configure runtime models.
        </p>
      </div>

      {/* System Health Overview Card */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs space-y-4">
        <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
          Runtime Engine & System Health
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {/* Backend API */}
          <div className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/70 text-xs space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-700">FastAPI Backend</span>
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                Connected :8000
              </span>
            </div>
            <p className="text-[11px] text-slate-500">REST API & APScheduler daemon</p>
          </div>

          {/* Ollama Local LLM */}
          <div className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/70 text-xs space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-700">Local Ollama LLM</span>
              {systemStatus?.ollama_running ? (
                <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  Online :11434
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                  Offline (Extractive Fallback)
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-500">
              {systemStatus?.ollama_models?.length > 0
                ? `${systemStatus.ollama_models.length} model(s) installed`
                : 'Using Local NLP Engine'}
            </p>
          </div>

          {/* SQLite DB */}
          <div className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/70 text-xs space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-700">SQLite Database</span>
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                Healthy
              </span>
            </div>
            <p className="text-[11px] text-slate-500">Persistent local storage</p>
          </div>
        </div>

        {/* Ollama Instructions if Offline */}
        {!systemStatus?.ollama_running && (
          <div className="p-3.5 rounded-lg bg-amber-50/70 border border-amber-200 text-xs text-amber-900 space-y-1.5">
            <div className="flex items-center gap-2 font-bold">
              <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
              Ollama Service Not Detected on Port 11434
            </div>
            <p className="text-[11px] text-amber-800 leading-relaxed">
              The application will automatically use its internal <strong>Extractive NLP and Rule-Based engine</strong> to perform analyses without interruption.
              To enable local neural LLM generation:
            </p>
            <div className="bg-white/80 p-2 rounded border border-amber-200 font-mono text-[11px] text-slate-800">
              ollama run qwen2.5:3b
            </div>
          </div>
        )}
      </div>

      {/* Model & AI Settings Form */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs space-y-5">
        <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
          AI & NLP Engine Configuration
        </h2>

        {/* Enable Ollama Toggle */}
        <div className="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
          <div>
            <span className="font-semibold text-slate-800">Use Local Ollama LLM</span>
            <p className="text-slate-400 text-[11px]">
              When enabled and reachable, Ollama will synthesize insights. When offline, falls back to deterministic NLP.
            </p>
          </div>
          <input
            type="checkbox"
            checked={useOllama}
            onChange={(e) => setUseOllama(e.target.checked)}
            className="w-4 h-4 accent-blue-900 cursor-pointer"
          />
        </div>

        {/* Model Selection */}
        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
            Configured Ollama Model
          </label>
          <input
            type="text"
            value={ollamaModel}
            onChange={(e) => setOllamaModel(e.target.value)}
            placeholder="e.g. qwen2.5:3b, llama3.2:3b, mistral"
            className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-xs text-slate-800 focus:ring-2 focus:ring-blue-600 outline-none"
          />
          <p className="text-[11px] text-slate-400 mt-1">
            Installed on system:{' '}
            {systemStatus?.ollama_models?.length > 0
              ? systemStatus.ollama_models.join(', ')
              : 'None currently running'}
          </p>
        </div>

        <hr className="border-slate-100" />

        {/* Optional External API Keys */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Optional External API Keys
            </h3>
            <span className="text-[10px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
              Zero Mandatory Keys
            </span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Google Gemini API Key (Optional)
            </label>
            <input
              type="password"
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              placeholder="Optional. Stored locally in your browser only."
              className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-xs text-slate-800 focus:ring-2 focus:ring-blue-600 outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              NewsAPI Key (Optional)
            </label>
            <input
              type="password"
              value={newsKey}
              onChange={(e) => setNewsKey(e.target.value)}
              placeholder="Optional. Public RSS is used automatically when omitted."
              className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-xs text-slate-800 focus:ring-2 focus:ring-blue-600 outline-none"
            />
          </div>
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          className="w-full flex items-center justify-center gap-2 bg-blue-900 hover:bg-blue-800 text-white py-2.5 rounded-lg text-xs font-bold shadow-xs transition-all"
        >
          {saved ? (
            <>
              <CheckCircle2 className="w-4 h-4" />
              Settings Saved to Local Storage!
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Configuration
            </>
          )}
        </button>
      </div>
    </div>
  );
}
