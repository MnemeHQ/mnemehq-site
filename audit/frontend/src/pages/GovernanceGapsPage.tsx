import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav, BackLink } from '../components/AuditNav';
import { AlertTriangle, ArrowRight } from 'lucide-react';
import type { GovernanceGap } from '../types/audit';

export function GovernanceGapsPage() {
  const { id } = useParams<{ id: string }>();
  const { getAudit, loading: apiLoading } = useAuditApi();
  const [gaps, setGaps] = useState<GovernanceGap[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      setLoading(true);
      getAudit(id).then((result) => {
        if (result.success && result.data) {
          setGaps(result.data.gaps);
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
          <div className="text-center">
            <div className="loading-spinner mx-auto mb-4" style={{ width: 40, height: 40 }} />
            <p className="text-muted">Loading governance gaps...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <BackLink to={`/audit/${id ?? ''}`} />
        
        <header className="audit-hero" style={{ textAlign: 'left', maxWidth: '900px', paddingTop: '3rem' }}>
          <span className="audit-hero-tag">Governance Gaps</span>
          <h1>Decisions that can't be enforced <span className="font-serif" style={{ color: 'var(--accent)' }}>yet</span></h1>
          <p className="text-left max-w-none mt-2 text-muted">
            {gaps.length} architectural decisions identified that lack machine-testable constraints. 
            Each gap includes the specific next step to make it enforceable.
          </p>
        </header>

        <section className="audit-section" aria-labelledby="gaps">
          <h2 id="gaps" className="audit-section-title">Governance Gaps</h2>
          
          {gaps.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✓</div>
              <h3 className="empty-title">No governance gaps found</h3>
              <p className="empty-text">All identified architectural decisions in this repository are at least partially enforceable by Mneme.</p>
            </div>
          ) : (
            <div className="decision-list" role="list" aria-label="Governance gaps">
              {gaps.map((gap, index) => (
                <article key={index} className="decision-item" style={{ borderColor: 'var(--warning)' }}>
                  <div className="decision-icon partial" style={{ width: 48, height: 48 }}>
                    <AlertTriangle size={24} />
                  </div>
                  <div className="decision-content">
                    <h3 className="decision-title">{gap.decision}</h3>
                    <p className="decision-summary" style={{ marginBottom: '0.75rem' }}><strong>Reason:</strong> {gap.reason}</p>
                    <p className="decision-summary text-teal"><strong>Suggested next step:</strong> {gap.suggestedNextStep}</p>
                  </div>
                  <div className="decision-meta">
                    <ArrowRight size={20} style={{ color: 'var(--warning)' }} />
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <div className="audit-section text-center" style={{ paddingBottom: '4rem' }}>
          <Link to={`/audit/${id ?? ''}`} className="btn btn-primary" data-cta-intent="back_to_overview" data-cta-position="gaps">
            Back to Audit Overview
          </Link>
        </div>
      </main>

      <footer className="audit-footer">
        <p>Mneme HQ — Architectural drift prevention for the agentic AI SDLC</p>
      </footer>
    </div>
  );
}