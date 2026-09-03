import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav } from '../components/AuditNav';
import { Loader2, AlertCircle, ArrowRight, Clock, GitBranch, Shield, CheckCircle, Zap, Brain, Circle, RotateCcw } from 'lucide-react';
import type { ProjectWithHistory, ProtectionAuditResponse, ProtectionSummary } from '../types/audit';

const LIFECYCLE_LABELS: Record<string, string> = {
  ephemeral: 'Ephemeral',
  saved: 'Saved',
  pilot: 'Pilot',
  archived: 'Archived',
};

const LIFECYCLE_COLORS: Record<string, string> = {
  ephemeral: 'var(--muted)',
  saved: 'var(--accent)',
  pilot: 'var(--teal)',
  archived: 'var(--red)',
};

function formatDateTime(dateString: string) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) + 
    ' ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function getProtectionPct(summary: ProtectionSummary | undefined) {
  if (!summary) return 0;
  return Math.round((summary.current_protection || 0) * 100);
}

function getMnemePotentialPct(summary: ProtectionSummary | undefined) {
  if (!summary) return 0;
  return Math.round((summary.identified_mneme_potential || 0) * 100);
}

export function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { getProject, runProjectAudit, getProjectAudit, error: apiError } = useAuditApi();
  
  const stateProject = (location.state as { project?: ProjectWithHistory })?.project;
  const [project, setProject] = useState<ProjectWithHistory | null>(stateProject ?? null);
  const [loading, setLoading] = useState<boolean>(!stateProject);
  const [error, setError] = useState<string | null>(null);
  const [runningAudit, setRunningAudit] = useState(false);
  const [baselineAuditData, setBaselineAuditData] = useState<ProtectionAuditResponse | null>(null);
  const [latestAuditData, setLatestAuditData] = useState<ProtectionAuditResponse | null>(null);

  const baseline = project?.audits.find(a => a.id === project?.baseline_audit_id);
  const latestAudit = project?.audits[0];

  useEffect(() => {
    if (!projectId) {
      navigate('/', { replace: true });
      return;
    }
  }, [projectId, navigate]);

  useEffect(() => {
    if (!projectId) return;
    
    if (project && project.id === projectId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    getProject(projectId).then((result) => {
      setLoading(false);
      if (result.success && result.data) {
        setProject(result.data);
      } else {
        setError(result.error || 'Failed to load project');
      }
    });
  }, [projectId, getProject]);

  // Fetch baseline audit details
  useEffect(() => {
    if (baseline && !baselineAuditData) {
      getProjectAudit(baseline.id).then((result) => {
        if (result.success && result.data?.result) {
          setBaselineAuditData(result.data.result as unknown as ProtectionAuditResponse);
        }
      });
    }
  }, [baseline, getProjectAudit]);

  // Fetch latest audit details
  useEffect(() => {
    if (latestAudit && latestAudit.id !== baseline?.id && !latestAuditData) {
      getProjectAudit(latestAudit.id).then((result) => {
        if (result.success && result.data?.result) {
          setLatestAuditData(result.data.result as unknown as ProtectionAuditResponse);
        }
      });
    }
  }, [latestAudit, baseline?.id, getProjectAudit]);

  const handleRunReaudit = async () => {
    if (!project) return;
    setRunningAudit(true);
    try {
      const result = await runProjectAudit(project.id, {
        trigger_type: 're_audit',
        repository_url: project.source_locator,
      });
      if (result.success) {
        // Refresh project to get new audit
        const refreshed = await getProject(project.id);
        if (refreshed.success && refreshed.data) {
          setProject(refreshed.data);
        }
      } else {
        setError(result.error || 'Failed to start re-audit');
      }
    } catch (err) {
      console.error('Re-audit failed:', err);
      setError('Failed to start re-audit');
    } finally {
      setRunningAudit(false);
    }
  };

  if (loading || (!project && !error && !apiError)) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto px-6">
            <Loader2 className="loading-spinner mx-auto mb-4" size={48} />
            <p className="text-muted">Loading project...</p>
          </div>
        </main>
      </div>
    );
  }

  const effectiveError = error || apiError;

  if (effectiveError || !project) {
    let title = 'Project unavailable';
    let message = 'This project may not exist or the link may be incorrect.';

    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto px-6">
            <AlertCircle size={48} className="mx-auto mb-4" style={{ color: 'var(--red)' }} />
            <h2 className="text-xl mb-2">{title}</h2>
            <p className="text-muted mb-6">{message}</p>
            <Link to="/" className="btn btn-primary" data-cta-intent="new_audit" data-cta-position="error">
              Run New Audit
            </Link>
          </div>
        </main>
      </div>
    );
  }

  const baselineProtectionPct = getProtectionPct(baselineAuditData?.summary);
  const baselineMnemePotentialPct = getMnemePotentialPct(baselineAuditData?.summary);
  const latestProtectionPct = getProtectionPct(latestAuditData?.summary);
  const latestMnemePotentialPct = getMnemePotentialPct(latestAuditData?.summary);

  const baselineSummary = baselineAuditData?.summary;
  const latestSummary = latestAuditData?.summary;

  const baselineProtected = baselineSummary?.protected_count || 0;
  const baselineRelevant = baselineSummary?.protection_relevant || 0;
  const baselineMnemeReady = baselineSummary?.mneme_ready_count || 0;
  const baselineRequiresModelling = baselineSummary?.requires_modelling_count || 0;
  const baselineGuidance = baselineSummary?.guidance_count || 0;

  const latestProtected = latestSummary?.protected_count || 0;
  const latestRelevant = latestSummary?.protection_relevant || 0;
  const latestMnemeReady = latestSummary?.mneme_ready_count || 0;
  const latestRequiresModelling = latestSummary?.requires_modelling_count || 0;
  const latestGuidance = latestSummary?.guidance_count || 0;

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <div className="audit-container">
          <header className="audit-hero" style={{ paddingTop: '2rem', paddingBottom: '2rem', textAlign: 'center' }}>
            <span className="audit-hero-tag">Architecture Protection Project</span>
            <h1>{project.name}</h1>
            <p className="text-muted mt-1">{project.source_locator}</p>
            
            <div className="mt-4 flex flex-wrap gap-2 justify-center">
              <span className={`badge flex items-center gap-1`} style={{ 
                background: `${LIFECYCLE_COLORS[project.lifecycle]}15`,
                color: LIFECYCLE_COLORS[project.lifecycle],
                borderColor: `${LIFECYCLE_COLORS[project.lifecycle]}33`
              }}>
                {LIFECYCLE_LABELS[project.lifecycle] || project.lifecycle}
              </span>
              <span className="badge badge-guidance flex items-center gap-1">
                <GitBranch size={12} /> {project.audits.length} audit{project.audits.length !== 1 ? 's' : ''}
              </span>
            </div>
          </header>

          {baselineAuditData && (
            <section className="audit-section" aria-labelledby="baseline-title">
              <h2 id="baseline-title" className="audit-section-title">Baseline Audit</h2>
              <p className="audit-section-subtitle">First saved audit — reference point for measuring protection changes.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="stat-card protection-summary-card">
                  <div className="flex items-center justify-center gap-2 mb-2" style={{ color: 'var(--accent)' }}>
                    <Shield size={20} />
                  </div>
                  <div className="stat-value" style={{ color: 'var(--accent)' }}>
                    {baselineProtectionPct}%
                  </div>
                  <div className="stat-label">CURRENT PROTECTION</div>
                  <div className="progress-bar mt-2" role="progressbar" aria-valuenow={baselineProtectionPct} aria-valuemin={0} aria-valuemax={100}>
                    <div className="progress-fill" style={{ width: `${baselineProtectionPct}%` }}></div>
                  </div>
                  {baselineMnemeReady > 0 && (
                    <div className="mt-2 text-xs text-muted">
                      Mneme Potential: {baselineMnemePotentialPct}%
                    </div>
                  )}
                </div>
                
                <div className="stat-card">
                  <div className="flex items-center justify-center gap-2 mb-2" style={{ color: 'var(--teal)' }}>
                    <CheckCircle size={20} />
                  </div>
                  <div className="stat-value" style={{ color: 'var(--teal)' }}>{baselineProtected}</div>
                  <div className="stat-label">PROTECTED</div>
                  <div className="text-xs text-muted mt-1">of {baselineRelevant} relevant</div>
                </div>
                
                <div className="stat-card">
                  <div className="flex items-center justify-center gap-2 mb-2" style={{ color: 'var(--warning)' }}>
                    <Zap size={20} />
                  </div>
                  <div className="stat-value" style={{ color: 'var(--warning)' }}>{baselineMnemeReady}</div>
                  <div className="stat-label">MNEME-READY</div>
                </div>
              </div>

              <div className="protection-breakdown mt-4 flex flex-wrap gap-2 justify-center">
                <span className="badge badge-protected flex items-center gap-1">
                  <CheckCircle size={12} /> {baselineProtected} Protected
                </span>
                {baselineMnemeReady > 0 && (
                  <span className="badge badge-mneme-ready flex items-center gap-1">
                    <Zap size={12} /> {baselineMnemeReady} Mneme-ready
                  </span>
                )}
                {baselineRequiresModelling > 0 && (
                  <span className="badge badge-requires-modelling flex items-center gap-1">
                    <Brain size={12} /> {baselineRequiresModelling} Requires modelling
                  </span>
                )}
                {baselineGuidance > 0 && (
                  <span className="badge badge-guidance flex items-center gap-1">
                    <Circle size={12} /> {baselineGuidance} Guidance
                  </span>
                )}
              </div>

              <div className="mt-4 flex flex-wrap gap-2 justify-center text-muted text-sm">
                <span className="flex items-center gap-1">
                  <Clock size={14} /> {baselineAuditData.timestamp ? formatDateTime(baselineAuditData.timestamp) : 'Unknown date'}
                </span>
                <span className="flex items-center gap-1">
                  <GitBranch size={14} /> {baselineAuditData.commit_sha.substring(0, 8)}
                </span>
                <span className="flex items-center gap-1">
                  <Shield size={14} /> Mneme {baselineAuditData.mneme_version}
                </span>
              </div>
            </section>
          )}

          {latestAuditData && latestAuditData.audit_id !== baseline?.id && (
            <section className="audit-section" aria-labelledby="latest-title">
              <h2 id="latest-title" className="audit-section-title">Latest Re-audit</h2>
              <p className="audit-section-subtitle">Most recent audit against the current repository state.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="stat-card protection-summary-card">
                  <div className="flex items-center justify-center gap-2 mb-2" style={{ color: 'var(--accent)' }}>
                    <Shield size={20} />
                  </div>
                  <div className="stat-value" style={{ color: 'var(--accent)' }}>
                    {latestProtectionPct}%
                  </div>
                  <div className="stat-label">CURRENT PROTECTION</div>
                  <div className="progress-bar mt-2" role="progressbar" aria-valuenow={latestProtectionPct} aria-valuemin={0} aria-valuemax={100}>
                    <div className="progress-fill" style={{ width: `${latestProtectionPct}%` }}></div>
                  </div>
                  {latestMnemeReady > 0 && (
                    <div className="mt-2 text-xs text-muted">
                      Mneme Potential: {latestMnemePotentialPct}%
                    </div>
                  )}
                </div>
                
                <div className="stat-card">
                  <div className="flex items-center justify-center gap-2 mb-2" style={{ color: 'var(--teal)' }}>
                    <CheckCircle size={20} />
                  </div>
                  <div className="stat-value" style={{ color: 'var(--teal)' }}>{latestProtected}</div>
                  <div className="stat-label">PROTECTED</div>
                  <div className="text-xs text-muted mt-1">of {latestRelevant} relevant</div>
                </div>
                
                <div className="stat-card">
                  <div className="flex items-center justify-center gap-2 mb-2" style={{ color: 'var(--warning)' }}>
                    <Zap size={20} />
                  </div>
                  <div className="stat-value" style={{ color: 'var(--warning)' }}>{latestMnemeReady}</div>
                  <div className="stat-label">MNEME-READY</div>
                </div>
              </div>

              <div className="protection-breakdown mt-4 flex flex-wrap gap-2 justify-center">
                <span className="badge badge-protected flex items-center gap-1">
                  <CheckCircle size={12} /> {latestProtected} Protected
                </span>
                {latestMnemeReady > 0 && (
                  <span className="badge badge-mneme-ready flex items-center gap-1">
                    <Zap size={12} /> {latestMnemeReady} Mneme-ready
                  </span>
                )}
                {latestRequiresModelling > 0 && (
                  <span className="badge badge-requires-modelling flex items-center gap-1">
                    <Brain size={12} /> {latestRequiresModelling} Requires modelling
                  </span>
                )}
                {latestGuidance > 0 && (
                  <span className="badge badge-guidance flex items-center gap-1">
                    <Circle size={12} /> {latestGuidance} Guidance
                  </span>
                )}
              </div>

              <div className="mt-4 flex flex-wrap gap-2 justify-center text-muted text-sm">
                <span className="flex items-center gap-1">
                  <Clock size={14} /> {latestAuditData.timestamp ? formatDateTime(latestAuditData.timestamp) : 'Unknown date'}
                </span>
                <span className="flex items-center gap-1">
                  <GitBranch size={14} /> {latestAuditData.commit_sha.substring(0, 8)}
                </span>
                <span className="flex items-center gap-1">
                  <Shield size={14} /> Mneme {latestAuditData.mneme_version}
                </span>
              </div>

              {baselineAuditData && (
                <div className="mt-6 text-center">
                  <Link 
                    to={`/project/${projectId}/compare`}
                    className="btn btn-primary flex items-center gap-2"
                    data-cta-intent="view_comparison"
                    data-cta-position="project_latest"
                  >
                    <ArrowRight size={16} /> Compare Baseline → Latest
                  </Link>
                </div>
              )}
            </section>
          )}

          {baseline && !latestAuditData && (
            <section className="audit-section" aria-labelledby="re-audit-title">
              <h2 id="re-audit-title" className="audit-section-title">Run Re-audit</h2>
              <p className="audit-section-subtitle">
                Run a new audit against the current repository state to measure protection changes since baseline.
              </p>
              
              <div className="text-center">
                <button 
                  onClick={handleRunReaudit}
                  disabled={runningAudit}
                  className="btn btn-primary flex items-center gap-2 justify-center mx-auto"
                  data-cta-intent="run_re_audit"
                  data-cta-position="project_baseline_only"
                >
                  {runningAudit ? (
                    <>
                      <Loader2 className="loading-spinner w-5 h-5" />
                      Running re-audit...
                    </>
                  ) : (
                    <>
                      <RotateCcw size={16} /> Run Re-audit
                    </>
                  )}
                </button>
              </div>
            </section>
          )}

          {latestAuditData && latestAuditData.audit_id !== baseline?.id && (
            <section className="audit-section" aria-labelledby="actions-title">
              <h2 id="actions-title" className="audit-section-title">Actions</h2>
              <div className="flex flex-wrap gap-3 justify-center">
                <button 
                  onClick={handleRunReaudit}
                  disabled={runningAudit}
                  className="btn btn-primary flex items-center gap-2"
                  data-cta-intent="run_re_audit"
                  data-cta-position="project_actions"
                >
                  {runningAudit ? (
                    <>
                      <Loader2 className="loading-spinner w-5 h-5" />
                      Running re-audit...
                    </>
                  ) : (
                    <>
                      <RotateCcw size={16} /> Run Re-audit
                    </>
                  )}
                </button>
                <Link 
                  to={`/project/${projectId}/compare`}
                  className="btn btn-ghost flex items-center gap-2"
                  data-cta-intent="view_comparison"
                  data-cta-position="project_actions"
                >
                  <ArrowRight size={16} /> Compare Changes
                </Link>
              </div>
            </section>
          )}
        </div>
      </main>

      <footer className="audit-footer">
        <p>Mneme HQ — Architectural drift prevention for the agentic AI SDLC</p>
      </footer>
    </div>
  );
}