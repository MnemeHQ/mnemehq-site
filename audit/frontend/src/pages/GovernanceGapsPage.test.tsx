import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { GovernanceGapsPage } from './GovernanceGapsPage';
import { auditFixture, decisionFixture } from '../test/protectionFixture';

const { getAudit } = vi.hoisted(() => ({ getAudit: vi.fn() }));

vi.mock('../hooks/useAuditApi', () => ({
  useAuditApi: () => ({ getAudit, loading: false, error: null }),
}));

describe('GovernanceGapsPage', () => {
  it('explains gaps and links the action to the matching governance item', async () => {
    getAudit.mockResolvedValue({
      success: true,
      data: auditFixture({
        summary: { ...auditFixture().summary, protection_relevant: 1, requires_modelling_count: 1, guidance_count: 0 },
        decisions: [decisionFixture({ protection_classification: 'Requires modelling' })],
      }),
    });

    render(
      <MemoryRouter initialEntries={['/audit/audit-1/gaps']}>
        <Routes>
          <Route path="/audit/:id/gaps" element={<GovernanceGapsPage />} />
          <Route path="/audit/:id/decisions/:decisionId" element={<div>Decision details destination</div>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText('Why it is a gap')).toBeInTheDocument();
    expect(screen.getByText(/Model the decision: define explicit applicability/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('link', { name: 'Review governance item: Project Config: pyproject.toml' }));
    expect(screen.getByText('Decision details destination')).toBeInTheDocument();
  });
});
