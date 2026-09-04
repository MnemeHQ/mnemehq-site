import { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav } from '../components/AuditNav';
import { StatsGrid } from '../components/StatsGrid';
import type { ProjectWithHistory, ProtectionAuditResponse } from '../types/audit';

export function AuditProvenance({ audit }: { audit: ProtectionAuditResponse }) {
  return <dl className="audit-provenance">
    <div><dt>Commit</dt><dd>{audit.commit_sha}</dd></div>
    <div><dt>Evaluated</dt><dd><time dateTime={audit.timestamp}>{new Date(audit.timestamp).toLocaleString(undefined, { timeZoneName: 'short' })}</time></dd></div>
    <div><dt>Mneme version</dt><dd>{audit.mneme_version}</dd></div>
    <div><dt>Audit schema</dt><dd>{audit.schema}</dd></div>
    <div><dt>Audit ID</dt><dd>{audit.audit_id}</dd></div>
  </dl>;
}

export function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { getProject, getProjectAudit, runProjectAudit } = useAuditApi();
  const [project, setProject] = useState<ProjectWithHistory | null>(null);
  const [baseline, setBaseline] = useState<ProtectionAuditResponse | null>(null);
  const [latest, setLatest] = useState<ProtectionAuditResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!projectId) throw new Error('Project ID is missing.');
    const response = await getProject(projectId);
    if (!response.success || !response.data) throw new Error(response.error || 'Project unavailable');
    const value = response.data;
    const latestId = value.audits.find(a => a.status === 'completed')?.id;
    const ids = [...new Set([value.baseline_audit_id, latestId].filter((id): id is string => !!id))];
    const records = await Promise.all(ids.map(id => getProjectAudit(id)));
    const failed = records.find(record => !record.success);
    if (failed) throw new Error(failed.error || 'Audit details unavailable');
    const audits = records.map(record => record.data!.result);
    setProject(value);
    setBaseline(audits.find(a => a.audit_id === value.baseline_audit_id) || null);
    setLatest(audits.find(a => a.audit_id === latestId && a.audit_id !== value.baseline_audit_id) || null);
  }, [projectId, getProject, getProjectAudit]);

  useEffect(() => {
    setLoading(true);
    setError(null);
    load().catch(cause => setError(cause.message)).finally(() => setLoading(false));
  }, [load]);

  const reaudit = async () => {
    if (!project) return;
    setRunning(true);
    setError(null);
    try {
      const response = await runProjectAudit(project.id, { trigger_type: 're_audit' });
      if (!response.success) throw new Error(response.error || 'Re-audit failed');
      await load();
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Re-audit failed'); }
    finally { setRunning(false); }
  };

  return <div className="audit-layout"><AuditNav /><main className="audit-container">
    {loading && <p role="status">Loading project…</p>}
    {error && <p role="alert" className="action-error">{error} {project && 'Your existing baseline remains unchanged.'}</p>}
    {!loading && !project && <Link to="/">Run New Audit</Link>}
    {project && <>
      <header className="audit-hero">
        <span className="audit-hero-tag">Architecture Protection Project</span>
        <h1>{project.name}</h1><p>{project.source_locator}</p>
        <p><span className="badge">{project.lifecycle}</span> · {project.audits.length} audits</p>
      </header>
      {[[baseline, 'Baseline Audit'], [latest, 'Latest Re-audit']].map(([value, title]) => {
        const audit = value as ProtectionAuditResponse | null;
        if (!audit) return null;
        return <section className="audit-section" key={String(title)} aria-label={String(title)}>
          <h2>{String(title)}</h2><StatsGrid summary={audit.summary} />
          <AuditProvenance audit={audit} />
          <Link className="btn btn-ghost" to={`/audit/${audit.audit_id}`}>View audit decisions</Link>
        </section>;
      })}
      <section className="audit-section" aria-label="Actions">
        <h2>Actions</h2><div className="flex flex-wrap gap-3">
          <button className="btn btn-primary" onClick={reaudit} disabled={running || project.lifecycle === 'ephemeral' || project.source_type !== 'github'}>
            {running ? 'Running re-audit…' : 'Run Re-audit'}
          </button>
          {baseline && latest && <Link className="btn btn-ghost" to={`/project/${project.id}/compare`}>Compare Changes</Link>}
        </div>
        {running && <p role="status">Evaluating the repository. Your baseline will not be overwritten.</p>}
        {project.source_type !== 'github' && <p>To audit a changed ZIP, start a new audit. Automatic re-audit requires a public GitHub repository.</p>}
      </section>
      <section className="audit-section" aria-label="Audit history"><h2>Audit history</h2>
        <ul className="audit-history">{project.audits.map(audit => <li key={audit.id}>
          {audit.status === 'completed' ? <Link to={`/audit/${audit.id}`}>{audit.id}</Link> : <span>{audit.id}</span>}
          <span>{audit.id === project.baseline_audit_id ? 'Baseline' : audit.trigger_type} · {audit.status}</span>
          <span>{audit.commit_sha}</span><time dateTime={audit.created_at}>{new Date(audit.created_at).toLocaleString(undefined, { timeZoneName: 'short' })}</time>
        </li>)}</ul>
      </section>
    </>}
  </main></div>;
}
