import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { GovernanceGapsPage } from './GovernanceGapsPage';

const { getAudit } = vi.hoisted(() => ({ getAudit: vi.fn() }));

vi.mock('../hooks/useAuditApi', () => ({
  useAuditApi: () => ({ getAudit, loading: false, error: null }),
}));

describe('GovernanceGapsPage', () => {
  it('explains gaps and links the action to the matching governance item', async () => {
    getAudit.mockResolvedValue({
      success: true,
      data: {
        id: 'audit-1',
        repository: 'https://github.com/example/repo',
        createdAt: '2026-09-01T00:00:00Z',
        summary: { totalDecisions: 1, enforceable: 0, partial: 0, guidance: 1, coverage: 0, sources: [] },
        gaps: [{
          decision: 'Project Config: pyproject.toml',
          reason: 'No machine-testable constraint.',
          suggestedNextStep: 'Define a required dependency policy.',
        }],
        decisions: [{
          id: 'decision-1',
          title: 'Project Config: pyproject.toml',
          summary: 'Python project configuration.',
          requirement: '[project]',
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
      <MemoryRouter initialEntries={['/audit/audit-1/gaps']}>
        <Routes>
          <Route path="/audit/:id/gaps" element={<GovernanceGapsPage />} />
          <Route path="/audit/:id/decisions/:decisionId" element={<div>Decision details destination</div>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText('Why it is a gap')).toBeInTheDocument();
    expect(screen.getByText('Define a required dependency policy.')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('link', { name: 'Review governance item: Project Config: pyproject.toml' }));
    expect(screen.getByText('Decision details destination')).toBeInTheDocument();
  });
});
