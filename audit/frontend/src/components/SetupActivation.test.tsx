import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { SetupCommandPanel, SetupStatePanel } from './SetupActivation';
import { auditFixture } from '../test/protectionFixture';
import type { ProjectWithHistory } from '../types/audit';

const { createSetupReference } = vi.hoisted(() => ({ createSetupReference: vi.fn() }));

vi.mock('../hooks/useAuditApi', () => ({
  useAuditApi: () => ({ createSetupReference, error: null }),
}));

vi.mock('../utils/pilotContext', () => ({
  buildPilotHref: () => 'https://mnemehq.com/pilot/',
  storePilotContext: vi.fn(),
}));

const reference = {
  reference: 'opaque-ref-1',
  audit_id: 'audit-1',
  project_id: 'project-1',
  install_command: 'pipx install "mneme-hq>=0.6.0"',
  setup_command: 'mneme setup --audit-ref opaque-ref-1',
  expires_at: '2026-09-19T00:00:00+00:00',
};

const baseline = auditFixture({ audit_id: 'audit-1', project_id: 'project-1' });

function projectFixture(overrides: Partial<ProjectWithHistory> = {}): ProjectWithHistory {
  return {
    id: 'project-1',
    name: 'Contract test',
    slug: 'contract-test',
    source_type: 'github',
    source_locator: 'https://github.com/example/contract-fixture',
    default_ref: null,
    lifecycle: 'saved',
    baseline_audit_id: 'audit-1',
    activation_state: 'not_installed',
    setup_completed_at: null,
    setup_audit_id: null,
    created_at: '2026-09-01T00:00:00Z',
    updated_at: '2026-09-01T00:00:00Z',
    audits: [],
    ...overrides,
  };
}

describe('SetupCommandPanel (before setup)', () => {
  beforeEach(() => {
    createSetupReference.mockReset();
  });

  it('presents the no-enforcement promise and creates the reference on demand', async () => {
    createSetupReference.mockResolvedValue({ success: true, data: reference });
    render(<MemoryRouter><SetupCommandPanel auditId="audit-1" /></MemoryRouter>);

    expect(screen.getByText(/without enabling enforcement/i)).toBeInTheDocument();
    expect(screen.queryByText(/mneme setup --audit-ref/)).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Install Mneme' }));
    expect(createSetupReference).toHaveBeenCalledWith('audit-1');

    const block = await screen.findByText(/mneme setup --audit-ref opaque-ref-1/);
    expect(block).toBeInTheDocument();
    expect(screen.getByText(/pipx install "mneme-hq>=0.6.0"/)).toBeInTheDocument();
    // The frozen promise: setup mode blocks nothing (promise + note).
    expect(screen.getAllByText(/nothing is blocked/i).length).toBeGreaterThanOrEqual(1);
  });

  it('copies the install and setup commands', async () => {
    createSetupReference.mockResolvedValue({ success: true, data: reference });
    render(<MemoryRouter><SetupCommandPanel auditId="audit-1" /></MemoryRouter>);
    fireEvent.click(await screen.findByRole('button', { name: 'Install Mneme' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Copy commands' }));
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      'pipx install "mneme-hq>=0.6.0"\nmneme setup --audit-ref opaque-ref-1');
    expect(await screen.findByText('Copied')).toBeInTheDocument();
  });

  it('fails safely for an unsaved baseline instead of showing a fabricated command', async () => {
    createSetupReference.mockResolvedValue({
      success: false,
      error: 'Setup references can only be created for a saved baseline audit',
    });
    render(<MemoryRouter><SetupCommandPanel auditId="audit-1" /></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: 'Install Mneme' }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/saved baseline/i);
    expect(screen.queryByText(/mneme setup --audit-ref/)).not.toBeInTheDocument();
  });

  it('does not start anything without an explicit user action', async () => {
    render(<MemoryRouter><SetupCommandPanel auditId="audit-1" /></MemoryRouter>);
    // No reference creation happens on render — only on click.
    expect(createSetupReference).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Install Mneme' }));
    await waitFor(() => expect(createSetupReference).toHaveBeenCalledTimes(1));
  });
});

describe('SetupStatePanel (after setup, G6)', () => {
  it('is silent while Mneme is not installed', () => {
    const { container } = render(
      <SetupStatePanel project={projectFixture()} baseline={baseline} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('recognizes setup mode, shows the honest checklist, and offers Start Pilot', () => {
    render(<SetupStatePanel
      project={projectFixture({ activation_state: 'setup', setup_completed_at: '2026-09-05T00:00:00+00:00' })}
      baseline={baseline} />);

    expect(screen.getByRole('heading', { name: 'Mneme installed — Setup mode' })).toBeInTheDocument();
    expect(screen.getByText('Architecture baseline connected')).toBeInTheDocument();
    expect(screen.getByText(/architectural decisions to review/)).toBeInTheDocument();
    expect(screen.getByText('Preventive enforcement not enabled')).toBeInTheDocument();
    const pilot = screen.getByRole('link', { name: 'Start Pilot' });
    expect(pilot).toHaveAttribute('href', 'https://mnemehq.com/pilot/');
    // The panel must never claim enforcement is on.
    expect(screen.queryByText(/enforcement enabled/i)).not.toBeInTheDocument();
  });

  it('renders the active state distinctly', () => {
    render(<SetupStatePanel
      project={projectFixture({ activation_state: 'active' })} baseline={baseline} />);
    expect(screen.getByRole('heading', { name: 'Mneme is active' })).toBeInTheDocument();
    expect(screen.getByText(/explicitly enabled/i)).toBeInTheDocument();
  });

  it('stays honest when the baseline record is unavailable', () => {
    render(<SetupStatePanel
      project={projectFixture({ activation_state: 'setup' })} baseline={null} />);
    expect(screen.getByRole('heading', { name: 'Mneme installed — Setup mode' })).toBeInTheDocument();
    expect(screen.queryByText(/decisions to review/)).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Start Pilot' })).not.toBeInTheDocument();
  });
});
