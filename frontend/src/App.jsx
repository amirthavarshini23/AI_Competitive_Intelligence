import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import NewAnalysis from './pages/NewAnalysis';
import AnalysisReport from './pages/AnalysisReport';
import CompetitorComparison from './pages/CompetitorComparison';
import MarketIntelligence from './pages/MarketIntelligence';
import SemanticSearch from './pages/SemanticSearch';
import TrendAnalysis from './pages/TrendAnalysis';
import NewsIntelligence from './pages/NewsIntelligence';
import CompetitorMonitoring from './pages/CompetitorMonitoring';
import History from './pages/History';
import Settings from './pages/Settings';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analyze" element={<NewAnalysis />} />
        <Route path="/report/:id" element={<AnalysisReport />} />
        <Route path="/compare" element={<CompetitorComparison />} />
        <Route path="/market" element={<MarketIntelligence />} />
        <Route path="/search" element={<SemanticSearch />} />
        <Route path="/trends" element={<TrendAnalysis />} />
        <Route path="/news" element={<NewsIntelligence />} />
        <Route path="/monitoring" element={<CompetitorMonitoring />} />
        <Route path="/history" element={<History />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
