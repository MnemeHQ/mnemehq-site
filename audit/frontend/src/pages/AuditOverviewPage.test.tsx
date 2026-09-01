import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuditOverviewPage } from './AuditOverviewPage';
import type { AuditResult } from '../types/audit';

const { getAudit } = vi.hoisted(() => ({
  getAudit: vi.fn(),
}));

vi.mock('../hooks/useAuditApi', () => ({
  useAuditApi: () => ({
    getAudit,
    exportAudit: vi.fn(),
    error: null,
  }),
}));

const audit: AuditResult = {
  id: '424e1795',
  repository: 'https://github.com/adr/gadr',
  createdAt: '2026-09-01T00:00:00Z',
  summary: {
    totalDecisions: 2,
    enforceable: 0,
    partial: 0,
    guidance: 2,
    coverage: 0,
    sources: ['docs/adr/0000.md', 'docs/adr/0001.md'],
    byCategory: {
      architecture_decision: 2,
      agent_instruction: 0,
      config_evidence: 0,
    },
  },
  decisions: [
    {
      id: 'decision-1',
      title: 'Use Markdown ADRs',
      summary: 'Record decisions in Markdown.',
      requirement: 'Architectural decisions should use Markdown.',
      source: { file: 'docs/adr/0000.md', lines: '1-20' },
      governability: 'guidance',
      appliesTo: [],
      proposedRule: null,
      confidence: 0.9,
    },
    {
      id: 'decision-2',
      title: 'Use GADR naming',
      summary: 'Use the GADR name.',
      requirement: 'Generalized records should be called GADRs.',
      source: { file: 'docs/adr/0001.md', lines: '1-12' },
      governability: 'guidance',
      appliesTo: [],
      proposedRule: null,
      confidence: 0.9,
    },
  ],
  gaps: [
    {
      decision: 'Use Markdown ADRs',
      reason: 'Missing explicit applicability.',
      suggestedNextStep: 'Add the paths this decision applies to.',
    },
    {
      decision: 'Use GADR naming',
      reason: 'Missing explicit applicability.',
      suggestedNextStep: 'Add the paths this decision applies to.',
    },
  ],
};

function renderOverview() {
  return render(
    <MemoryRouter
      initialEntries={[{ pathname: '/audit/424e1795', state: { audit } }]}
    >
      <Routes>
        <Route path="/audit/:id" element={<AuditOverviewPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('AuditOverviewPage section navigation', () => {
  beforeEach(() => {
    getAudit.mockReset();
    vi.spyOn(window, 'scrollTo').mockImplementation(() => undefined);
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it.each([
    ['Coverage', 'coverage'],
    ['Sources', 'sources'],
  ])('scrolls to and activates the %s section', (label, sectionId) => {
    renderOverview();

    const section = document.getElementById(sectionId);
    expect(section).not.toBeNull();
    vi.spyOn(section!, 'getBoundingClientRect').mockReturnValue({
      top: 1200,
      bottom: 1400,
      left: 0,
      right: 640,
      width: 640,
      height: 200,
      x: 0,
      y: 1200,
      toJSON: () => ({}),
    });

    const button = screen.getByRole('button', { name: label });
    fireEvent.click(button);

    expect(window.scrollTo).toHaveBeenCalledWith({
      top: 1128,
      behavior: 'smooth',
    });
    expect(button).toHaveAttribute('aria-current', 'location');
  });

  it('uses the reduced small-audit layout and shows gaps inline', () => {
    renderOverview();

    expect(screen.queryByLabelText('Filter by governability')).not.toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Audit summary' })).not.toBeInTheDocument();
    expect(screen.getByText('GOVERNANCE ITEMS')).toBeInTheDocument();
    expect(screen.getByText('Architecture decisions')).toBeInTheDocument();
    expect(screen.getByText('2 governance gaps')).toBeInTheDocument();
    expect(screen.getAllByText('Missing explicit applicability.')).toHaveLength(2);
    expect(screen.getAllByText(/Recommendation:/)).toHaveLength(2);
    expect(screen.getByText('How to read this audit')).toBeInTheDocument();
    expect(screen.getByText('Governance Items')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Request a pilot' })).toHaveAttribute('href', '/pilot/');
  });

  it('opens a bounded, accessible explanation from a metric info control', () => {
    renderOverview();

    const trigger = screen.getByRole('button', { name: 'More information: ENFORCEABLE NOW' });
    fireEvent.mouseEnter(trigger);

    expect(screen.getByRole('tooltip')).toHaveTextContent('deterministic control');
    expect(trigger).toHaveAttribute('aria-expanded', 'true');

    fireEvent.mouseLeave(trigger);
    fireEvent.click(trigger);
    expect(screen.getByRole('tooltip')).toHaveTextContent('deterministic control');
  });
});
