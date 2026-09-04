import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { DecisionDetailPage } from './DecisionDetailPage';
import { auditFixture } from '../test/protectionFixture';

const { getAudit } = vi.hoisted(() => ({ getAudit: vi.fn() }));

vi.mock('../hooks/useAuditApi', () => ({
  useAuditApi: () => ({ getAudit }),
}));

describe('DecisionDetailPage', () => {
  it('turns raw configuration evidence into an explained finding with recommendations', async () => {
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
});
