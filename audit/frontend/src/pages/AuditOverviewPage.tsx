import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav } from '../components/AuditNav';
import { StatsGrid } from '../components/StatsGrid';
import { DecisionItem } from '../components/DecisionItem';
import { Loader2, Download, FileText, AlertCircle } from 'lucide-react';
import type { AuditResult } from '../types/audit';
import { trackAuditEvent } from '../analytics';

export function AuditOverviewPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { getAudit, exportAudit, loading, error } = useAuditApi();
  const [audit, setAudit] = useState<AuditResult | null>(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (id) {
      getAudit(id).then((result) => {
        if (result.success && result.data) {
          setAudit(result.data);
        }
      });
    }
  }, [id, getAudit]);

  const handleExport = async (format: 'markdown' | 'json') => {
    if (!id) return;
    setExporting(true);
    try {
      const blob = await exportAudit(id, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `architecture-audit-${id}.${format === 'markdown' ? 'md' : 'json'}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setExporting(false);
    }
  };

  if (loading && !audit) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="loading-spinner mx-auto mb-4" size={48} />
            <p className="text-muted">Analyzing repository...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error || !audit) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <AlertCircle size={48} className="mx-auto mb-4" style={{ color: 'var(--red)' }} />
            <h2 className="text-xl mb-2">Audit not found</h2>
            <p className="text-muted mb-4">{error || 'The requested audit could not be loaded.'}</p>
            <Link to="/" className="btn btn-primary" data-cta-intent="new_audit" data-cta-position="error">Run New Audit</Link>
          </div>
        </main>
      </div>
    );
  }

  const { summary, decisions, repository } = audit;

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <header className="audit-hero" style={{ textAlign: 'left', maxWidth: '900px', paddingTop: '3rem' }}>
          <span className="audit-hero-tag">Architecture Governability Audit</span>
          <h1>{repository}</h1>
          <p className="text-left max-w-none mt-2">
            {summary.totalDecisions} architectural decisions identified · 
            {summary.enforceable} enforceable · 
            {summary.partial} partially enforceable · 
            {summary.guidance} guidance only
          </p>
          <div className="flex flex-wrap gap-2 mt-4 justify-start">
            <button 
              onClick={() => handleExport('markdown')} 
              disabled={exporting}
              className="btn btn-ghost flex items-center gap-2"
              data-cta-intent="export_markdown"
              data-cta-position="audit_overview"
              data-cta-component="audit_export"
            >
              <Download size={16} /> Export Markdown
            </button>
            <button 
              onClick={() => handleExport('json')} 
              disabled={exporting}
              className="btn btn-ghost flex items-center gap-2"
              data-cta-intent="export_json"
              data-cta-position="audit_overview"
              data-cta-component="audit_export"
            >
              <FileText size={16} /> Export JSON
            </button>
          </div>
        </header>

        <section className="audit-section" aria-labelledby="stats">
          <StatsGrid summary={summary} />
        </section>

        <section className="audit-section" aria-labelledby="sources">
          <h2 id="sources" className="audit-section-title">Sources found</h2>
          <ul className="works-grid" style={{ listStyle: 'none' }}>
            {summary.sources.map((source, i) => (
              <li key={i} className="works-card flex items-center gap-2">
                <FileText size={20} className="text-teal" />
                <span>{source}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="audit-section" aria-labelledby="decisions">
          <div className="flex items-center justify-between mb-3">
            <h2 id="decisions" className="audit-section-title" style={{ marginBottom: 0 }}>Architectural decisions</h2>
            <Link to={`/audit/${id}/gaps`} className="btn btn-ghost btn-sm" data-cta-intent="view_gaps" data-cta-position="audit_overview">
              View Governance Gaps
            </Link>
          </div>
          
          <div className="decision-list" role="list" aria-label="Architectural decisions">
            {decisions.map((decision) => (
              <DecisionItem 
                key={decision.id} 
                decision={decision} 
                onClick={() => {
                  trackAuditEvent('audit_decision_view', {
                    governability: decision.governability,
                    rule_type: decision.proposedRule?.type || 'none',
                  });
                  navigate(`/audit/${id}/decisions/${decision.id}`);
                }}
              />
            ))}
          </div>
        </section>
      </main>

      <footer className="audit-footer">
        <p>Mneme HQ — Architectural drift prevention for the agentic AI SDLC</p>
      </footer>
    </div>
  );
}
