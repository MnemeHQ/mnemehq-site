import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav, BackLink } from '../components/AuditNav';
import { Copy, CheckCircle, AlertTriangle, Circle, FileText, AlertCircle } from 'lucide-react';
import type { ArchitecturalDecision, Governability } from '../types/audit';

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
          <div className="text-center">
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
          <div className="text-center">
            <AlertCircle size={48} className="mx-auto mb-4" style={{ color: 'var(--red)' }} />
            <h2 className="text-xl mb-2">Decision not found</h2>
            <Link to={`/audit/${id ?? ''}`} className="btn btn-primary" data-cta-intent="back_to_audit" data-cta-position="error">Back to Audit</Link>
          </div>
        </main>
      </div>
    );
  }

  const Icon = ICONS[decision.governability];
  const iconColor = ICON_COLORS[decision.governability];
  const badgeClass = `badge-${decision.governability === 'enforceable' ? 'enforceable' : decision.governability === 'partial' ? 'partial' : 'guidance'}`;

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <BackLink to={`/audit/${id ?? ''}`} />
        
        <header className="detail-header">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <span className={`badge ${badgeClass} mb-2`}>{GOVERNABILITY_LABELS[decision.governability]}</span>
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
            <span className="font-mono text-sm text-teal">
              Confidence: {Math.round(decision.confidence * 100)}%
            </span>
          </div>
        </header>

        <section className="detail-section" aria-labelledby="requirement">
          <h2 id="requirement" className="detail-section-title">REQUIREMENT</h2>
          <div className="detail-content">{decision.requirement}</div>
        </section>

        <section className="detail-section" aria-labelledby="source">
          <h2 id="source" className="detail-section-title">SOURCE</h2>
          <div className="detail-content">
            <p>{decision.source.file}</p>
            <p>Lines {decision.source.lines}</p>
          </div>
        </section>

        <section className="detail-section" aria-labelledby="governability">
          <h2 id="governability" className="detail-section-title">GOVERNABILITY</h2>
          <div className="flex items-start gap-3">
            <div style={{ width: 48, height: 48, borderRadius: '50%', background: `${iconColor}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: iconColor }}>
              <Icon size={24} />
            </div>
            <div>
              <h3 className="font-medium mb-1" style={{ color: iconColor }}>{GOVERNABILITY_LABELS[decision.governability]}</h3>
              <p className="text-muted">{GOVERNABILITY_DESC[decision.governability]}</p>
            </div>
          </div>
          
          {decision.appliesTo.length > 0 && (
            <div className="mt-3">
              <h4 className="font-mono text-xs text-muted mb-2">Applies to:</h4>
              <div className="flex flex-wrap gap-2">
                {decision.appliesTo.map((path, i) => (
                  <span key={i} className="font-mono text-xs px-2 py-1 bg-surface2 border border-border rounded">{path}</span>
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="detail-section" aria-labelledby="proposed-rule">
          <h2 id="proposed-rule" className="detail-section-title">PROPOSED MNEM RULE</h2>
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

        <div className="detail-section" style={{ paddingBottom: '4rem' }}>
          <Link to={`/audit/${id ?? ''}`} className="btn btn-ghost" data-cta-intent="back_to_overview" data-cta-position="decision_detail">
            ← Back to Audit Overview
          </Link>
        </div>
      </main>

      <footer className="audit-footer">
        <p>Mneme HQ — Architectural drift prevention for the agentic AI SDLC</p>
      </footer>
    </div>
  );
}