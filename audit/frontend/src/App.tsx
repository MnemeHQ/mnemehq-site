import { Routes, Route, Navigate } from 'react-router-dom';
import { NewAuditPage } from './pages/NewAuditPage';
import { AuditOverviewPage } from './pages/AuditOverviewPage';
import { DecisionDetailPage } from './pages/DecisionDetailPage';
import { GovernanceGapsPage } from './pages/GovernanceGapsPage';
import { ProjectPage } from './pages/ProjectPage';
import { ComparisonPage } from './pages/ComparisonPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<NewAuditPage />} />
      <Route path="/audit" element={<Navigate to="/" replace />} />
      <Route path="/audit/" element={<Navigate to="/" replace />} />
      <Route path="/audit/:id" element={<AuditOverviewPage />} />
      <Route path="/audit/:id/decisions/:decisionId" element={<DecisionDetailPage />} />
      <Route path="/audit/:id/gaps" element={<GovernanceGapsPage />} />
      <Route path="/project/:projectId" element={<ProjectPage />} />
      <Route path="/project/:projectId/compare" element={<ComparisonPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;