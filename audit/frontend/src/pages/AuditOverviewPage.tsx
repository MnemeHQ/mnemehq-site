import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav } from '../components/AuditNav';
import { StatsGrid } from '../components/StatsGrid';
import { DecisionItem } from '../components/DecisionItem';
import { Loader2, Download, FileText, AlertCircle } from 'lucide-react';
import type { AuditResult } from '../types/audit';

export function AuditOverviewPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { getAudit, exportAudit, loading, error } = useAuditApi();
  const [audit, setAudit] = useState<AuditResult | null>(null);
  const [exporting, setExporting] = useState(false);

  // Guard: if no audit ID, redirect to new audit
  useEffect(() => {
    if (!id) {
      navigate('/', { replace: true });
      return;
    }
  }, [id, navigate]);

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
          <div className="text-center max-w-md mx-auto px-6">
            <Loader2 className="loading-spinner mx-auto mb-4" size={48} />
            <p className="text-muted">Analyzing repository...</p>
          </div>
        </main>
      </div>
    );
  }

  // Determine error state
  const isNotFound = error && (error.includes('404') || error.includes('not found'));
  const isNetworkError = error && (error.includes('network') || error.includes('fetch') || error.includes('connection'));
  const isServerError = error && (error.includes('500') || error.includes('server'));

  if (error || !audit) {
    let title = 'Audit unavailable';
    let message = 'This audit may have expired or the link may be incorrect.';
    let actionText = 'Run New Audit';
    let showRetry = false;

    if (isNotFound) {
      title = 'Audit unavailable';
      message = 'This audit may have expired or the link may be incorrect.';
    } else if (isNetworkError) {
      title = 'Couldn\'t load audit';
      message = 'A network error occurred. Please check your connection and try again.';
      showRetry = true;
      actionText = 'Retry';
    } else if (isServerError) {
      title = 'Server error';
      message = 'The audit service is temporarily unavailable. Please try again in a moment.';
      showRetry = true;
      actionText = 'Retry';
    } else if (!audit) {
      title = 'Audit unavailable';
      message = 'This audit may have expired or the link may be incorrect.';
    }

    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto px-6">
            <AlertCircle size={48} className="mx-auto mb-4" style={{ color: 'var(--red)' }} />
            <h2 className="text-xl mb-2">{title}</h2>
            <p className="text-muted mb-6">{message}</p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/" className="btn btn-primary" data-cta-intent="new_audit" data-cta-position="error">
                {actionText}
              </Link>
              {showRetry && id && (
                <button 
                  onClick={() => window.location.reload()}
                  className="btn btn-ghost"
                  data-cta-intent="retry_audit"
                  data-cta-position="error"
                >
                  Retry
                </button>
              )}
            </div>
          </div>
        </main>
      </div>
    );
  }

const { summary, decisions, repository } = audit;

  // Section navigation
  const sections = [
    { id: 'overview', label: 'Overview' },
    { id: 'gaps', label: 'Governance Gaps' },
    { id: 'decisions', label: 'Decisions' },
    { id: 'coverage', label: 'Coverage' },
    { id: 'sources', label: 'Sources' },
  ];

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <div className="audit-container">
          <header className="audit-hero" style={{ paddingTop: '2rem', paddingBottom: '1.5rem' }}>
            <span className="audit-hero-tag">Architecture Governability Audit</span>
            <h1>{repository}</h1>
            <p className="mt-2">
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
              >
                <Download size={16} /> Export Markdown
              </button>
              <button 
                onClick={() => handleExport('json')} 
                disabled={exporting}
                className="btn btn-ghost flex items-center gap-2"
                data-cta-intent="export_json"
                data-cta-position="audit_overview"
              >
                <FileText size={16} /> Export JSON
              </button>
            </div>
          </header>

          {/* Compact summary bar */}
          <div className="audit-summary-bar" role="region" aria-label="Audit summary">
            <div className="audit-summary-stats">
              <span className="audit-summary-total">{summary.totalDecisions} decisions</span>
              <div className="audit-summary-breakdown">
                <span className="audit-summary-item enforceable">
                  <strong>{summary.enforceable}</strong> Enforceable
                </span>
                <span className="audit-summary-item partial">
                  <strong>{summary.partial}</strong> Partial
                </span>
                <span className="audit-summary-item guidance">
                  <strong>{summary.guidance}</strong> Guidance
                </span>
              </div>
            </div>
            <div className="audit-summary-actions">
              <Link to={`/audit/${id}/gaps`} className="btn btn-ghost btn-sm" data-cta-intent="view_gaps" data-cta-position="audit_summary">
                Governance Gaps
              </Link>
              <button 
                onClick={() => handleExport('markdown')} 
                disabled={exporting}
                className="btn btn-primary btn-sm"
                data-cta-intent="export_markdown"
                data-cta-position="audit_summary"
              >
                <Download size={14} /> Export
              </button>
            </div>
          </div>

          {/* Sticky section navigator */}
          <nav className="audit-section-nav" aria-label="Audit sections">
            <div className="audit-section-nav-inner">
              {sections.map((section) => (
                <a 
                  key={section.id}
                  href={`#${section.id}`}
                  className="audit-section-nav-item"
                  data-section={section.id}
                >
                  {section.label}
                </a>
              ))}
            </div>
          </nav>

          <section id="overview" className="audit-section" aria-labelledby="stats">
            <StatsGrid summary={summary} />
          </section>

          <section id="gaps" className="audit-section" aria-labelledby="gaps-title">
            <h2 id="gaps-title" className="audit-section-title">Governance Gaps</h2>
            <p className="audit-section-subtitle">Decisions that cannot be fully enforced — with specific next steps to make them machine-testable.</p>
            <Link to={`/audit/${id}/gaps`} className="btn btn-primary" data-cta-intent="view_gaps" data-cta-position="audit_overview">
              View All Governance Gaps
            </Link>
          </section>

          <section id="decisions" className="audit-section" aria-labelledby="decisions">
            <div className="flex items-center justify-between mb-3">
              <h2 id="decisions" className="audit-section-title" style={{ marginBottom: 0 }}>Architectural decisions</h2>
            </div>
            
            <div className="decision-list" role="list" aria-label="Architectural decisions">
              {decisions.map((decision) => (
                <DecisionItem 
                  key={decision.id} 
                  decision={decision} 
                  onClick={() => navigate(`/audit/${id}/decisions/${decision.id}`)} 
                />
              ))}
            </div>
          </section>

          <section id="coverage" className="audit-section" aria-labelledby="coverage-title">
            <h2 id="coverage-title" className="audit-section-title">Coverage</h2>
            <div className="audit-coverage">
              <div className="audit-coverage-bar">
                <div 
                  className="audit-coverage-fill" 
                  style={{ width: `${summary.coverage}%` }}
                />
              </div>
              <p className="audit-coverage-text">
                {summary.coverage}% of decisions have at least partial enforceability
              </p>
            </div>
          </section>

          <section id="sources" className="audit-section" aria-labelledby="sources">
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
        </div>
      </main>

      <footer className="audit-footer">
        <p>Mneme HQ — Architectural drift prevention for the agentic AI SDLC</p>
      </footer>
    </div>
  );
}