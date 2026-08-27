import { Routes, Route } from 'react-router-dom';
import { NewAuditPage } from './pages/NewAuditPage';
import { AuditOverviewPage } from './pages/AuditOverviewPage';
import { DecisionDetailPage } from './pages/DecisionDetailPage';
import { GovernanceGapsPage } from './pages/GovernanceGapsPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<NewAuditPage />} />
      <Route path="/audit/:id" element={<AuditOverviewPage />} />
      <Route path="/audit/:id/decisions/:decisionId" element={<DecisionDetailPage />} />
      <Route path="/audit/:id/gaps" element={<GovernanceGapsPage />} />
    </Routes>
  );
}

export default App;