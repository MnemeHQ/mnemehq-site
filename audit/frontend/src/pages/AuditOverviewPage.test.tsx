import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuditOverviewPage } from './AuditOverviewPage';
import { auditFixture, decisionFixture } from '../test/protectionFixture';

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

const audit = auditFixture({
  audit_id: '424e1795',
  repository: 'https://github.com/adr/gadr',
  summary: {
    decisions_discovered: 2, protection_relevant: 2, protected_count: 0,
    mneme_ready_count: 0, requires_modelling_count: 2, guidance_count: 0,
    current_protection: 0, identified_mneme_potential: 0,
    sources: ['docs/adr/0000.md', 'docs/adr/0001.md'],
    by_category: {
      architecture_decision: 2,
      agent_instruction: 0,
      config_evidence: 0,
    },
  },
  decisions: [
    decisionFixture({
      id: 'decision-1',
      title: 'Use Markdown ADRs',
      summary: 'Record decisions in Markdown.',
      requirement: 'Architectural decisions should use Markdown.',
      source: { file: 'docs/adr/0000.md', lines: '1-20' },
      protection_classification: 'Requires modelling',
      category: 'architecture_decision',
    }),
    decisionFixture({
      id: 'decision-2',
      title: 'Use GADR naming',
      summary: 'Use the GADR name.',
      requirement: 'Generalized records should be called GADRs.',
      source: { file: 'docs/adr/0001.md', lines: '1-12' },
      protection_classification: 'Requires modelling',
      category: 'architecture_decision',
    }),
  ],
});

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
    ['Protection gaps', 'gaps'],
    ['Sources', 'sources'],
    ['Setup', 'setup'],
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

    expect(screen.queryByLabelText('Protection Classification')).not.toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Audit summary' })).not.toBeInTheDocument();
    expect(screen.getByText('DECISIONS IDENTIFIED')).toBeInTheDocument();
    expect(screen.getByText('Architecture decisions')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Protection Gaps' })).toBeInTheDocument();
    expect(screen.getAllByText(/Needs architectural modelling \(scope/)).toHaveLength(2);
    expect(screen.getAllByText(/Recommendation:/)).toHaveLength(2);
    expect(screen.getByText('How to read this audit')).toBeInTheDocument();
    expect(screen.getByText('Protection Decisions')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Request a pilot' })).toHaveAttribute('href', expect.stringContaining('https://mnemehq.com/pilot/?source=architecture-audit'));
  });

  it('offers setup before the downstream pilot without promising automatic enforcement', () => {
    renderOverview();
    const install = screen.getByRole('link', { name: 'Install Mneme' });
    const pilot = screen.getByRole('link', { name: 'Request a pilot' });
    expect(install).toHaveAttribute('href', '/docs/#quickstart');
    expect(install).toHaveClass('btn-primary');
    expect(pilot).toHaveClass('btn-ghost');
    expect(install.compareDocumentPosition(pilot) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(screen.getByText(/Installing Mneme does not automatically enable enforcement or activate the proposed guardrails/)).toBeInTheDocument();
    expect(screen.getByText(/After setup, want help/)).toBeInTheDocument();
  });

  it('opens a bounded, accessible explanation from a metric info control', () => {
    renderOverview();

    const trigger = screen.getByRole('button', { name: 'More information: PROTECTED' });
    fireEvent.mouseEnter(trigger);

    expect(screen.getByRole('tooltip')).toHaveTextContent('deterministic Mneme enforcement evidence');
    expect(trigger).toHaveAttribute('aria-expanded', 'true');

    fireEvent.mouseLeave(trigger);
    fireEvent.click(trigger);
    expect(screen.getByRole('tooltip')).toHaveTextContent('deterministic Mneme enforcement evidence');
  });
});
