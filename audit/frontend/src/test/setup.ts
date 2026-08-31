import '@testing-library/jest-dom';
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
    Github: () => globalThis.React.createElement('svg', { 'data-testid': 'github-icon' }),
    ArrowLeft: () => globalThis.React.createElement('svg', { 'data-testid': 'arrow-left-icon' }),
    Loader2: () => globalThis.React.createElement('svg', { 'data-testid': 'loader-icon' }),
    Download: () => globalThis.React.createElement('svg', { 'data-testid': 'download-icon' }),
    FileText: () => globalThis.React.createElement('svg', { 'data-testid': 'file-text-icon' }),
    AlertCircle: () => globalThis.React.createElement('svg', { 'data-testid': 'alert-circle-icon' }),
    CheckCircle: () => globalThis.React.createElement('svg', { 'data-testid': 'check-circle-icon' }),
    AlertTriangle: () => globalThis.React.createElement('svg', { 'data-testid': 'alert-triangle-icon' }),
    Circle: () => globalThis.React.createElement('svg', { 'data-testid': 'circle-icon' }),
    Target: () => globalThis.React.createElement('svg', { 'data-testid': 'target-icon' }),
    Upload: () => globalThis.React.createElement('svg', { 'data-testid': 'upload-icon' }),
    Copy: () => globalThis.React.createElement('svg', { 'data-testid': 'copy-icon' }),
    ArrowRight: () => globalThis.React.createElement('svg', { 'data-testid': 'arrow-right-icon' }),
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