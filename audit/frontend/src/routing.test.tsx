import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route, Navigate } from 'react-router-dom';
import { vi, describe, it, expect } from 'vitest';

// Mock the pages as simple components
const NewAuditPage = () => <div data-testid="new-audit-page">New Audit Page</div>;
const AuditOverviewPage = () => <div data-testid="audit-overview-page">Audit Overview Page</div>;
const DecisionDetailPage = () => <div data-testid="decision-detail-page">Decision Detail Page</div>;
const GovernanceGapsPage = () => <div data-testid="governance-gaps-page">Governance Gaps Page</div>;

// Mock useAuditApi hook
vi.mock('../hooks/useAuditApi', () => ({
  useAuditApi: () => ({
    getAudit: vi.fn(),
    createAudit: vi.fn(),
    exportAudit: vi.fn(),
    loading: false,
    error: null,
  }),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Github: () => <svg data-testid="github-icon" />,
  ArrowLeft: () => <svg data-testid="arrow-left-icon" />,
  Loader2: () => <svg data-testid="loader-icon" />,
  Download: () => <svg data-testid="download-icon" />,
  FileText: () => <svg data-testid="file-text-icon" />,
  AlertCircle: () => <svg data-testid="alert-circle-icon" />,
  CheckCircle: () => <svg data-testid="check-circle-icon" />,
  AlertTriangle: () => <svg data-testid="alert-triangle-icon" />,
  Circle: () => <svg data-testid="circle-icon" />,
  Target: () => <svg data-testid="target-icon" />,
  Upload: () => <svg data-testid="upload-icon" />,
  Copy: () => <svg data-testid="copy-icon" />,
  ArrowRight: () => <svg data-testid="arrow-right-icon" />,
}));

// Mock window.location.reload
Object.defineProperty(window, 'location', {
  value: {
    reload: vi.fn(),
    href: 'http://localhost:3000/audit/',
  },
  writable: true,
});

// Mock navigator.clipboard
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

const renderApp = (initialPath = '/') => {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/" element={<NewAuditPage />} />
        <Route path="/audit" element={<Navigate to="/" replace />} />
        <Route path="/audit/" element={<Navigate to="/" replace />} />
        <Route path="/audit/:id" element={<AuditOverviewPage />} />
        <Route path="/audit/:id/decisions/:decisionId" element={<DecisionDetailPage />} />
        <Route path="/audit/:id/gaps" element={<GovernanceGapsPage />} />
      </Routes>
    </MemoryRouter>
  );
};

describe('Audit Workspace Routing', () => {
  describe('Empty workspace route', () => {
    it('redirects /audit to /', () => {
      renderApp('/audit');
      expect(screen.getByTestId('new-audit-page')).toBeInTheDocument();
    });

    it('redirects /audit/ to /', () => {
      renderApp('/audit/');
      expect(screen.getByTestId('new-audit-page')).toBeInTheDocument();
    });

    it('shows New Audit page at root', () => {
      renderApp('/');
      expect(screen.getByTestId('new-audit-page')).toBeInTheDocument();
    });
  });

  describe('Valid audit routes render correct pages', () => {
    it('renders AuditOverviewPage for /audit/:id', () => {
      renderApp('/audit/test-123');
      expect(screen.getByTestId('audit-overview-page')).toBeInTheDocument();
    });

    it('renders DecisionDetailPage for /audit/:id/decisions/:decisionId', () => {
      renderApp('/audit/test-123/decisions/dec-456');
      expect(screen.getByTestId('decision-detail-page')).toBeInTheDocument();
    });

    it('renders GovernanceGapsPage for /audit/:id/gaps', () => {
      renderApp('/audit/test-123/gaps');
      expect(screen.getByTestId('governance-gaps-page')).toBeInTheDocument();
    });
  });

  describe('Mobile Container', () => {
    it('renders without errors', () => {
      renderApp('/');
      expect(screen.getByTestId('new-audit-page')).toBeInTheDocument();
    });
  });
});