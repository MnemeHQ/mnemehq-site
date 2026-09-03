import { describe, expect, it } from 'vitest';
import { getLegacyHashRoute } from './routing';

describe('clean audit workspace URLs', () => {
  it('migrates an old hash audit URL to the history route', () => {
    expect(
      getLegacyHashRoute('#/audit/424e1795', '/audit/workspace'),
    ).toBe('/audit/workspace/audit/424e1795');
  });

  it('migrates the old hash root without adding a duplicate slash', () => {
    expect(getLegacyHashRoute('#/', '/audit/workspace')).toBe('/audit/workspace/');
  });

  it('leaves ordinary fragment identifiers alone', () => {
    expect(getLegacyHashRoute('#sources', '/audit/workspace')).toBeNull();
  });
});
