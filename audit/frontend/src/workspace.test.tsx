import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';
import { parseAudit, parseComparison, parseProject } from './utils/contracts';

const summary = { decisions_discovered: 1, protection_relevant: 0, protected_count: 0,
  mneme_ready_count: 0, requires_modelling_count: 0, guidance_count: 1,
  current_protection: 0, identified_mneme_potential: 0, sources: ['Makefile'], by_category: {} };
const decision = { id: 'config', title: 'Build configuration', summary: 'Build guidance',
  requirement: 'Use a repeatable build', source: {file: 'Makefile', lines: '1-3'},
  protection_classification: 'Guidance', evidence_confidence: 'low', applies_to: [], proposed_rule: null, category: 'config_evidence' };
const audit = { schema: 'mneme.audit/v1', audit_id: 'baseline-id', project_id: 'project-id',
  repository: 'https://github.com/example/repo', repository_url: 'https://github.com/example/repo',
  commit_sha: '1234567890abcdef', mneme_version: '0.6.0', timestamp: '2026-09-03T18:00:00Z', summary, decisions: [decision] };
const row = { id: audit.audit_id, status: 'completed', trigger_type: 'initial', commit_sha: audit.commit_sha,
  mneme_version: audit.mneme_version, schema_version: 1, created_at: audit.timestamp, completed_at: audit.timestamp };
const project = {id: 'project-id', name: 'Contract test', slug: 'contract-test', source_type: 'github',
  source_locator: audit.repository, default_ref: null, lifecycle: 'saved', baseline_audit_id: audit.audit_id,
  audits: [row], created_at: audit.timestamp, updated_at: audit.timestamp };
const states = ['improved', 'regressed', 'added', 'removed', 'unchanged', 'uncomparable'];
const comparison = {baseline_audit_id: audit.audit_id, current_audit_id: 'latest-id',
  baseline_commit_sha: audit.commit_sha, current_commit_sha: 'abcdef1234567890',
  baseline_mneme_version: '0.6.0', current_mneme_version: '0.6.0', baseline_schema: audit.schema,
  current_schema: audit.schema, baseline_schema_version: 1, current_schema_version: 1, schema_compatibility: 'compatible',
  baseline_summary: {...summary, current_protection: .2}, current_summary: {...summary, current_protection: .6},
  current_protection_delta: .4, identified_mneme_potential_delta: 0,
  summary: Object.fromEntries(states.map(state => [state, 1])),
  decisions: states.map(state => ({decision_key: state, state, baseline_decision: decision, current_decision: decision, details: {}})) };
const respond = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), {status, headers: {'Content-Type': 'application/json'}}));
const mount = (path: string) => render(<MemoryRouter initialEntries={[path]} future={{v7_startTransition: true, v7_relativeSplatPath: true}}><App /></MemoryRouter>);

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn());
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });

it('rejects legacy/missing/non-finite fields before rendering an audit', () => {
  expect(() => parseAudit({id: 'legacy', summary: {coverage: 20}})).toThrow('incompatible audit');
  expect(() => parseAudit({...audit, summary: {...summary, current_protection: NaN}})).toThrow();
  expect(parseAudit(audit).audit_id).toBe(audit.audit_id);
  expect(() => parseComparison({...comparison, summary: undefined})).toThrow('incompatible comparison');
});

it.each([null, {}, {type: 'FORBID_LITERAL', pattern: ' ', description: 'Reject token'},
  {type: 'UNSUPPORTED', pattern: 'sqlite3', description: 'Reject token'}])(
  'rejects an invalid Mneme-ready guardrail without reclassifying or hiding it: %j', rule => {
    expect(() => parseAudit({...audit, decisions: [{...decision,
      protection_classification: 'Mneme-ready', proposed_rule: rule}]})).toThrow('incompatible audit');
  });

it('rejects unsafe render shapes and missing project identity', () => {
  expect(() => parseAudit({...audit, decisions: [{...decision, evidence_confidence: 'unknown'}]})).toThrow();
  expect(() => parseProject({...project, id: undefined})).toThrow('incompatible project');
  expect(() => parseProject({...project, id: 'undefined'})).toThrow();
  expect(() => parseComparison({...comparison, decisions: [{...comparison.decisions[0], current_decision: {id: 'bad'}}]})).toThrow();
});

it('opens a concrete guardrail supplied by the backend', async () => {
  const ready = {...decision, protection_classification: 'Mneme-ready', proposed_rule: {
    type: 'FORBID_LITERAL', pattern: 'sqlite3', description: 'Reject the sqlite3 literal',
  }};
  vi.mocked(fetch).mockImplementation(() => respond({id: audit.audit_id,
    project_id: project.id, result: {...audit, decisions: [ready]}, summary_payload: summary}));
  mount('/audit/baseline-id/decisions/config');
  const button = await screen.findByRole('button', {name: 'View guardrail'});
  const target = document.getElementById('guardrail')!;
  target.scrollIntoView = vi.fn();
  fireEvent.click(button);
  expect(target.scrollIntoView).toHaveBeenCalled();
  expect(target).toHaveFocus();
  expect(screen.getByText('FORBID_LITERAL "sqlite3"')).toBeInTheDocument();
  expect(screen.getByText('Reject the sqlite3 literal')).toBeInTheDocument();
});

it('rejects a baseline response without a project ID instead of navigating to undefined', async () => {
  vi.mocked(fetch).mockImplementation((input) => String(input).endsWith('/baselines')
    ? respond({...project, id: undefined})
    : respond({id: audit.audit_id, project_id: project.id, result: audit, summary_payload: summary}));
  mount('/audit/baseline-id');
  fireEvent.click(await screen.findByRole('button', {name: 'Save Baseline'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('incompatible project');
  expect(screen.getByRole('button', {name: 'Save Baseline'})).toBeInTheDocument();
  expect(vi.mocked(fetch).mock.calls.some(([url]) => String(url).includes('/undefined'))).toBe(false);
});

it('uses canonical multipart response and saves the exact audit ID as JSON', async () => {
  vi.mocked(fetch).mockImplementation((input, options) => {
    const url = String(input);
    if (url.endsWith('/api/v1/audit')) return respond(audit, 201);
    if (url.endsWith('/api/v1/baselines')) {
      expect(JSON.parse(options?.body as string)).toEqual({audit_id: audit.audit_id});
      return respond(project);
    }
    if (url.includes('/projects/')) return respond(project);
    return respond({id: audit.audit_id, project_id: project.id, result: audit, summary_payload: summary});
  });
  mount('/');
  fireEvent.change(screen.getByLabelText('GitHub Repository URL'), {target: {value: audit.repository}});
  fireEvent.click(screen.getByRole('button', {name: 'Run Architecture Audit'}));
  await screen.findByRole('button', {name: 'Save Baseline'});
  expect(vi.mocked(fetch).mock.calls[0][1]?.body).toBeInstanceOf(FormData);
  fireEvent.click(screen.getByRole('button', {name: 'View All Decisions'}));
  expect(window.scrollTo).toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', {name: 'Save Baseline'}));
  await screen.findByRole('heading', {name: 'Contract test'});
  expect(screen.getByRole('heading', {name: 'Audit history'})).toBeInTheDocument();
  expect(screen.queryByText(/NaN/)).not.toBeInTheDocument();
});

it('renders backend percentages, delta and states without reconstructing them from rows', async () => {
  vi.mocked(fetch).mockImplementation(() => respond(comparison));
  mount('/project/project-id/compare');
  await screen.findByText('20%');
  expect(screen.getByText('60%')).toBeInTheDocument();
  expect(screen.getByTestId('score-delta')).toHaveTextContent('+40 percentage points');
  for (const label of ['Improved', 'Regressed', 'Added', 'Removed', 'Unchanged', 'Not comparable']) {
    expect(screen.getByRole('heading', {name: `${label} (1)`})).toBeInTheDocument();
  }
  // All row classifications are Guidance; their backend states still win.
  expect(screen.queryByText(/Mneme Potential/)).not.toBeInTheDocument();
});

it('shows an actionable error instead of crashing on a missing comparison summary', async () => {
  vi.mocked(fetch).mockImplementation(() => respond({...comparison, summary: undefined}));
  mount('/project/project-id/compare');
  expect(await screen.findByRole('alert')).toHaveTextContent('incompatible comparison');
  expect(screen.getByRole('link', {name: 'Back to Project'})).toBeInTheDocument();
});

it('keeps the persisted project visible when Re-audit fails', async () => {
  vi.mocked(fetch).mockImplementation((input, options) => {
    if (options?.method === 'POST') {
      expect(JSON.parse(options.body as string)).toEqual({trigger_type: 're_audit'});
      return respond({error: 'Repository unavailable'}, 502);
    }
    return String(input).includes('/projects/') ? respond(project)
      : respond({id: audit.audit_id, project_id: project.id, result: audit, summary_payload: summary});
  });
  mount('/project/project-id');
  fireEvent.click(await screen.findByRole('button', {name: 'Run Re-audit'}));
  await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('baseline remains unchanged'));
  expect(screen.getByRole('heading', {name: 'Baseline Audit'})).toBeInTheDocument();
});
