import axios from 'axios';

const API_BASE = '/api';
const api = axios.create({ baseURL: API_BASE });

// ---- Dashboard & System ----
export async function getDashboardStats() {
  const res = await api.get('/dashboard/stats');
  return res.data;
}

export async function getSystemStatus() {
  const res = await api.get('/system/status');
  return res.data;
}

// ---- Analysis Pipeline ----
export async function runAnalysis(payload) {
  const res = await api.post('/analyze', payload);
  return res.data;
}

export async function getAnalyses() {
  const res = await api.get('/analyses');
  return res.data;
}

export async function getAnalysisDetails(id) {
  const res = await api.get(`/analyses/${id}`);
  return res.data;
}

export async function deleteAnalysis(id) {
  const res = await api.delete(`/analyses/${id}`);
  return res.data;
}

export function getPdfUrl(id) {
  return `${API_BASE}/analyses/${id}/pdf`;
}

// ---- Competitor Comparison ----
export async function getAvailableCompetitors() {
  const res = await api.get('/compare/competitors');
  return res.data;
}

export async function compareCompetitors(competitorIds) {
  const res = await api.post('/compare', { competitor_ids: competitorIds });
  return res.data;
}

// ---- Semantic Search / RAG ----
export async function searchSemantic(query, competitorId = null, topK = 5) {
  const res = await api.post('/search/semantic', {
    query,
    competitor_id: competitorId ? parseInt(competitorId) : null,
    top_k: topK
  });
  return res.data;
}

// ---- Market Intelligence & SWOT ----
export async function getMarketOverview() {
  const res = await api.get('/market/overview');
  return res.data;
}

export async function getSwot(competitorId) {
  const res = await api.get(`/swot/${competitorId}`);
  return res.data;
}

// ---- Trends ----
export async function getTrendCompetitors() {
  const res = await api.get('/trends/competitors');
  return res.data;
}

export async function getCompetitorTrends(competitorId) {
  const res = await api.get(`/trends/${competitorId}`);
  return res.data;
}

// ---- News Intelligence ----
export async function getNewsArticles(params = {}) {
  const res = await api.get('/news', { params });
  return res.data;
}

export async function getNewsStats() {
  const res = await api.get('/news/stats');
  return res.data;
}

// ---- Competitor Monitoring ----
export async function getMonitoringJobs() {
  const res = await api.get('/monitoring');
  return res.data;
}

export async function addMonitoringJob(competitorId, intervalMinutes = 60) {
  const res = await api.post('/monitoring/add', {
    competitor_id: competitorId,
    check_interval_minutes: intervalMinutes
  });
  return res.data;
}

export async function checkCompetitorNow(competitorId) {
  const res = await api.post(`/monitoring/check/${competitorId}`);
  return res.data;
}

export async function getDetectedChanges() {
  const res = await api.get('/monitoring/changes');
  return res.data;
}

// ---- Settings ----
export async function getSettings() {
  const res = await api.get('/settings');
  return res.data;
}

export async function updateSettings(config) {
  const res = await api.post('/settings', config);
  return res.data;
}

// ---- LocalStorage Keys Helper ----
export function getStoredConfig() {
  return {
    gemini_key: localStorage.getItem('ci_gemini_key') || '',
    news_key: localStorage.getItem('ci_news_key') || '',
    ollama_model: localStorage.getItem('ci_ollama_model') || 'qwen2.5:3b',
    use_ollama: localStorage.getItem('ci_use_ollama') !== 'false',
  };
}

export function saveStoredConfig(config) {
  if (config.gemini_key !== undefined) localStorage.setItem('ci_gemini_key', config.gemini_key);
  if (config.news_key !== undefined) localStorage.setItem('ci_news_key', config.news_key);
  if (config.ollama_model !== undefined) localStorage.setItem('ci_ollama_model', config.ollama_model);
  if (config.use_ollama !== undefined) localStorage.setItem('ci_use_ollama', String(config.use_ollama));
}
