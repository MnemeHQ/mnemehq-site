import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { DecisionDetailPage } from './DecisionDetailPage';

const { getAudit } = vi.hoisted(() => ({ getAudit: vi.fn() }));

vi.mock('../hooks/useAuditApi', () => ({
  useAuditApi: () => ({ getAudit }),
}));

describe('DecisionDetailPage', () => {
  it('turns raw configuration evidence into an explained finding with recommendations', async () => {
    getAudit.mockResolvedValue({
      success: true,
      data: {
        id: 'audit-1',
        repository: 'https://github.com/example/repo',
        createdAt: '2026-09-01T00:00:00Z',
        summary: { totalDecisions: 1, enforceable: 0, partial: 0, guidance: 1, coverage: 0, sources: [] },
        gaps: [{ decision: 'Project Config: pyproject.toml', reason: 'Missing constraint.', suggestedNextStep: 'Define a constraint.' }],
        decisions: [{
          id: 'decision-1',
          title: 'Project Config: pyproject.toml',
          summary: 'Python project configuration with dependency and test settings.',
          requirement: '[project]\nname = "example"',
          source: { file: 'pyproject.toml', lines: '1-20' },
          governability: 'guidance',
          appliesTo: [],
          proposedRule: null,
          confidence: 0.4,
          category: 'config_evidence',
        }],
      },
    });

    render(
      <MemoryRouter initialEntries={['/audit/audit-1/decisions/decision-1']}>
        <Routes>
          <Route path="/audit/:id/decisions/:decisionId" element={<DecisionDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: 'What this means' })).toBeInTheDocument();
    expect(screen.getAllByText(/Mneme found project configuration in pyproject.toml/)).toHaveLength(2);
    expect(screen.getByText('No deterministic rule yet')).toBeInTheDocument();
    expect(screen.getByText('View evidence')).toBeInTheDocument();
    expect(screen.getByText('State a machine-testable constraint')).toBeInTheDocument();
    expect(screen.getByText('Define where this applies')).toBeInTheDocument();
    const pilotLink = screen.getByRole('link', { name: 'Request a pilot' });
    expect(pilotLink).toHaveAttribute('href', expect.stringContaining('https://mnemehq.com/pilot/?source=architecture-audit'));
    pilotLink.addEventListener('click', (event) => event.preventDefault(), { once: true });
    fireEvent.click(pilotLink);
    expect(JSON.parse(sessionStorage.getItem('mneme_pilot_context') || '{}')).toMatchObject({
      auditId: 'audit-1',
      selectedDecisionId: 'decision-1',
    });
  });
});
