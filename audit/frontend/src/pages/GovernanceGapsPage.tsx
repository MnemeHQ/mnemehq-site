import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav, BackLink } from '../components/AuditNav';
import { ArrowRight, AlertCircle, Brain, Zap } from 'lucide-react';
import type { ProtectionDecision, ProtectionClassification } from '../types/audit';

interface DerivedGap {
  decision: string;
  reason: string;
  suggestedNextStep: string;
  classification: ProtectionClassification;
}

function deriveGaps(decisions: ProtectionDecision[]): DerivedGap[] {
  return decisions
    .filter(d => d.protection_classification === 'Requires modelling' || d.protection_classification === 'Mneme-ready')
    .map(d => ({
      decision: d.title,
      reason: d.protection_classification === 'Requires modelling'
        ? 'Needs architectural modelling (scope, constraints, patterns) before protection is possible.'
        : 'Complete specification exists; ready for rule generation and CI/CD integration.',
      suggestedNextStep: d.protection_classification === 'Requires modelling'
        ? 'Model the decision: define explicit applicability, deterministic matchers, and confidence thresholds.'
        : 'Generate Mneme rule and integrate into CI/CD pipeline.',
      classification: d.protection_classification,
    }));
}

export function GovernanceGapsPage() {
  const { id } = useParams<{ id: string }>();
  const { getAudit } = useAuditApi();
  const [gaps, setGaps] = useState<DerivedGap[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      setLoading(true);
      getAudit(id).then((result) => {
        if (result.success && result.data) {
          setGaps(deriveGaps(result.data.decisions));
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
            <span className="audit-hero-tag">Protection Gaps</span>
            <h1>Decisions not yet protected <span className="font-serif" style={{ color: 'var(--accent)' }}>yet</span></h1>
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
              <div className="decision-list" role="list" aria-label="Protection gaps">
                {gaps.map((gap, index) => {
                  const isModelling = gap.classification === 'Requires modelling';
                  const Icon = isModelling ? Brain : Zap;
                  const iconClass = isModelling ? 'requires-modelling' : 'mneme-ready';
                  const badgeClass = isModelling ? 'badge-requires-modelling' : 'badge-mneme-ready';
                  const badgeLabel = isModelling ? 'REQUIRES MODELLING' : 'MNEME-READY';
                  
                  return (
                    <article key={index} className="decision-item" style={{ borderColor: 'var(--warning)' }}>
                      <div className={`decision-icon ${iconClass}`} style={{ width: 48, height: 48 }}>
                        <Icon size={24} />
                      </div>
                      <div className="decision-content">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="decision-title">{gap.decision}</h3>
                          <span className={`badge ${badgeClass}`}>{badgeLabel}</span>
                        </div>
                        <p className="decision-summary" style={{ marginBottom: '0.75rem' }}><strong>Reason:</strong> {gap.reason}</p>
                        <p className="decision-summary text-teal"><strong>Suggested next step:</strong> {gap.suggestedNextStep}</p>
                      </div>
                      <div className="decision-meta">
                        <ArrowRight size={20} style={{ color: 'var(--warning)' }} />
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </section>

          <div className="audit-section text-center" style={{ paddingBottom: '4rem' }}>
            <Link to={`/audit/${id}`} className="btn btn-primary" data-cta-intent="back_to_overview" data-cta-position="gaps">
              Back to Audit Overview
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