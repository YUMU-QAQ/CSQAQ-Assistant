import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import ItemSearch from './pages/ItemSearch';
import ItemDetail from './pages/ItemDetail';
import Rankings from './pages/Rankings';
import Watchlist from './pages/Watchlist';
import Portfolio from './pages/Portfolio';
import Alerts from './pages/Alerts';
import Arbitrage from './pages/Arbitrage';
import Cases from './pages/Cases';
import AIAssistant from './pages/AIAssistant';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/items" element={<ItemSearch />} />
          <Route path="/items/:goodId" element={<ItemDetail />} />
          <Route path="/rankings" element={<Rankings />} />
          <Route path="/watchlist" element={<Watchlist />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/arbitrage" element={<Arbitrage />} />
          <Route path="/cases" element={<Cases />} />
          <Route path="/ai" element={<AIAssistant />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
