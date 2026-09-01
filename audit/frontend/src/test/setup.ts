import '@testing-library/jest-dom';
import { createElement } from 'react';
import { vi } from 'vitest';

// Mock useAuditApi hook
vi.mock('../hooks/useAuditApi', () => ({
  useAuditApi: () => ({
    getAudit: vi.fn(),
    createAudit: vi.fn(),
    exportAudit: vi.fn(),
    loading: false,
    error: null,
  }),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => {
  return {
    Github: () => createElement('svg', { 'data-testid': 'github-icon' }),
    ArrowLeft: () => createElement('svg', { 'data-testid': 'arrow-left-icon' }),
    Loader2: () => createElement('svg', { 'data-testid': 'loader-icon' }),
    Download: () => createElement('svg', { 'data-testid': 'download-icon' }),
    FileText: () => createElement('svg', { 'data-testid': 'file-text-icon' }),
    AlertCircle: () => createElement('svg', { 'data-testid': 'alert-circle-icon' }),
    CheckCircle: () => createElement('svg', { 'data-testid': 'check-circle-icon' }),
    AlertTriangle: () => createElement('svg', { 'data-testid': 'alert-triangle-icon' }),
    Circle: () => createElement('svg', { 'data-testid': 'circle-icon' }),
    Search: () => createElement('svg', { 'data-testid': 'search-icon' }),
    ChevronRight: () => createElement('svg', { 'data-testid': 'chevron-right-icon' }),
    ChevronDown: () => createElement('svg', { 'data-testid': 'chevron-down-icon' }),
    ChevronUp: () => createElement('svg', { 'data-testid': 'chevron-up-icon' }),
    Target: () => createElement('svg', { 'data-testid': 'target-icon' }),
    Upload: () => createElement('svg', { 'data-testid': 'upload-icon' }),
    Copy: () => createElement('svg', { 'data-testid': 'copy-icon' }),
    ArrowRight: () => createElement('svg', { 'data-testid': 'arrow-right-icon' }),
  };
});

// Mock window.location.reload
Object.defineProperty(window, 'location', {
  value: {
    reload: vi.fn(),
    href: 'http://localhost:3000/audit/',
  },
  writable: true,
});

// Mock navigator.clipboard
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});
