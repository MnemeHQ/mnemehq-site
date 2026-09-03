import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav, BackLink } from '../components/AuditNav';
import { ArrowRight, AlertCircle, AlertTriangle } from 'lucide-react';
import { InfoTooltip } from '../components/InfoTooltip';
import { PilotLink } from '../components/PilotLink';
import type { ProtectionAuditResponse, ProtectionDecision, ProtectionClassification } from '../types/audit';

export interface DerivedGap {
  decisionId: string;
  decision: string;
  reason: string;
  suggestedNextStep: string;
  classification: ProtectionClassification;
}

export function deriveGaps(decisions: ProtectionDecision[]): DerivedGap[] {
  return decisions
    .filter(d => d.protection_classification === 'Requires modelling' || d.protection_classification === 'Mneme-ready')
    .map(d => ({
      decisionId: d.id,
      decision: d.title,
      reason: d.protection_classification === 'Requires modelling'
        ? 'Needs architectural modelling (scope, constraints, patterns) before protection is possible.'
        : 'A concrete supported guardrail has been identified, but is not yet enforced.',
      suggestedNextStep: d.protection_classification === 'Requires modelling'
        ? 'Model the decision: define explicit applicability, deterministic matchers, and confidence thresholds.'
        : 'Review the identified guardrail and validate it before enabling enforcement.',
      classification: d.protection_classification,
    }));
}

export function GovernanceGapsPage() {
  const { id } = useParams<{ id: string }>();
  const { getAudit } = useAuditApi();
  const [gaps, setGaps] = useState<DerivedGap[]>([]);
  const [decisions, setDecisions] = useState<ProtectionDecision[]>([]);
  const [audit, setAudit] = useState<ProtectionAuditResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      setLoading(true);
      getAudit(id).then((result) => {
        if (result.success && result.data) {
          setGaps(deriveGaps(result.data.decisions));
          setDecisions(result.data.decisions);
          setAudit(result.data);
        }
        setLoading(false);
      });
    }
  }, [id, getAudit]);

  if (loading) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="audit-container text-center">
            <div className="loading-spinner mx-auto mb-4" style={{ width: 40, height: 40 }} />
            <p className="text-muted">Loading protection gaps...</p>
          </div>
        </main>
      </div>
    );
  }

  if (!id || !audit) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="audit-container text-center">
            <AlertCircle size={48} className="mx-auto mb-4" style={{ color: 'var(--red)' }} />
            <h2 className="text-xl mb-2">Audit unavailable</h2>
            <p className="text-muted mb-6">This audit may have expired or the link may be incorrect.</p>
            <Link to="/" className="btn btn-primary" data-cta-intent="new_audit" data-cta-position="error">
              Run New Audit
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <div className="audit-container">
          <BackLink to={`/audit/${id}`} />
          
          <header className="audit-hero" style={{ textAlign: 'left', paddingTop: '2rem', paddingBottom: '1.5rem' }}>
            <span className="audit-hero-tag">Protection Gaps</span>
            <h1>Decisions not yet <span className="font-serif" style={{ color: 'var(--accent)' }}>protected</span></h1>
            <p className="mt-2 text-muted">
              {gaps.length} protection-relevant decisions lack deterministic enforcement. 
              Each gap shows the classification and specific next step.
            </p>
          </header>

          <section className="audit-section" aria-labelledby="gaps">
            <h2 id="gaps" className="audit-section-title">Protection Gaps</h2>
            
            {gaps.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">✓</div>
                <h3 className="empty-title">No protection gaps found</h3>
                <p className="empty-text">All protection-relevant architectural decisions in this repository are protected by Mneme.</p>
              </div>
            ) : (
              <div className="decision-list" role="list" aria-label="Governance gaps">
                {gaps.map((gap, index) => {
                  const decision = decisions.find((item) => item.id === gap.decisionId);
                  return (
                  <article key={index} className="governance-gap-card">
                    <div className="decision-icon partial" style={{ width: 48, height: 48 }}>
                      <AlertTriangle size={24} />
                    </div>
                    <div className="decision-content">
                      <h3 className="decision-title">{gap.decision}</h3>
                      <p className="decision-summary gap-explanation"><strong>Why it is a gap <InfoTooltip label="Why it is a gap">This is the specific missing information that prevents Mneme from applying a deterministic control safely.</InfoTooltip></strong>{gap.reason}</p>
                      <p className="decision-summary gap-recommendation"><strong>Recommendation <InfoTooltip label="Recommendation">A concrete documentation or rule-authoring change that would move this item closer to enforceability.</InfoTooltip></strong>{gap.suggestedNextStep}</p>
                    </div>
                    <Link
                      to={decision ? `/audit/${id}/decisions/${decision.id}` : `/audit/${id}`}
                      className="gap-card-action"
                      aria-label={decision ? `Review governance item: ${gap.decision}` : 'Return to audit overview'}
                      data-cta-intent="review_gap_item"
                      data-cta-position="governance_gaps"
                    >
                      <span>{decision ? 'Review item' : 'View overview'}</span>
                      <ArrowRight size={20} style={{ color: 'var(--warning)' }} />
                    </Link>
                  </article>
                  );
                })}
              </div>
            )}
          </section>

          <div className="audit-section text-center" style={{ paddingBottom: '4rem' }}>
            <div className="gap-next-actions">
              <div>
                <h2>Use this audit as the pilot starting point</h2>
                <p>We’ll review these recommendations before a short follow-up, select 3–5 priorities with you, and turn them into observe-mode controls. You won’t need to recreate the findings.</p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center">
                <Link to={`/audit/${id}`} className="btn btn-ghost" data-cta-intent="back_to_overview" data-cta-position="gaps">Back to Audit Overview</Link>
                {audit && <PilotLink audit={audit} ctaPosition="governance_gaps">Request a pilot</PilotLink>}
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="audit-footer">
        <p>Mneme HQ — Architectural drift prevention for the agentic AI SDLC</p>
      </footer>
    </div>
  );
}
