import { useEffect, useState } from 'react';
import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav, BackLink } from '../components/AuditNav';
import { Copy, CheckCircle, Zap, Brain, Circle, FileText, AlertCircle, Eye, Search } from 'lucide-react';
import type { ProtectionAuditResponse, ProtectionDecision, ProtectionClassification, EvidenceConfidence } from '../types/audit';
import { InfoTooltip } from '../components/InfoTooltip';
import { PilotLink } from '../components/PilotLink';
import { FIELD_HELP, getDecisionRecommendations, getPlainLanguageSummary } from '../utils/auditInsights';

const CLASSIFICATION_LABELS: Record<ProtectionClassification, string> = {
  Protected: 'PROTECTED',
  'Mneme-ready': 'MNEME-READY',
  'Requires modelling': 'REQUIRES MODELLING',
  Guidance: 'GUIDANCE ONLY',
};

const CLASSIFICATION_DESC: Record<ProtectionClassification, string> = {
  Protected: 'Deterministic enforcement detected.',
  'Mneme-ready': 'A concrete Mneme guardrail can protect this decision.',
  'Requires modelling': 'This intent appears mechanically enforceable, but a safe deterministic guardrail has not yet been identified.',
  Guidance: 'Architectural guidance — deterministic enforcement is not appropriate.',
};

const CLASSIFICATION_CTA: Record<ProtectionClassification, { label: string; intent: string; icon: typeof Eye } | null> = {
  Protected: null,
  'Mneme-ready': { label: 'View guardrail', intent: 'view_guardrail', icon: Eye },
  'Requires modelling': { label: 'Review protection gap', intent: 'review_gap', icon: Search },
  Guidance: null,
};

const ICONS: Record<ProtectionClassification, typeof CheckCircle> = {
  Protected: CheckCircle,
  'Mneme-ready': Zap,
  'Requires modelling': Brain,
  Guidance: Circle,
};

const ICON_COLORS: Record<ProtectionClassification, string> = {
  Protected: 'var(--teal)',
  'Mneme-ready': 'var(--warning)',
  'Requires modelling': 'var(--warning)',
  Guidance: 'var(--muted)',
};

const CONFIDENCE_ICONS: Record<EvidenceConfidence, typeof CheckCircle> = {
  high: CheckCircle,
  medium: Zap,
  low: Circle,
};

const CONFIDENCE_COLORS: Record<EvidenceConfidence, string> = {
  high: 'var(--teal)',
  medium: 'var(--warning)',
  low: 'var(--muted)',
};

export function DecisionDetailPage() {
  const { id, decisionId } = useParams<{ id: string; decisionId: string }>();
  const { getAudit } = useAuditApi();
  const [decision, setDecision] = useState<ProtectionDecision | null>(null);
  const [audit, setAudit] = useState<ProtectionAuditResponse | null>(null);
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
    if (!decision || !decision.proposed_rule) return;
    const ruleText = `${decision.proposed_rule.type} "${decision.proposed_rule.pattern}"`;
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

  const Icon = ICONS[decision.protection_classification];
  const recommendations = getDecisionRecommendations(decision);
  const iconColor = ICON_COLORS[decision.protection_classification];
  const badgeClass = `badge-${decision.protection_classification === 'Protected' ? 'protected' : 
    decision.protection_classification === 'Mneme-ready' ? 'mneme-ready' : 
    decision.protection_classification === 'Requires modelling' ? 'requires-modelling' : 'guidance'}`;

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <div className="audit-container">
          <BackLink to={`/audit/${id ?? ''}`} />
          
          <header className="detail-header">
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <span className={`badge ${badgeClass} mb-2`}>{CLASSIFICATION_LABELS[decision.protection_classification]}</span>
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
              <span className="font-mono text-sm" style={{ color: CONFIDENCE_COLORS[decision.evidence_confidence] }}>
                {(CONFIDENCE_ICONS[decision.evidence_confidence] as React.ComponentType<{ size: number; className?: string }>) &&
                  React.createElement(CONFIDENCE_ICONS[decision.evidence_confidence], { size: 12, className: 'inline' })}
                Evidence: {decision.evidence_confidence.charAt(0).toUpperCase() + decision.evidence_confidence.slice(1)}
              </span>
            </div>
          </header>

          <section className="detail-section" aria-labelledby="assessment">
            <div className="detail-section-heading">
              <h2 id="assessment" className="detail-section-title">What this means</h2>
              <InfoTooltip label="Protection classification">{FIELD_HELP.protection}</InfoTooltip>
            </div>
            <p className="detail-section-description">The classification, current blocker, and control readiness in one view.</p>
            <div className="detail-assessment-card">
              <div className="detail-assessment-row">
                <span className="detail-assessment-icon" style={{ color: iconColor, background: `${iconColor}15` }}><Icon size={20} /></span>
                <div>
                  <span className="detail-assessment-label">Status</span>
                  <strong style={{ color: iconColor }}>{CLASSIFICATION_LABELS[decision.protection_classification]}</strong>
                  <p>{CLASSIFICATION_DESC[decision.protection_classification]}</p>
                  {CLASSIFICATION_CTA[decision.protection_classification] && <button
                    className="btn btn-primary btn-sm mt-3"
                    onClick={() => {
                      const target = document.getElementById(decision.protection_classification === 'Requires modelling' ? 'recommendations' : 'guardrail');
                      target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                      target?.focus({ preventScroll: true });
                    }}>
                    {CLASSIFICATION_CTA[decision.protection_classification]!.label}
                  </button>}
                </div>
              </div>
              <div className="detail-assessment-row">
                <div>
                  <span className="detail-assessment-label">Scope <InfoTooltip label="Applies to">{FIELD_HELP.appliesTo}</InfoTooltip></span>
                  {decision.applies_to.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {decision.applies_to.map((path, index) => <code key={index}>{path}</code>)}
                    </div>
                  ) : (
                    <><strong>Not specified</strong><p>Add paths, services, or change types before enabling enforcement.</p></>
                  )}
                </div>
              </div>
              <div className="detail-assessment-row">
                <div>
                  <span id="guardrail" tabIndex={-1} className="detail-assessment-label">Control readiness <InfoTooltip label="Proposed Mneme rule">{FIELD_HELP.proposedRule}</InfoTooltip></span>
                  {decision.proposed_rule ? (
                    <>
                      <code>{decision.proposed_rule.type} "{decision.proposed_rule.pattern}"</code>
                      <p>{decision.proposed_rule.description}</p>
                      <button onClick={copyRule} className="btn btn-secondary btn-sm mt-2" data-cta-intent="copy_rule" data-cta-position="decision_detail">
                        <Copy size={14} /> {copied ? 'Copied' : 'Copy rule'}
                      </button>
                    </>
                  ) : (
                    <><strong>No deterministic rule yet</strong><p>{decision.protection_classification === 'Guidance' ? 'Deterministic enforcement is not appropriate for this guidance.' : 'A safe supported guardrail has not been identified. Review the protection gap with the decision owner.'}</p></>
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
            <h2 id="recommendations" tabIndex={-1} className="detail-section-title">Recommended next steps</h2>
            <p className="detail-section-description">Review these suggestions in the context of the backend's protection classification.</p>
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
                  <strong>We’ll start from this recommendation</strong>
                  <p>You won’t need to explain the finding again. We’ll review the attached audit before a short follow-up, agree on the intended scope, and test the recommendation safely against real changes.</p>
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
