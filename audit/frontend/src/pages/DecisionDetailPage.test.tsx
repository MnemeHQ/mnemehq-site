import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { DecisionDetailPage } from './DecisionDetailPage';
import { auditFixture } from '../test/protectionFixture';

const { getAudit, track } = vi.hoisted(() => ({ getAudit: vi.fn(), track: vi.fn() }));

vi.mock('../hooks/useAuditApi', () => ({
  useAuditApi: () => ({ getAudit }),
}));
vi.mock('../analytics', async importActual => ({
  ...(await importActual<typeof import('../analytics')>()),
  track,
}));

describe('DecisionDetailPage', () => {
  it('turns raw configuration evidence into an explained finding with recommendations', async () => {
    track.mockReset();
    getAudit.mockResolvedValue({
      success: true,
      data: auditFixture(),
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
    expect(screen.getByText(/Deterministic enforcement is not appropriate/)).toBeInTheDocument();
    expect(screen.getByText('View evidence')).toBeInTheDocument();
    expect(screen.getByText('Review this guidance with the decision owner')).toBeInTheDocument();
    expect(screen.queryByText('State a machine-testable constraint')).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Install Mneme' })).toHaveAttribute('href', '/docs/#quickstart');
    const pilotLink = screen.getByRole('link', { name: 'Request a pilot' });
    expect(pilotLink).toHaveAttribute('href', expect.stringContaining('https://mnemehq.com/pilot/?source=architecture-audit'));
    pilotLink.addEventListener('click', (event) => event.preventDefault(), { once: true });
    fireEvent.click(pilotLink);
    expect(JSON.parse(sessionStorage.getItem('mneme_pilot_context') || '{}')).toMatchObject({
      auditId: 'audit-1',
      selectedDecisionId: 'decision-1',
    });
  });

  it('separates safe detail-view and successful rule-copy events', async () => {
    track.mockReset();
    getAudit.mockResolvedValue({
      success: true,
      data: auditFixture({
        decisions: [auditFixture().decisions[0] && {
          ...auditFixture().decisions[0],
          protection_classification: 'Mneme-ready',
          evidence_confidence: 'high',
          proposed_rule: { type: 'FORBID_LITERAL', pattern: 'private-pattern', description: 'Safe rule' },
        }],
      }),
    });

    render(
      <MemoryRouter initialEntries={['/audit/audit-1/decisions/decision-1']}>
        <Routes>
          <Route path="/audit/:id/decisions/:decisionId" element={<DecisionDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    fireEvent.click(await screen.findByRole('button', { name: 'Copy rule' }));
    await waitFor(() => expect(track).toHaveBeenCalledWith('audit_rule_copy', expect.anything()));
    expect(track).toHaveBeenCalledWith('audit_decision_view', {
      protection_classification: 'Mneme-ready',
      evidence_confidence: 'high',
      has_proposed_rule: true,
      rule_type: 'FORBID_LITERAL',
    });
    expect(track).toHaveBeenCalledWith('audit_rule_copy', {
      protection_classification: 'Mneme-ready',
      evidence_confidence: 'high',
      has_proposed_rule: true,
      rule_type: 'FORBID_LITERAL',
    });
    expect(JSON.stringify(track.mock.calls)).not.toContain('private-pattern');
    expect(JSON.stringify(track.mock.calls)).not.toContain('decision-1');
  });
});
