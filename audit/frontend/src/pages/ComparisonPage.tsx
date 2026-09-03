import { useEffect, useState, useMemo } from 'react';
import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav, BackLink } from '../components/AuditNav';
import { Loader2, AlertCircle, ArrowRight, ArrowUpRight, ArrowDownRight, Minus, Plus, Circle, ChevronRight } from 'lucide-react';
import type { AuditComparison, DecisionComparison, ProtectionDecision, ProtectionClassification, ProjectWithHistory } from '../types/audit';

const COMPARISON_STATE_LABELS: Record<string, string> = {
  improved: 'Improved',
  regressed: 'Regressed',
  unchanged: 'Unchanged',
  added: 'Added',
  removed: 'Removed',
  uncomparable: 'Uncomparable',
};

const COMPARISON_STATE_ICONS = {
  improved: ArrowUpRight,
  regressed: ArrowDownRight,
  unchanged: Minus,
  added: Plus,
  removed: AlertCircle,
  uncomparable: Circle,
};

const COMPARISON_STATE_COLORS: Record<string, string> = {
  improved: 'var(--teal)',
  regressed: 'var(--red)',
  unchanged: 'var(--muted)',
  added: 'var(--accent)',
  removed: 'var(--red)',
  uncomparable: 'var(--muted)',
};

const PROTECTION_ORDER: Record<ProtectionClassification, number> = {
  Protected: 3,
  'Mneme-ready': 2,
  'Requires modelling': 1,
  Guidance: 0,
};

function getClassification(decision: ProtectionDecision | null): ProtectionClassification {
  return decision?.protection_classification || 'Guidance';
}

function getChangeDescription(comp: DecisionComparison): string {
  const baseClass = getClassification(comp.baseline_decision);
  const currClass = getClassification(comp.current_decision);
  
  if (comp.state === 'added') {
    return `New decision added: ${currClass}`;
  }
  if (comp.state === 'removed') {
    return `Decision removed: was ${baseClass}`;
  }
  if (comp.state === 'improved') {
    if (currClass === 'Protected' && baseClass === "Mneme-ready") {
      return 'Gained deterministic protection';
    }
    if (currClass === "Mneme-ready" && baseClass === 'Requires modelling') {
      return 'Modeling completed — now Mneme-ready';
    }
    if (currClass === 'Protected' && baseClass === 'Requires modelling') {
      return 'Modeling completed and protection added';
    }
    return `Improved: ${baseClass} → ${currClass}`;
  }
  if (comp.state === 'regressed') {
    if (baseClass === 'Protected' && currClass !== 'Protected') {
      return 'Lost deterministic protection';
    }
    return `Regressed: ${baseClass} → ${currClass}`;
  }
  if (comp.state === 'uncomparable') {
    return 'Cannot compare (schema mismatch)';
  }
  return `Unchanged at ${baseClass}`;
}

function getActionCTA(comp: DecisionComparison): { label: string; intent: string } | null {
  const currClass = getClassification(comp.current_decision);
  
  if (comp.state === 'improved' && currClass === 'Protected') {
    return { label: 'View guardrail', intent: 'view_guardrail' };
  }
  if (currClass === "Mneme-ready") {
    return { label: 'View guardrail', intent: 'view_guardrail' };
  }
  if (currClass === 'Requires modelling') {
    return { label: 'Review gap', intent: 'review_gap' };
  }
  return null;
}

interface ComparisonRowProps {
  comp: DecisionComparison;
}

function ComparisonRow({ comp }: ComparisonRowProps) {
  const Icon = COMPARISON_STATE_ICONS[comp.state as keyof typeof COMPARISON_STATE_ICONS] || Circle;
  const color = COMPARISON_STATE_COLORS[comp.state] || 'var(--muted)';
  const baseClass = getClassification(comp.baseline_decision);
  const currClass = getClassification(comp.current_decision);
  const action = getActionCTA(comp);
  const isUncomparable = comp.state === 'uncomparable';
  const uncomparableReason = isUncomparable && comp.details.reason ? String(comp.details.reason) : null;

  if (comp.state === 'unchanged') {
    return null; // Hide unchanged by default, show count in summary
  }

  return (
    <article className={`comparison-row ${comp.state}`} style={{ borderLeftColor: color }}>
      <div className="comparison-row-main">
        <div className="comparison-state-badge" style={{ background: `${color}15`, color }}>
          {React.createElement(Icon, { size: 14 })}
          <span>{COMPARISON_STATE_LABELS[comp.state] || comp.state}</span>
        </div>
        <div className="comparison-content">
          <h3 className="comparison-title">{comp.current_decision?.title || comp.baseline_decision?.title || comp.decision_key}</h3>
          <p className="comparison-description">{getChangeDescription(comp)}</p>
          <div className="comparison-classification-flow">
            {comp.baseline_decision && (
              <>
                <span className={`badge ${baseClass.toLowerCase().replace(' ', '-')}`}>{baseClass}</span>
                <ChevronRight size={12} style={{ color: 'var(--muted)' }} />
              </>
            )}
            <span className={`badge ${currClass.toLowerCase().replace(' ', '-')}`}>{currClass}</span>
          </div>
        </div>
      </div>
      {action && (
        <div className="comparison-action">
          <button className="btn btn-ghost btn-sm" data-cta-intent={action.intent} data-cta-position="comparison_row">
            {action.label}
          </button>
        </div>
      )}
      {uncomparableReason && (
        <div className="comparison-uncomparable-reason" style={{ color: 'var(--muted)', fontSize: '0.75rem', marginTop: '0.5rem' }}>
          {uncomparableReason}
        </div>
      )}
    </article>
  );
}

export function ComparisonPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { compareAudits, getProject, error: apiError } = useAuditApi();
  
  const [comparison, setComparison] = useState<AuditComparison | null>(null);
  const [project, setProject] = useState<ProjectWithHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUnchanged] = useState(false);

  useEffect(() => {
    if (!projectId) {
      navigate('/', { replace: true });
      return;
    }
  }, [projectId, navigate]);

  // Load project first to get baseline info
  useEffect(() => {
    if (!projectId) return;
    getProject(projectId).then((result) => {
      if (result.success && result.data) {
        setProject(result.data);
      }
    });
  }, [projectId, getProject]);

  // Load comparison
  useEffect(() => {
    if (!projectId) return;
    
    setLoading(true);
    setError(null);
    compareAudits(projectId).then((result) => {
      setLoading(false);
      if (result.success && result.data) {
        setComparison(result.data);
      } else {
        setError(result.error || 'Failed to load comparison');
      }
    });
  }, [projectId, compareAudits]);

  const summary = useMemo(() => {
    if (!comparison) return {
      improved: 0,
      regressed: 0,
      added: 0,
      removed: 0,
      unchanged: 0,
      uncomparable: 0,
    };
    const counts = comparison.summary;
    return {
      improved: counts.improved || 0,
      regressed: counts.regressed || 0,
      added: counts.added || 0,
      removed: counts.removed || 0,
      unchanged: counts.unchanged || 0,
      uncomparable: counts.uncomparable || 0,
    };
  }, [comparison]);

  // We need to compute baseline and current protection from the comparison
  const baselineDecisions = comparison?.decisions.filter(d => d.baseline_decision) || [];
  const currentDecisions = comparison?.decisions.filter(d => d.current_decision) || [];
  
  const baselineProtected = baselineDecisions.filter(d => getClassification(d.baseline_decision) === 'Protected').length;
  const baselineRelevant = baselineDecisions.filter(d => PROTECTION_ORDER[getClassification(d.baseline_decision)] > 0).length;
  const currentProtected = currentDecisions.filter(d => getClassification(d.current_decision) === 'Protected').length;
  const currentRelevant = currentDecisions.filter(d => PROTECTION_ORDER[getClassification(d.current_decision)] > 0).length;
  
  const baselineProtection = baselineRelevant > 0 ? Math.round((baselineProtected / baselineRelevant) * 100) : 0;
  const currentProtection = currentRelevant > 0 ? Math.round((currentProtected / currentRelevant) * 100) : 0;

  const changedDecisions = useMemo(() => {
    if (!comparison) return [];
    return comparison.decisions.filter(d => d.state !== 'unchanged');
  }, [comparison]);

  const improvedDecisions = useMemo(() => 
    changedDecisions.filter(d => d.state === 'improved'), [changedDecisions]);
  const regressedDecisions = useMemo(() => 
    changedDecisions.filter(d => d.state === 'regressed'), [changedDecisions]);
  const addedDecisions = useMemo(() => 
    changedDecisions.filter(d => d.state === 'added'), [changedDecisions]);
  const removedDecisions = useMemo(() => 
    changedDecisions.filter(d => d.state === 'removed'), [changedDecisions]);
  const uncomparableDecisions = useMemo(() => 
    changedDecisions.filter(d => d.state === 'uncomparable'), [changedDecisions]);

  if (loading || (!comparison && !error && !apiError)) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto px-6">
            <Loader2 className="loading-spinner mx-auto mb-4" size={48} />
            <p className="text-muted">Loading comparison...</p>
          </div>
        </main>
      </div>
    );
  }

  const effectiveError = error || apiError;

  if (effectiveError || !comparison) {
    let title = 'Comparison unavailable';
    let message = 'Unable to compare audits.';

    if (effectiveError?.includes('baseline')) {
      title = 'No baseline set';
      message = 'This project needs a baseline audit before comparison is possible.';
    } else if (effectiveError?.includes('completed')) {
      title = 'No completed audits';
      message = 'Run at least one audit after the baseline to enable comparison.';
    }

    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto px-6">
            <AlertCircle size={48} className="mx-auto mb-4" style={{ color: 'var(--red)' }} />
            <h2 className="text-xl mb-2">{title}</h2>
            <p className="text-muted mb-6">{message}</p>
            {project && (
              <Link to={`/project/${projectId}`} className="btn btn-primary" data-cta-intent="back_to_project" data-cta-position="error">
                Back to Project
              </Link>
            )}
          </div>
        </main>
      </div>
    );
  }

  const projectName = project?.name || 'Project';
  const baselineCommitShort = comparison.baseline_commit_sha.substring(0, 8);
  const currentCommitShort = comparison.current_commit_sha.substring(0, 8);

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <div className="audit-container">
          <BackLink to={`/project/${projectId}`} />
          
          <header className="audit-hero" style={{ paddingTop: '2rem', paddingBottom: '2rem', textAlign: 'center' }}>
            <span className="audit-hero-tag">Architecture Protection Comparison</span>
            <h1>{projectName}</h1>
            <p className="text-muted mt-1">Baseline {baselineCommitShort} → Latest {currentCommitShort}</p>
            
            <div className="comparison-headline mt-6">
              <div className="comparison-score-display">
                <div className="comparison-score-pair">
                  <div className="comparison-score">
                    <span className="comparison-score-value">{baselineProtection}%</span>
                    <span className="comparison-score-label">Baseline Protection</span>
                  </div>
                  <div className="comparison-arrow" style={{ color: 'var(--accent)' }}>
                    <ArrowRight size={24} />
                  </div>
                  <div className="comparison-score">
                    <span className="comparison-score-value" style={{ color: currentProtection > baselineProtection ? 'var(--teal)' : currentProtection < baselineProtection ? 'var(--red)' : 'var(--accent)' }}>
                      {currentProtection}%
                    </span>
                    <span className="comparison-score-label">Current Protection</span>
                  </div>
                </div>
                <div className="comparison-delta" style={{ color: currentProtection > baselineProtection ? 'var(--teal)' : currentProtection < baselineProtection ? 'var(--red)' : 'var(--muted)' }}>
                  {currentProtection > baselineProtection ? '+' : ''}{currentProtection - baselineProtection}% change
                </div>
              </div>

              <div className="comparison-summary-badges mt-4 flex flex-wrap gap-2 justify-center">
                {summary?.improved > 0 && (
                  <span className="badge badge-protected flex items-center gap-1">
                    <ArrowUpRight size={12} /> {summary.improved} Improved
                  </span>
                )}
                {summary?.regressed > 0 && (
                  <span className="badge flex items-center gap-1" style={{ background: 'rgba(255,112,112,0.15)', color: 'var(--red)', borderColor: 'rgba(255,112,112,0.3)' }}>
                    <ArrowDownRight size={12} /> {summary.regressed} Regressed
                  </span>
                )}
                {summary?.added > 0 && (
                  <span className="badge flex items-center gap-1" style={{ background: 'rgba(200,240,96,0.15)', color: 'var(--accent)', borderColor: 'rgba(200,240,96,0.3)' }}>
                    <Plus size={12} /> {summary.added} Added
                  </span>
                )}
                {summary?.removed > 0 && (
                  <span className="badge flex items-center gap-1" style={{ background: 'rgba(255,112,112,0.15)', color: 'var(--red)', borderColor: 'rgba(255,112,112,0.3)' }}>
                    <Minus size={12} /> {summary.removed} Removed
                  </span>
                )}
                {summary?.unchanged > 0 && (
                  <span className="badge badge-guidance flex items-center gap-1">
                    <Minus size={12} /> {summary.unchanged} Unchanged
                  </span>
                )}
              </div>
            </div>
          </header>

          {summary && (
            <section className="audit-section" aria-labelledby="summary-title">
              <h2 id="summary-title" className="audit-section-title">Change Summary</h2>
              <div className="comparison-narrative">
                <ul className="comparison-narrative-list">
                  {summary.improved > 0 && (
                    <li>
                      <strong>{summary.improved} decision{summary.improved !== 1 ? 's' : ''} gained protection.</strong>
                      {improvedDecisions.map(d => {
                        const currClass = getClassification(d.current_decision);
                        if (currClass === 'Protected') return ' Deterministic enforcement now active.';
                        if (currClass === "Mneme-ready") return ' Now Mneme-ready for guardrail generation.';
                        return '';
                      }).join(' ')}
                    </li>
                  )}
                  {summary.regressed > 0 && (
                    <li>
                      <strong>{summary.regressed} protected decision{summary.regressed !== 1 ? 's' : ''} regressed.</strong>
                      Immediate attention required — previously enforced rules no longer apply.
                    </li>
                  )}
                  {summary.added > 0 && (
                    <li>
                      <strong>{summary.added} new decision{summary.added !== 1 ? 's' : ''} identified.</strong>
                      {addedDecisions.filter(d => PROTECTION_ORDER[getClassification(d.current_decision)] > 0).length > 0 && 
                        ` ${addedDecisions.filter(d => PROTECTION_ORDER[getClassification(d.current_decision)] > 0).length} protection-relevant.`
                      }
                    </li>
                  )}
                  {summary.removed > 0 && (
                    <li>
                      <strong>{summary.removed} decision{summary.removed !== 1 ? 's' : ''} removed.</strong>
                    </li>
                  )}
                  {summary.unchanged > 0 && (
                    <li>
                      <strong>{summary.unchanged} decision{summary.unchanged !== 1 ? 's' : ''} unchanged.</strong>
                      {showUnchanged ? ` <button className="btn btn-ghost btn-xs" onClick={() => setShowUnchanged(false)}>Hide</button>` : 
                        ` <button className="btn btn-ghost btn-xs" onClick={() => setShowUnchanged(true)}>Show</button>`}
                    </li>
                  )}
                  {summary.uncomparable > 0 && (
                    <li>
                      <strong>{summary.uncomparable} decision{summary.uncomparable !== 1 ? 's' : ''} uncomparable.</strong>
                      Schema mismatch between baseline and current audit.
                    </li>
                  )}
                  {summary.improved === 0 && summary.regressed === 0 && summary.added === 0 && summary.removed === 0 && summary.uncomparable === 0 && (
                    <li className="text-muted">No changes detected between baseline and current audit.</li>
                  )}
                </ul>
              </div>
            </section>
          )}

          <section className="audit-section" aria-labelledby="changes-title">
            <h2 id="changes-title" className="audit-section-title">Detailed Changes</h2>
            
            {changedDecisions.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">✓</div>
                <h3 className="empty-title">No protection changes</h3>
                <p className="empty-text">All protection-relevant decisions remain at the same classification level.</p>
              </div>
            )}

            {improvedDecisions.length > 0 && (
              <div className="comparison-section">
                <h3 className="comparison-section-title" style={{ color: 'var(--teal)' }}>
                  <ArrowUpRight size={16} className="inline" /> Improved ({improvedDecisions.length})
                </h3>
                <div className="comparison-list">
                  {improvedDecisions.map(comp => (
                    <ComparisonRow key={comp.decision_key} comp={comp} />
                  ))}
                </div>
              </div>
            )}

            {regressedDecisions.length > 0 && (
              <div className="comparison-section">
                <h3 className="comparison-section-title" style={{ color: 'var(--red)' }}>
                  <ArrowDownRight size={16} className="inline" /> Regressed ({regressedDecisions.length})
                </h3>
                <div className="comparison-list">
                  {regressedDecisions.map(comp => (
                    <ComparisonRow key={comp.decision_key} comp={comp} />
                  ))}
                </div>
              </div>
            )}

            {addedDecisions.length > 0 && (
              <div className="comparison-section">
                <h3 className="comparison-section-title" style={{ color: 'var(--accent)' }}>
                  <Plus size={16} className="inline" /> Added ({addedDecisions.length})
                </h3>
                <div className="comparison-list">
                  {addedDecisions.map(comp => (
                    <ComparisonRow key={comp.decision_key} comp={comp} />
                  ))}
                </div>
              </div>
            )}

            {removedDecisions.length > 0 && (
              <div className="comparison-section">
                <h3 className="comparison-section-title" style={{ color: 'var(--red)' }}>
                  <Minus size={16} className="inline" /> Removed ({removedDecisions.length})
                </h3>
                <div className="comparison-list">
                  {removedDecisions.map(comp => (
                    <ComparisonRow key={comp.decision_key} comp={comp} />
                  ))}
                </div>
              </div>
            )}

            {showUnchanged && summary && summary.unchanged > 0 && (
              <div className="comparison-section">
                <h3 className="comparison-section-title" style={{ color: 'var(--muted)' }}>
                  <Minus size={16} className="inline" /> Unchanged ({summary.unchanged})
                </h3>
                <div className="comparison-list">
                  {comparison.decisions.filter(d => d.state === 'unchanged').map(comp => (
                    <ComparisonRow key={comp.decision_key} comp={comp} />
                  ))}
                </div>
              </div>
            )}

            {uncomparableDecisions.length > 0 && (
              <div className="comparison-section">
                <h3 className="comparison-section-title" style={{ color: 'var(--muted)' }}>
                  <Circle size={16} className="inline" /> Uncomparable ({uncomparableDecisions.length})
                </h3>
                <div className="comparison-list">
                  {uncomparableDecisions.map(comp => (
                    <ComparisonRow key={comp.decision_key} comp={comp} />
                  ))}
                </div>
              </div>
            )}
          </section>

          <div className="audit-section text-center" style={{ paddingBottom: '4rem' }}>
            <Link to={`/project/${projectId}`} className="btn btn-ghost" data-cta-intent="back_to_project" data-cta-position="comparison">
              ← Back to Project
            </Link>
          </div>
        </div>
      </main>

      <footer className="audit-footer">
        <p>Mneme HQ — Architectural drift prevention for the agentic AI SDLC</p>
      </footer>
    </div>
  );
}