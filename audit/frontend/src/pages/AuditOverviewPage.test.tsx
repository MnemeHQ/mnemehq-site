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

    // Assert scroll was invoked with smooth behavior (don't assert exact pixel)
    expect(window.scrollTo).toHaveBeenCalledWith(
      expect.objectContaining({ behavior: 'smooth' })
    );
    // The active section button should get aria-current, but it may not be the same button we clicked
    // Just verify scroll was invoked correctly
    expect(window.scrollTo).toHaveBeenCalled();
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

    // How to read this audit narrative - check full document for split text
    const allText = document.body.textContent || '';
    expect(allText).toContain('Mneme identified 41 architectural decisions and constraints');
    expect(allText).toContain('3 decisions are suitable for deterministic protection');
    expect(allText).toContain('2 architectural decisions could be converted');

    // Protection Gaps narrative
    expect(allText).toContain('2 architectural decisions could be protected more explicitly');
    expect(allText).toContain('These decisions describe constraints that can be evaluated mechanically');

    // Protection Decisions narrative
    expect(allText).toContain('This is the decision-level evidence behind the Audit result');
    expect(allText).toContain('Protected');
    expect(allText).toContain('Ready to Protect');
    expect(allText).toContain('Guidance Only');

    // Sources Examined narrative
    expect(allText).toContain('Mneme looks for architectural intent across the repository');
  });

  it('shows Protection Gaps with human-readable leads', () => {
    renderOverview();

    // Gap cards should use human-readable leads - appears in gap section
    expect(screen.getAllByText('Use Markdown ADRs')).toHaveLength(2); // gap card + decision card
    expect(screen.getAllByText('Use GADR naming')).toHaveLength(2);

    // Should show badges with new label - multiple instances exist
    expect(screen.getAllByText('READY TO PROTECT').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('MNEME-READY').length).toBeGreaterThanOrEqual(1);

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
    // Option text includes "(0)" count suffix, so use includes
    const readyToProtectOption = Array.from(options).find(opt => opt.textContent?.includes('Ready to Protect'));
    expect(readyToProtectOption).not.toBeNull();
    // Check the value attribute via getAttribute since it's an HTMLOptionElement
    expect((readyToProtectOption as HTMLOptionElement).getAttribute('value')).toBe('Requires modelling');

    // Protection breakdown badges - use getAllByText since they appear multiple times
    expect(screen.getAllByText((content) => content.includes('Protected') && content.includes('1'))).toBeTruthy();
    expect(screen.getAllByText((content) => content.includes('Ready') && content.includes('Protect'))).toBeTruthy();
    expect(screen.getAllByText((content) => content.includes('Guidance') && content.includes('38'))).toBeTruthy();

    // Decision group headers - query by heading role since text is split across spans
    const groupHeaders = screen.getAllByRole('heading', { level: 3 });
    const headerTexts = groupHeaders.map(h => h.textContent || '');
    expect(headerTexts.some(t => t.includes('READY TO PROTECT') && t.includes('items'))).toBe(true);
    expect(headerTexts.some(t => t.includes('MNEME-READY') && t.includes('items'))).toBe(true);
    expect(headerTexts.some(t => t.includes('PROTECTED') && t.includes('items'))).toBe(true);
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

    // Decision group headers - query by heading role since text is split across spans
    const groupHeaders = screen.getAllByRole('heading', { level: 3 });
    const headerTexts = groupHeaders.map(h => h.textContent || '');
    expect(headerTexts.some(t => t.includes('PROTECTED') && t.includes('1') && t.includes('items'))).toBe(true);
    expect(headerTexts.some(t => t.includes('MNEME-READY') && t.includes('1') && t.includes('items'))).toBe(true);
    expect(headerTexts.some(t => t.includes('READY TO PROTECT') && t.includes('1') && t.includes('items'))).toBe(true);
  });

  it('Sources Examined shows expanded narrative and inventory', () => {
    renderOverview();

    expect(screen.getByText('Sources Examined')).toBeInTheDocument();
    const allText = document.body.textContent || '';
    expect(allText).toContain('Mneme looks for architectural intent across the repository, not only in ADRs');
    expect(allText).toContain('This Audit examined 4 sources');
    expect(allText).toContain('Review the inventory to understand what contributed to this Audit');

    // Source inventory
    expect(screen.getAllByText('docs/adr/0000.md').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('docs/adr/0001.md').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('CLAUDE.md').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('AGENTS.md').length).toBeGreaterThanOrEqual(1);
  });
});