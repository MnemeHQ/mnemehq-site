import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Keep application components/hooks real by default. Routing-only tests may
// mock explicitly; contract tests exercise fetch at the HTTP boundary.
Object.assign(navigator, { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } });
