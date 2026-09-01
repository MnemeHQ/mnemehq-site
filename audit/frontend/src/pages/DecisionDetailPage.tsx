import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav, BackLink } from '../components/AuditNav';
import { InfoTooltip } from '../components/InfoTooltip';
import { Copy, CheckCircle, AlertTriangle, Circle, FileText, AlertCircle } from 'lucide-react';
import type { ArchitecturalDecision, Governability } from '../types/audit';
import { FIELD_HELP, getDecisionRecommendations, getEvidenceLabel, getPlainLanguageSummary } from '../utils/auditInsights';

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
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (id) {
      setLoading(true);
      getAudit(id).then((result) => {
        if (result.success && result.data) {
          const found = result.data.decisions.find((d) => d.id === decisionId);
          setDecision(found || null);
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
  const evidenceLabel = getEvidenceLabel(decision);
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
              <div className="flex items-center gap-2" style={{ color: iconColor }}>
                <Icon size={28} />
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

          <section className="detail-section" aria-labelledby="requirement">
            <div className="detail-section-heading">
              <h2 id="requirement" className="detail-section-title">{evidenceLabel}</h2>
              <InfoTooltip label={evidenceLabel}>{FIELD_HELP.requirement}</InfoTooltip>
            </div>
            <p className="detail-section-description">What Mneme extracted from the repository and used to classify this governance item.</p>
            {decision.category === 'config_evidence' ? (
              <div className="detail-content">
                <p className="detail-evidence-summary">{getPlainLanguageSummary(decision)}</p>
                <details className="evidence-details">
                  <summary>View source evidence excerpt</summary>
                  <pre>{decision.requirement}</pre>
                </details>
              </div>
            ) : (
              <div className="detail-content">{decision.requirement}</div>
            )}
          </section>

          <section className="detail-section" aria-labelledby="source">
            <div className="detail-section-heading">
              <h2 id="source" className="detail-section-title">Source evidence</h2>
              <InfoTooltip label="Source evidence">{FIELD_HELP.source}</InfoTooltip>
            </div>
            <p className="detail-section-description">Validate the finding against this file and line range with the team that owns the decision.</p>
            <div className="detail-content">
              <p>{decision.source.file}</p>
              <p>Lines {decision.source.lines}</p>
            </div>
          </section>

          <section className="detail-section" aria-labelledby="governability">
            <div className="detail-section-heading">
              <h2 id="governability" className="detail-section-title">Governability</h2>
              <InfoTooltip label="Governability">{FIELD_HELP.governability}</InfoTooltip>
            </div>
            <p className="detail-section-description">Whether this item is precise enough for Mneme to evaluate without relying on human interpretation.</p>
            <div className="flex items-start gap-3">
              <div style={{ width: 48, height: 48, borderRadius: '50%', background: `${iconColor}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: iconColor }}>
                <Icon size={24} />
              </div>
              <div>
                <h3 className="font-medium mb-1" style={{ color: iconColor }}>{GOVERNABILITY_LABELS[decision.governability]}</h3>
                <p className="text-muted">{GOVERNABILITY_DESC[decision.governability]}</p>
              </div>
            </div>
            
            <div className="mt-3">
                <h4 className="detail-field-label">Applies to <InfoTooltip label="Applies to">{FIELD_HELP.appliesTo}</InfoTooltip></h4>
              {decision.appliesTo.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {decision.appliesTo.map((path, i) => (
                    <span key={i} className="font-mono text-xs px-2 py-1 bg-surface2 border border-border rounded">{path}</span>
                  ))}
                </div>
              ) : <p className="text-muted">Not specified. Add explicit paths, services, or change types before enforcing this item.</p>}
            </div>
          </section>

          <section className="detail-section" aria-labelledby="proposed-rule">
            <div className="detail-section-heading">
              <h2 id="proposed-rule" className="detail-section-title">Proposed Mneme rule</h2>
              <InfoTooltip label="Proposed Mneme rule">{FIELD_HELP.proposedRule}</InfoTooltip>
            </div>
            <p className="detail-section-description">The deterministic control Mneme could evaluate for this item. Treat it as a proposal to validate with the decision owner.</p>
            {decision.proposedRule ? (
              <div className="rule-box">
                <div className="rule-box-label">Deterministic enforcement rule</div>
                <code>{decision.proposedRule.type} "{decision.proposedRule.pattern}"</code>
                <p className="mt-2 text-sm text-muted font-normal font-sans">{decision.proposedRule.description}</p>
                <button 
                  onClick={copyRule}
                  className="btn btn-ghost btn-sm mt-3 flex items-center gap-2"
                  data-cta-intent="copy_rule"
                  data-cta-position="decision_detail"
                >
                  <Copy size={14} /> {copied ? 'Copied!' : 'Copy rule'}
                </button>
              </div>
            ) : (
              <div className="rule-box" style={{ background: 'var(--surface2)', borderColor: 'var(--border2)' }}>
                <div className="rule-box-label">Deterministic enforcement rule</div>
                <p className="text-muted">No deterministic rule defined for this decision.</p>
              </div>
            )}
          </section>

          <section className="detail-section" aria-labelledby="recommendations">
            <h2 id="recommendations" className="detail-section-title">Recommendations</h2>
            <p className="detail-section-description">Practical next steps, ordered by what currently prevents safe enforcement.</p>
            <ol className="recommendation-list">
              {recommendations.map((recommendation, index) => (
                <li key={recommendation.title}>
                  <span>{index + 1}</span>
                  <div>
                    <strong>{recommendation.title}</strong>
                    <p>{recommendation.description}</p>
                  </div>
                </li>
              ))}
            </ol>
            <div className="detail-pilot-prompt">
              <div>
                <strong>Want to validate this against real pull requests?</strong>
                <p>A pilot starts in observe mode so your team can measure signal before enabling enforcement.</p>
              </div>
              <a href="/pilot/" className="btn btn-primary" data-cta-intent="request_pilot" data-cta-position="decision_detail">Request a pilot</a>
            </div>
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
