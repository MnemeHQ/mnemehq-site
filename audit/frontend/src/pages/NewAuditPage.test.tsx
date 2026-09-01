import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useAuditApi } from '../hooks/useAuditApi';
import { NewAuditPage } from './NewAuditPage';

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
