import { render, screen } from '@testing-library/react';
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

    expect(await screen.findByRole('heading', { name: 'Detected evidence' })).toBeInTheDocument();
    expect(screen.getAllByText(/Mneme found project configuration in pyproject.toml/)).toHaveLength(2);
    expect(screen.getByText('State a machine-testable constraint')).toBeInTheDocument();
    expect(screen.getByText('Define where this applies')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Request a pilot' })).toHaveAttribute('href', '/pilot/');
  });
});
