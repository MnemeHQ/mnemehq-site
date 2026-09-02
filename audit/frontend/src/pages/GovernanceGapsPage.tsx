import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav, BackLink } from '../components/AuditNav';
import { InfoTooltip } from '../components/InfoTooltip';
import { PilotLink } from '../components/PilotLink';
import { AlertTriangle, ArrowRight, AlertCircle } from 'lucide-react';
import type { ArchitecturalDecision, AuditResult, GovernanceGap } from '../types/audit';

export function GovernanceGapsPage() {
  const { id } = useParams<{ id: string }>();
  const { getAudit, loading: apiLoading } = useAuditApi();
  const [gaps, setGaps] = useState<GovernanceGap[]>([]);
  const [decisions, setDecisions] = useState<ArchitecturalDecision[]>([]);
  const [audit, setAudit] = useState<AuditResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      setLoading(true);
      getAudit(id).then((result) => {
        if (result.success && result.data) {
          setGaps(result.data.gaps);
          setDecisions(result.data.decisions);
          setAudit(result.data);
        }
        setLoading(false);
      });
    }
  }, [id, getAudit]);

  if (loading || apiLoading) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="audit-container text-center">
            <div className="loading-spinner mx-auto mb-4" style={{ width: 40, height: 40 }} />
            <p className="text-muted">Loading governance gaps...</p>
          </div>
        </main>
      </div>
    );
  }

  if (!id) {
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
            <span className="audit-hero-tag">Governance Gaps</span>
            <h1>Decisions that can't be enforced <span className="font-serif" style={{ color: 'var(--accent)' }}>yet</span></h1>
            <p className="mt-2 text-muted">
              {gaps.length} governance {gaps.length === 1 ? 'item needs' : 'items need'} more specificity before Mneme can enforce {gaps.length === 1 ? 'it' : 'them'} safely.
              Use this list to decide what to clarify with decision owners first.
            </p>
          </header>

          <section className="audit-section" aria-labelledby="gaps">
            <h2 id="gaps" className="audit-section-title">Governance Gaps</h2>
            <p className="audit-section-subtitle">Each card connects the finding to its blocker and a recommended action. Open the governance item to review the evidence, confidence, applicability, and proposed rule.</p>
            
            {gaps.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">✓</div>
                <h3 className="empty-title">No governance gaps found</h3>
                <p className="empty-text">All identified architectural decisions in this repository are at least partially enforceable by Mneme.</p>
              </div>
            ) : (
              <div className="decision-list" role="list" aria-label="Governance gaps">
                {gaps.map((gap, index) => {
                  const decision = decisions.find((item) => item.title === gap.decision);
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
