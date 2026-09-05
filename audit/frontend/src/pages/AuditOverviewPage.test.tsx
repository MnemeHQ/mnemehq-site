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
    saveBaseline: vi.fn(),
    createProject: vi.fn(),
  }),
}));

const audit = auditFixture({
  audit_id: '424e1795',
  repository: 'https://github.com/adr/gadr',
  summary: {
    decisions_discovered: 41,
    protection_relevant: 3,
    protected_count: 1,
    mneme_ready_count: 1,
    requires_modelling_count: 1,
    guidance_count: 38,
    current_protection: 0.33,
    identified_mneme_potential: 0.66,
    sources: ['docs/adr/0000.md', 'docs/adr/0001.md', 'CLAUDE.md', 'AGENTS.md'],
    by_category: {
      architecture_decision: 3,
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
      protection_classification: 'Mneme-ready',
      category: 'architecture_decision',
    }),
    decisionFixture({
      id: 'decision-3',
      title: 'PostgreSQL for persistence',
      summary: 'Use PostgreSQL for all persistence.',
      requirement: 'All data persistence must use PostgreSQL.',
      source: { file: 'docs/adr/0002.md', lines: '1-15' },
      protection_classification: 'Protected',
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
    ['Decisions', 'decisions'],
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

  it('shows hero with protection score and bridge statement', () => {
    renderOverview();

    // 33% appears multiple times (hero + primary metrics) - use getAllByText
    expect(screen.getAllByText('33%').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('1 of 3 protection-relevant decisions protected')).toBeInTheDocument();
    expect(screen.getByText(/2 architectural decisions could be converted from guidance into enforceable protection/)).toBeInTheDocument();
  });

  it('shows simplified metrics: primary row and secondary row', () => {
    renderOverview();

    // Primary metrics - 33% appears multiple times, check it exists
    expect(screen.getAllByText('33%').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('41')).toBeInTheDocument(); // Decisions Discovered
    expect(screen.getByText('3')).toBeInTheDocument(); // Protection Relevant

    // Secondary metrics
    expect(screen.getByText('1')).toBeInTheDocument(); // Protected count
    expect(screen.getByText('2')).toBeInTheDocument(); // Ready to Protect count
    expect(screen.getByText('38')).toBeInTheDocument(); // Guidance Only count
  });

  it('shows expanded narrative for each section', () => {
    renderOverview();

    expect(screen.getByText('How to read this audit')).toBeInTheDocument();
    expect(screen.getByText('Protection Gaps')).toBeInTheDocument();
    expect(screen.getByText('Protection Decisions')).toBeInTheDocument();
    expect(screen.getByText('Sources Examined')).toBeInTheDocument();

    // How to read this audit narrative - use function matcher for text that may be split across elements
    expect(screen.getByText((content) => content.includes('Mneme identified 41 architectural decisions and constraints'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('3 decisions are suitable for deterministic protection'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('2 architectural decisions could be converted'))).toBeInTheDocument();

    // Protection Gaps narrative
    expect(screen.getByText((content) => content.includes('2 architectural decisions could be protected more explicitly'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('These decisions describe constraints that can be evaluated mechanically'))).toBeInTheDocument();

    // Protection Decisions narrative
    expect(screen.getByText((content) => content.includes('This is the decision-level evidence behind the Audit result'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('Protected'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('Ready to Protect'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('Guidance Only'))).toBeInTheDocument();

    // Sources Examined narrative
    expect(screen.getByText((content) => content.includes('Mneme looks for architectural intent across the repository'))).toBeInTheDocument();
  });

  it('shows Protection Gaps with human-readable leads', () => {
    renderOverview();

    // Gap cards should use human-readable leads - appears in gap section
    expect(screen.getAllByText('Use Markdown ADRs')).toHaveLength(2); // gap card + decision card
    expect(screen.getAllByText('Use GADR naming')).toHaveLength(2);

    // Should show badges with new label - multiple instances exist
    expect(screen.getAllByText('READY TO PROTECT').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('MNEME-READY')).toBeInTheDocument();

    // Next steps
    expect(screen.getByText('Model the decision: define explicit applicability, deterministic matchers, and confidence thresholds.')).toBeInTheDocument();
    expect(screen.getByText('Generate Mneme rule and integrate into CI/CD pipeline.')).toBeInTheDocument();
  });

  it('shows "Ready to Protect" classification instead of "Requires Modelling"', () => {
    renderOverview();

    // Filter dropdown shows "Ready to Protect" as option text but value is "Requires modelling"
    const select = screen.getByLabelText('Filter by protection classification');
    expect(select).toBeInTheDocument();
    const options = select.querySelectorAll('option');
    const readyToProtectOption = Array.from(options).find(opt => opt.textContent === 'Ready to Protect');
    expect(readyToProtectOption).not.toBeNull();
    expect(readyToProtectOption?.value).toBe('Requires modelling');

    // Protection breakdown badges
    expect(screen.getByText('1 Protected')).toBeInTheDocument();
    expect(screen.getByText('2 Ready to Protect')).toBeInTheDocument();
    expect(screen.getByText('38 Guidance')).toBeInTheDocument();

    // Decision group headers
    expect(screen.getByText('READY TO PROTECT 2 items')).toBeInTheDocument();
    expect(screen.getByText('MNEME-READY 1 items')).toBeInTheDocument();
    expect(screen.getByText('PROTECTED 1 items')).toBeInTheDocument();
  });

  it('has Install section with state transition and canonical GitHub CTA', () => {
    renderOverview();

    // State transition
    expect(screen.getByText('Audit')).toBeInTheDocument();
    expect(screen.getByText('Install')).toBeInTheDocument();
    expect(screen.getByText('Review proposed controls')).toBeInTheDocument();
    expect(screen.getByText('Validate')).toBeInTheDocument();
    expect(screen.getByText('Enable')).toBeInTheDocument();

    // Primary CTA - Install Mneme (points to GitHub)
    const install = screen.getByRole('link', { name: 'Install Mneme' });
    expect(install).toHaveAttribute('href', 'https://github.com/MnemeHQ/mneme');
    expect(install).toHaveClass('btn-primary');

    // Secondary CTA - Discuss a pilot
    const pilot = screen.getByRole('link', { name: 'Discuss a pilot →' });
    expect(pilot).toHaveAttribute('href', 'https://github.com/MnemeHQ/mneme/discussions/categories/pilots');
    expect(pilot).toHaveClass('install-cta-secondary');

    // Setup narrative - use function matcher for text that may be split across elements
    expect(screen.getByText((content) => content.includes('The Audit identifies the gaps. Setup is where you decide what should become protected'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('Mneme does not automatically turn every architectural statement into a guardrail'))).toBeInTheDocument();
  });

  it('does not have Setup section in nav', () => {
    renderOverview();

    expect(screen.queryByRole('button', { name: 'Setup' })).not.toBeInTheDocument();
    expect(screen.queryByText('Request a pilot')).not.toBeInTheDocument();
  });

  it('does not show metric info tooltips', () => {
    renderOverview();

    expect(screen.queryByRole('button', { name: 'More information: PROTECTED' })).not.toBeInTheDocument();
  });

  it('shows section bands with full-width backgrounds', () => {
    renderOverview();

    // Section bands should exist
    const charcoalBands = document.querySelectorAll('.audit-section-band-charcoal');
    expect(charcoalBands.length).toBeGreaterThanOrEqual(3); // overview, decisions, sources

    const warmBand = document.querySelector('.audit-section-band-warm');
    expect(warmBand).toBeInTheDocument();

    const greenBand = document.querySelector('.install-section');
    expect(greenBand).toBeInTheDocument();
  });

  it('Protection Decisions shows all three classifications with counts', () => {
    renderOverview();

    expect(screen.getByText((content) => content.includes('PROTECTED') && content.includes('1') && content.includes('items'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('MNEME-READY') && content.includes('1') && content.includes('items'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('READY TO PROTECT') && content.includes('2') && content.includes('items'))).toBeInTheDocument();
  });

it('Sources Examined shows expanded narrative and inventory', () => {
    renderOverview();

    expect(screen.getByText('Sources Examined')).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('Mneme looks for architectural intent across the repository, not only in ADRs'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('This Audit examined 4 sources'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('Review the inventory to understand what contributed to this Audit'))).toBeInTheDocument();

    // Source inventory
    expect(screen.getByText('docs/adr/0000.md')).toBeInTheDocument();
    expect(screen.getByText('docs/adr/0001.md')).toBeInTheDocument();
    expect(screen.getByText('CLAUDE.md')).toBeInTheDocument();
    expect(screen.getByText('AGENTS.md')).toBeInTheDocument();
  });
});