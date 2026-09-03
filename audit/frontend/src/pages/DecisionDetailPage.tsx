import { useEffect, useState } from 'react';
import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav, BackLink } from '../components/AuditNav';
import { Copy, CheckCircle, Zap, Brain, Circle, FileText, AlertCircle, Eye, Search } from 'lucide-react';
import type { ProtectionDecision, ProtectionClassification, EvidenceConfidence } from '../types/audit';

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
                <p className="text-muted" style={{ maxWidth: '700px' }}>{decision.requirement}</p>
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
              <span className="font-mono text-sm" style={{ color: CONFIDENCE_COLORS[decision.evidence_confidence] }}>
                {(CONFIDENCE_ICONS[decision.evidence_confidence] as React.ComponentType<{ size: number; className?: string }>) &&
                  React.createElement(CONFIDENCE_ICONS[decision.evidence_confidence], { size: 12, className: 'inline' })}
                Evidence: {decision.evidence_confidence.charAt(0).toUpperCase() + decision.evidence_confidence.slice(1)}
              </span>
            </div>
          </header>

          <section className="detail-section" aria-labelledby="classification">
            <h2 id="classification" className="detail-section-title">PROTECTION CLASSIFICATION</h2>
            <div className="flex items-start gap-3">
              <div style={{ width: 48, height: 48, borderRadius: '50%', background: `${iconColor}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: iconColor }}>
                <Icon size={24} />
              </div>
              <div className="flex-1">
                <h3 className="font-medium mb-1" style={{ color: iconColor }}>{CLASSIFICATION_LABELS[decision.protection_classification]}</h3>
                <p className="text-muted">{CLASSIFICATION_DESC[decision.protection_classification]}</p>
                
                {CLASSIFICATION_CTA[decision.protection_classification] && (
                  <button 
                    onClick={() => {
                      const target = document.getElementById(decision.protection_classification === 'Requires modelling' ? 'requirement' : 'proposed-rule');
                      target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                      target?.focus({ preventScroll: true });
                    }}
                    className="btn btn-primary btn-sm mt-3"
                    data-cta-intent={CLASSIFICATION_CTA[decision.protection_classification]!.intent}
                    data-cta-position="decision_detail"
                  >
                    {React.createElement(CLASSIFICATION_CTA[decision.protection_classification]!.icon, { size: 14, className: 'inline' })}
                    {CLASSIFICATION_CTA[decision.protection_classification]!.label}
                  </button>
                )}
              </div>
            </div>
            
            {decision.applies_to.length > 0 && (
              <div className="mt-3">
                <h4 className="font-mono text-xs text-muted mb-2">Applies to:</h4>
                <div className="flex flex-wrap gap-2">
                  {decision.applies_to.map((path, i) => (
                    <span key={i} className="font-mono text-xs px-2 py-1 bg-surface2 border border-border rounded">{path}</span>
                  ))}
                </div>
              </div>
            )}
          </section>

          <section className="detail-section" aria-labelledby="requirement">
            <h2 id="requirement" tabIndex={-1} className="detail-section-title">REQUIREMENT</h2>
            <div className="detail-content">{decision.requirement}</div>
          </section>

          <section className="detail-section" aria-labelledby="source">
            <h2 id="source" className="detail-section-title">SOURCE</h2>
            <div className="detail-content">
              <p>{decision.source.file}</p>
              <p>Lines {decision.source.lines}</p>
            </div>
          </section>

          <section className="detail-section" aria-labelledby="proposed-rule">
            <h2 id="proposed-rule" tabIndex={-1} className="detail-section-title">MNEME GUARDRAIL EVIDENCE</h2>
            {decision.proposed_rule ? (
              <div className="rule-box">
                <div className="rule-box-label">Deterministic enforcement rule</div>
                <code>{decision.proposed_rule.type} "{decision.proposed_rule.pattern}"</code>
                <p className="mt-2 text-sm text-muted font-normal font-sans">{decision.proposed_rule.description}</p>
                {decision.proposed_rule.include_paths && decision.proposed_rule.include_paths.length > 0 && (
                  <div className="mt-2">
                    <p className="font-mono text-xs text-muted">Include paths:</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {decision.proposed_rule.include_paths.map((path, i) => (
                        <span key={i} className="font-mono text-xs px-2 py-0.5 bg-surface2 border border-border rounded">{path}</span>
                      ))}
                    </div>
                  </div>
                )}
                {decision.proposed_rule.exclude_paths && decision.proposed_rule.exclude_paths.length > 0 && (
                  <div className="mt-2">
                    <p className="font-mono text-xs text-muted">Exclude paths:</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {decision.proposed_rule.exclude_paths.map((path, i) => (
                        <span key={i} className="font-mono text-xs px-2 py-0.5 bg-surface2 border border-border rounded">{path}</span>
                      ))}
                    </div>
                  </div>
                )}
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
