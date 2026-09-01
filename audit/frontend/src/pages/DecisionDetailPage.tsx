import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav, BackLink } from '../components/AuditNav';
import { InfoTooltip } from '../components/InfoTooltip';
import { PilotLink } from '../components/PilotLink';
import { Copy, CheckCircle, AlertTriangle, Circle, FileText, AlertCircle } from 'lucide-react';
import type { ArchitecturalDecision, AuditResult, Governability } from '../types/audit';
import { FIELD_HELP, getDecisionRecommendations, getPlainLanguageSummary } from '../utils/auditInsights';

const GOVERNABILITY_LABELS: Record<Governability, string> = {
  enforceable: 'ENFORCEABLE',
  partial: 'PARTIALLY ENFORCEABLE',
  guidance: 'GUIDANCE ONLY',
};

const GOVERNABILITY_DESC: Record<Governability, string> = {
  enforceable: 'Mneme can evaluate this decision before an agent performs the relevant change.',
  partial: 'Mneme can partially evaluate this decision; some aspects require human judgment.',
  guidance: 'This decision expresses intent but cannot be deterministically enforced by Mneme.',
};

const ICONS: Record<Governability, typeof CheckCircle> = {
  enforceable: CheckCircle,
  partial: AlertTriangle,
  guidance: Circle,
};

const ICON_COLORS: Record<Governability, string> = {
  enforceable: 'var(--teal)',
  partial: 'var(--warning)',
  guidance: 'var(--muted)',
};

export function DecisionDetailPage() {
  const { id, decisionId } = useParams<{ id: string; decisionId: string }>();
  const { getAudit } = useAuditApi();
  const [decision, setDecision] = useState<ArchitecturalDecision | null>(null);
  const [audit, setAudit] = useState<AuditResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (id) {
      setLoading(true);
      getAudit(id).then((result) => {
        if (result.success && result.data) {
          const found = result.data.decisions.find((d) => d.id === decisionId);
          setDecision(found || null);
          setAudit(result.data);
        }
        setLoading(false);
      });
    }
  }, [id, decisionId, getAudit]);

  const copyRule = async () => {
    if (!decision || !decision.proposedRule) return;
    const ruleText = `${decision.proposedRule.type} "${decision.proposedRule.pattern}"`;
    await navigator.clipboard.writeText(ruleText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="audit-container text-center">
            <div className="loading-spinner mx-auto mb-4" style={{ width: 40, height: 40 }} />
            <p className="text-muted">Loading decision...</p>
          </div>
        </main>
      </div>
    );
  }

  if (!decision) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="audit-container text-center">
            <AlertCircle size={48} className="mx-auto mb-4" style={{ color: 'var(--red)' }} />
            <h2 className="text-xl mb-2">Decision unavailable</h2>
            <p className="text-muted mb-6">This decision may have been removed or the link may be incorrect.</p>
            {id && (
              <Link to={`/audit/${id}`} className="btn btn-primary" data-cta-intent="back_to_audit" data-cta-position="error">
                Back to Audit
              </Link>
            )}
          </div>
        </main>
      </div>
    );
  }

  const Icon = ICONS[decision.governability];
  const iconColor = ICON_COLORS[decision.governability];
  const badgeClass = `badge-${decision.governability === 'enforceable' ? 'enforceable' : decision.governability === 'partial' ? 'partial' : 'guidance'}`;
  const recommendations = getDecisionRecommendations(decision);

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <div className="audit-container">
          <BackLink to={`/audit/${id ?? ''}`} />
          
          <header className="detail-header">
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <span className={`badge ${badgeClass} mb-2`}>{GOVERNABILITY_LABELS[decision.governability]}</span>
                <h1 className="detail-title">{decision.title}</h1>
                <p className="text-muted" style={{ maxWidth: '700px' }}>{getPlainLanguageSummary(decision)}</p>
              </div>
            </div>
            
            <div className="detail-meta mt-3">
              <span className="font-mono text-sm" style={{ color: 'var(--muted)' }}>
                <FileText size={14} className="inline" /> {decision.source.file}
              </span>
              <span className="font-mono text-sm" style={{ color: 'var(--muted)' }}>
                Lines {decision.source.lines}
              </span>
              <span className="detail-meta-item font-mono text-sm text-teal">
                Confidence: {Math.round(decision.confidence * 100)}%
                <InfoTooltip label="Confidence">{FIELD_HELP.confidence}</InfoTooltip>
              </span>
            </div>
          </header>

          <section className="detail-section" aria-labelledby="assessment">
            <div className="detail-section-heading">
              <h2 id="assessment" className="detail-section-title">What this means</h2>
              <InfoTooltip label="Governability assessment">{FIELD_HELP.governability}</InfoTooltip>
            </div>
            <p className="detail-section-description">The classification, current blocker, and control readiness in one view.</p>
            <div className="detail-assessment-card">
              <div className="detail-assessment-row">
                <span className="detail-assessment-icon" style={{ color: iconColor, background: `${iconColor}15` }}><Icon size={20} /></span>
                <div>
                  <span className="detail-assessment-label">Status</span>
                  <strong style={{ color: iconColor }}>{GOVERNABILITY_LABELS[decision.governability]}</strong>
                  <p>{GOVERNABILITY_DESC[decision.governability]}</p>
                </div>
              </div>
              <div className="detail-assessment-row">
                <div>
                  <span className="detail-assessment-label">Scope <InfoTooltip label="Applies to">{FIELD_HELP.appliesTo}</InfoTooltip></span>
                  {decision.appliesTo.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {decision.appliesTo.map((path, index) => <code key={index}>{path}</code>)}
                    </div>
                  ) : (
                    <><strong>Not specified</strong><p>Add paths, services, or change types before enabling enforcement.</p></>
                  )}
                </div>
              </div>
              <div className="detail-assessment-row">
                <div>
                  <span className="detail-assessment-label">Control readiness <InfoTooltip label="Proposed Mneme rule">{FIELD_HELP.proposedRule}</InfoTooltip></span>
                  {decision.proposedRule ? (
                    <>
                      <code>{decision.proposedRule.type} "{decision.proposedRule.pattern}"</code>
                      <p>{decision.proposedRule.description}</p>
                      <button onClick={copyRule} className="btn btn-secondary btn-sm mt-2" data-cta-intent="copy_rule" data-cta-position="decision_detail">
                        <Copy size={14} /> {copied ? 'Copied' : 'Copy rule'}
                      </button>
                    </>
                  ) : (
                    <><strong>No deterministic rule yet</strong><p>Clarify the scope and pass/fail condition before Mneme proposes a control.</p></>
                  )}
                </div>
              </div>
            </div>
          </section>

          <section className="detail-section" aria-labelledby="evidence">
            <div className="detail-section-heading">
              <h2 id="evidence" className="detail-section-title">Evidence</h2>
              <InfoTooltip label="Evidence">{FIELD_HELP.source}</InfoTooltip>
            </div>
            <p className="detail-section-description">Open this only when you need to validate Mneme’s interpretation against the repository.</p>
            <details className="detail-evidence-disclosure">
              <summary>
                <span><FileText size={16} /> {decision.source.file}</span>
                <span>Lines {decision.source.lines}</span>
                <span className="detail-evidence-action">View evidence</span>
              </summary>
              <div className="detail-evidence-body">
                <p>{getPlainLanguageSummary(decision)}</p>
                <pre>{decision.requirement}</pre>
              </div>
            </details>
          </section>

          <section className="detail-section" aria-labelledby="recommendations">
            <h2 id="recommendations" className="detail-section-title">Recommended next steps</h2>
            <p className="detail-section-description">Start with the first action; each completed step moves this item closer to safe enforcement.</p>
            <ol className="recommendation-list recommendation-list-compact">
              {recommendations.map((recommendation, index) => (
                <li key={recommendation.title}>
                  <span>{index + 1}</span>
                  <div><strong>{recommendation.title}</strong><p>{recommendation.description}</p></div>
                </li>
              ))}
            </ol>
            {audit && (
              <div className="detail-pilot-prompt">
                <div>
                  <strong>Test this item against real pull requests</strong>
                  <p>Your audit summary and this selected item will be attached to the pilot request.</p>
                </div>
                <PilotLink audit={audit} selectedDecisionId={decision.id} ctaPosition="decision_detail">Request a pilot</PilotLink>
              </div>
            )}
          </section>

          <div className="detail-section" style={{ paddingBottom: '4rem' }}>
            <Link to={`/audit/${id ?? ''}`} className="btn btn-ghost" data-cta-intent="back_to_overview" data-cta-position="decision_detail">
              ← Back to Audit Overview
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
