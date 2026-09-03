import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav } from '../components/AuditNav';
import type { AuditComparison, ComparisonState } from '../types/audit';

const states: ComparisonState[] = ['improved', 'regressed', 'added', 'removed', 'unchanged', 'uncomparable'];
const labels: Record<ComparisonState, string> = { improved: 'Improved', regressed: 'Regressed', added: 'Added', removed: 'Removed', unchanged: 'Unchanged', uncomparable: 'Not comparable' };
// Percentage formatting only. All values and deltas are returned by the backend.
const percentage = (value: number) => new Intl.NumberFormat(undefined, { style: 'percent', maximumFractionDigits: 0 }).format(value);

export function ComparisonPage() {
  const { projectId } = useParams<{projectId: string}>();
  const { compareAudits } = useAuditApi();
  const [comparison, setComparison] = useState<AuditComparison | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (!projectId) { setError('Project ID is missing.'); setLoading(false); return; }
    let active = true;
    setLoading(true);
    setError(null);
    compareAudits(projectId).then(result => {
      if (!active) return;
      if (result.success && result.data) setComparison(result.data);
      else setError(result.error || 'Comparison unavailable');
      setLoading(false);
    });
    return () => { active = false; };
  }, [projectId, compareAudits]);

  return <div className="audit-layout"><AuditNav /><main className="audit-container">
    <Link className="btn btn-ghost" to={`/project/${projectId}`}>Back to Project</Link>
    <header className="audit-hero"><span className="audit-hero-tag">Architecture Protection</span><h1>Compare Changes</h1></header>
    {loading && <p role="status">Loading comparison…</p>}
    {error && <p role="alert" className="action-error">{error}</p>}
    {!loading && !error && comparison && <>
      <section className="comparison-score-display" aria-label="Protection comparison">
        <div className="comparison-score-pair">
          <div className="comparison-score"><span className="comparison-score-value">{percentage(comparison.baseline_summary.current_protection)}</span><span>Baseline Protection</span></div>
          <span aria-hidden="true">→</span>
          <div className="comparison-score"><span className="comparison-score-value">{percentage(comparison.current_summary.current_protection)}</span><span>Current Protection</span></div>
        </div>
        <p data-testid="score-delta">{comparison.current_protection_delta > 0 ? '+' : ''}{new Intl.NumberFormat(undefined, {maximumFractionDigits: 1}).format(comparison.current_protection_delta * 100)} percentage points</p>
        {comparison.current_summary.mneme_ready_count > 0 && <p>Mneme Potential: {percentage(comparison.current_summary.identified_mneme_potential)}</p>}
      </section>
      <section className="audit-section" aria-label="Comparison summary"><h2>Summary</h2>
        <p>{states.map(state => `${comparison.summary[state]} ${labels[state].toLowerCase()}`).join(' · ')}</p>
        <p className="text-muted">Comparison states and protection scores are supplied by the backend from the saved snapshots.</p>
      </section>
      <dl className="audit-provenance">
        <div><dt>Baseline audit</dt><dd><Link to={`/audit/${comparison.baseline_audit_id}`}>{comparison.baseline_audit_id}</Link></dd></div>
        <div><dt>Latest audit</dt><dd><Link to={`/audit/${comparison.current_audit_id}`}>{comparison.current_audit_id}</Link></dd></div>
        <div><dt>Baseline commit</dt><dd>{comparison.baseline_commit_sha}</dd></div>
        <div><dt>Latest commit</dt><dd>{comparison.current_commit_sha}</dd></div>
        <div><dt>Mneme versions</dt><dd>{comparison.baseline_mneme_version} → {comparison.current_mneme_version}</dd></div>
        <div><dt>Schemas</dt><dd>{comparison.baseline_schema} → {comparison.current_schema}</dd></div>
      </dl>
      {states.map(state => comparison.summary[state] > 0 && <section key={state} className="audit-section" aria-label={labels[state]}>
        <h2>{labels[state]} ({comparison.summary[state]})</h2>
        <div className="comparison-list">{comparison.decisions.filter(item => item.state === state).map(item => {
          const decision = item.current_decision || item.baseline_decision;
          const auditId = item.current_decision ? comparison.current_audit_id : comparison.baseline_audit_id;
          return <article key={item.decision_key} className="comparison-row">
            <span className="badge">{labels[item.state]}</span><h3>{decision?.title}</h3>
            <p>{decision?.summary}</p>
            <p>{item.baseline_decision?.protection_classification || 'Not present'} → {item.current_decision?.protection_classification || 'Not present'}</p>
            {item.state === 'uncomparable' && <p>{String(item.details.reason || 'The backend marked these snapshots as not comparable.')}</p>}
            {decision && <Link to={`/audit/${auditId}/decisions/${encodeURIComponent(decision.id)}`}>View decision evidence</Link>}
          </article>;
        })}</div>
      </section>)}
    </>}
  </main></div>;
}
