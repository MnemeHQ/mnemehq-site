import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useAuditApi } from '../hooks/useAuditApi';
import { NewAuditPage } from './NewAuditPage';

vi.mock('../hooks/useAuditApi', () => ({ useAuditApi: vi.fn() }));

const mockedUseAuditApi = vi.mocked(useAuditApi);

describe('NewAuditPage errors', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows a repository ingestion error exactly once', async () => {
    const createAudit = vi.fn().mockResolvedValue({
      success: false,
      error: 'Repository contains unsafe symlink: escape.md',
    });

    mockedUseAuditApi.mockReturnValue({
      createAudit,
      createSetupReference: vi.fn(),
      getAudit: vi.fn(),
      exportAudit: vi.fn(),
      getProject: vi.fn(),
      getProjectAudit: vi.fn(),
      saveBaseline: vi.fn(),
      runProjectAudit: vi.fn(),
      compareAudits: vi.fn(),
      loading: false,
      error: 'Repository contains unsafe symlink: escape.md',
    });

    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText('GitHub Repository URL'), {
      target: { value: 'https://github.com/example/repository' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Run Architecture Audit' }));

    await waitFor(() => expect(createAudit).toHaveBeenCalledTimes(1));
    const alerts = await screen.findAllByRole('alert');
    expect(alerts).toHaveLength(1);
    expect(alerts[0]).toHaveTextContent('Repository contains unsafe symlink: escape.md');
  });
});

describe('NewAuditPage private repository section', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseAuditApi.mockReturnValue({
      createAudit: vi.fn(),
      createSetupReference: vi.fn(),
      getAudit: vi.fn(),
      exportAudit: vi.fn(),
      getProject: vi.fn(),
      getProjectAudit: vi.fn(),
      saveBaseline: vi.fn(),
      runProjectAudit: vi.fn(),
      compareAudits: vi.fn(),
      loading: false,
      error: null,
    });
  });

  it('shows private repository heading and description', () => {
    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Working with a private repository?')).toBeInTheDocument();
    expect(screen.getByText('Upload a repository ZIP for the Audit without granting Mneme HQ access to GitHub.')).toBeInTheDocument();
  });

  it('defers local setup until after the baseline is saved', () => {
    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('After the Audit, save a baseline to generate the setup command for your local checkout.')).toBeInTheDocument();
    expect(screen.queryByText('mneme init')).not.toBeInTheDocument();
  });

  it('shows Set up Mneme locally CTA link to quickstart docs', () => {
    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    const link = screen.getByRole('link', { name: 'Set up Mneme locally' });
    expect(link).toHaveAttribute('href', '/docs/#quickstart');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveClass('btn-ghost');
  });

  it('shows ZIP preparation, upload, retention, and journey guidance', () => {
    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole('button', { name: 'Upload repository ZIP file' })).toBeInTheDocument();
    expect(screen.getByText('Upload repository ZIP')).toBeInTheDocument();
    expect(screen.getByText('Upload a ZIP of the repository source.')).toBeInTheDocument();
    expect(screen.getByText(/Exclude/)).toHaveTextContent(
      'Exclude .git, node_modules, build artifacts, .env files, credentials, and other secrets.',
    );
    expect(screen.getByText('Repository code is temporarily processed on Mneme’s servers to perform the Audit. The uploaded ZIP and extracted repository are deleted when processing finishes; Mneme retains the resulting Audit record.')).toBeInTheDocument();
    expect(screen.getByLabelText('Private repository journey')).toHaveTextContent(
      'Prepare ZIP → Upload → Audit → Save baseline → Install Mneme → Setup → Start Pilot',
    );
  });

  it('submits the selected ZIP through the existing audit contract', async () => {
    const createAudit = vi.fn().mockResolvedValue({
      success: true,
      data: { audit_id: 'private-audit-123' },
    });
    mockedUseAuditApi.mockReturnValue({
      createAudit,
      createSetupReference: vi.fn(),
      getAudit: vi.fn(),
      exportAudit: vi.fn(),
      getProject: vi.fn(),
      getProjectAudit: vi.fn(),
      saveBaseline: vi.fn(),
      runProjectAudit: vi.fn(),
      compareAudits: vi.fn(),
      loading: false,
      error: null,
    });
    const archive = new File(['repository'], 'private-repository.zip', { type: 'application/zip' });

    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText('Choose repository ZIP'), { target: { files: [archive] } });
    expect(screen.getByText(/private-repository\.zip/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Run Private Repository Audit' }));

    await waitFor(() => expect(createAudit).toHaveBeenCalledTimes(1));
    expect(createAudit).toHaveBeenCalledWith({ zipFile: archive }, 'zip');
  });

  it('does not claim local Architecture Audit or protection gaps reporting', () => {
    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    // These claims are not made in the current implementation
    expect(screen.queryByText('reports protection gaps')).not.toBeInTheDocument();
    expect(screen.queryByText('Local Architecture Audit')).not.toBeInTheDocument();
    expect(screen.queryByText('Your code stays on your machine')).not.toBeInTheDocument();
  });

  it('uses full-width charcoal section band', () => {
    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    const band = document.querySelector('.audit-section-band-charcoal');
    expect(band).toBeInTheDocument();
    // Band should contain the private repo section
    expect(band?.querySelector('#private-repo-heading')).toBeInTheDocument();
  });
});

describe('NewAuditPage demo repository', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseAuditApi.mockReturnValue({
      createAudit: vi.fn().mockResolvedValue({
        success: true,
        data: { audit_id: 'test-audit-123' },
      }),
      getAudit: vi.fn(),
      exportAudit: vi.fn(),
      getProject: vi.fn(),
      getProjectAudit: vi.fn(),
      saveBaseline: vi.fn(),
      createSetupReference: vi.fn(),
      runProjectAudit: vi.fn(),
      compareAudits: vi.fn(),
      loading: false,
      error: null,
    });
  });

  it('submits the canonical demo repository URL when Try Demo Repository is clicked', async () => {
    const createAudit = vi.fn().mockResolvedValue({
      success: true,
      data: { audit_id: 'test-audit-123' },
    });

    mockedUseAuditApi.mockReturnValue({
      createAudit,
      getAudit: vi.fn(),
      exportAudit: vi.fn(),
      getProject: vi.fn(),
      getProjectAudit: vi.fn(),
      saveBaseline: vi.fn(),
      createSetupReference: vi.fn(),
      runProjectAudit: vi.fn(),
      compareAudits: vi.fn(),
      loading: false,
      error: null,
    });

    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    // Click the Try Demo Repository button
    fireEvent.click(screen.getByRole('button', { name: 'Try Demo Repository' }));

    // Wait for createAudit to be called
    await waitFor(() => expect(createAudit).toHaveBeenCalledTimes(1));

    // Verify the exact canonical demo URL was submitted
    expect(createAudit).toHaveBeenCalledWith(
      expect.objectContaining({
        repositoryUrl: 'https://github.com/MnemeHQ/architecture-protection-demo',
      }),
      'demo',
    );
  });
});
