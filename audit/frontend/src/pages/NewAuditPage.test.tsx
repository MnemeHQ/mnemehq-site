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
    expect(screen.getByText('Install Mneme in your local checkout and use it without granting Mneme HQ access to your repository.')).toBeInTheDocument();
  });

  it('shows verified local commands: pip install mneme-hq and mneme init', () => {
    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('pip install mneme-hq')).toBeInTheDocument();
    expect(screen.getByText('mneme init')).toBeInTheDocument();
    // Should NOT show npm install or mneme check
    expect(screen.queryByText('npm install -g @mnemehq/mneme')).not.toBeInTheDocument();
    expect(screen.queryByText('mneme check')).not.toBeInTheDocument();
  });

  it('shows Set up Mneme locally CTA link to quickstart docs', () => {
    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    const link = screen.getByRole('link', { name: 'Set up Mneme locally' });
    expect(link).toHaveAttribute('href', '/docs/quickstart');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveClass('btn-ghost');
  });

  it('does not show ZIP upload area', () => {
    render(
      <MemoryRouter>
        <NewAuditPage />
      </MemoryRouter>,
    );

    expect(screen.queryByText('Upload repository ZIP')).not.toBeInTheDocument();
    expect(screen.queryByText('Drag and drop a .zip file')).not.toBeInTheDocument();
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
