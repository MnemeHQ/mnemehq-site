import { useEffect, useState, useMemo } from 'react';
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav } from '../components/AuditNav';
import { StatsGrid } from '../components/StatsGrid';
import { Loader2, Download, FileText, AlertCircle, ChevronDown, ChevronUp, Search, CheckCircle, AlertTriangle, Circle, ChevronRight } from 'lucide-react';
import type { AuditResult, ArchitecturalDecision, Governability } from '../types/audit';

type FilterType = 'all' | 'enforceable' | 'partial' | 'guidance';
type SourceTypeFilter = 'all' | 'adr' | 'agent-instructions' | 'config' | 'code';

// Limits for progressive disclosure
const DEFAULT_LIMITS = {
  enforceable: 10,
  partial: 10,
  guidance: 5,
};

const ICONS: Record<Governability, typeof CheckCircle> = {
  enforceable: CheckCircle,
  partial: AlertTriangle,
  guidance: Circle,
};

const ICON_CLASS: Record<Governability, string> = {
  enforceable: 'enforceable',
  partial: 'partial',
  guidance: 'guidance',
};

const BADGE_CLASS: Record<Governability, string> = {
  enforceable: 'badge-enforceable',
  partial: 'badge-partial',
  guidance: 'badge-guidance',
};

const BADGE_LABEL: Record<Governability, string> = {
  enforceable: 'ENFORCEABLE',
  partial: 'PARTIALLY ENFORCEABLE',
  guidance: 'GUIDANCE ONLY',
};

interface CollapsibleDecisionItemProps {
  decision: ArchitecturalDecision;
  isExpanded: boolean;
  onToggle: () => void;
  onViewDetails: () => void;
  showMissing?: string;
}

function CollapsibleDecisionItem({ decision, isExpanded, onToggle, onViewDetails, showMissing }: CollapsibleDecisionItemProps) {
  const Icon = ICONS[decision.governability];
  const iconClass = ICON_CLASS[decision.governability];
  const badgeClass = BADGE_CLASS[decision.governability];
  const badgeLabel = BADGE_LABEL[decision.governability];

  return (
    <article className="decision-item" role="listitem">
      <div className="decision-item-header" onClick={onToggle} style={{ cursor: 'pointer' }}>
        <div className={`decision-icon ${iconClass}`}>
          <Icon size={20} />
        </div>
        <div className="decision-content">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="decision-title">{decision.title}</h3>
            <span className={`badge ${badgeClass}`}>{badgeLabel}</span>
          </div>
          {showMissing && <p className="decision-missing">Missing: {showMissing}</p>}
        </div>
        <div className="decision-meta">
          <span className="decision-source">{decision.source.file}</span>
          <ChevronRight size={16} style={{ color: 'var(--muted)', transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)', transition: 'transform 0.15s ease' }} />
        </div>
      </div>
      
      {isExpanded && (
        <div className="decision-item-expanded">
          <div className="decision-expanded-content">
            <div className="decision-expanded-row">
              <span className="decision-expanded-label">Requirement</span>
              <p className="decision-expanded-value">{decision.requirement}</p>
            </div>
            <div className="decision-expanded-row">
              <span className="decision-expanded-label">Applies To</span>
              <div className="decision-expanded-value">
                {decision.appliesTo.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {decision.appliesTo.map((path, i) => (
                      <span key={i} className="font-mono text-xs px-2 py-1 bg-surface2 border border-border rounded">{path}</span>
                    ))}
                  </div>
                ) : (
                  <span className="text-muted">Not specified</span>
                )}
              </div>
            </div>
            <div className="decision-expanded-row">
              <span className="decision-expanded-label">Proposed Rule</span>
              <div className="decision-expanded-value">
                {decision.proposedRule ? (
                  <>
                    <code>{decision.proposedRule.type} "{decision.proposedRule.pattern}"</code>
                    <p className="mt-1 text-sm text-muted font-normal font-sans">{decision.proposedRule.description}</p>
                  </>
                ) : (
                  <span className="text-muted">No deterministic rule defined</span>
                )}
              </div>
            </div>
            <div className="decision-expanded-row">
              <span className="decision-expanded-label">Confidence</span>
              <span className="decision-expanded-value font-mono text-teal">{Math.round(decision.confidence * 100)}%</span>
            </div>
            <div className="decision-expanded-row">
              <span className="decision-expanded-label">Source</span>
              <span className="decision-expanded-value font-mono text-xs">{decision.source.file} (Lines {decision.source.lines})</span>
            </div>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); onViewDetails(); }}
            className="btn btn-ghost btn-sm mt-3"
            data-cta-intent="view_details"
            data-cta-position="decision_list"
          >
            View Full Details
          </button>
        </div>
      )}
    </article>
  );
}

export function AuditOverviewPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams<{ id: string }>();
  const { getAudit, exportAudit, error: apiError } = useAuditApi();
  
  const stateAudit = (location.state as { audit?: AuditResult } | null)?.audit;
  const [audit, setAudit] = useState<AuditResult | null>(stateAudit ?? null);
  const [loading, setLoading] = useState<boolean>(!stateAudit);
  const [error, setError] = useState<string | null>(null);
  
  const [exporting, setExporting] = useState(false);
  const [governabilityFilter, setGovernabilityFilter] = useState<FilterType>('all');
  const [sourceTypeFilter, setSourceTypeFilter] = useState<SourceTypeFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedDecisions, setExpandedDecisions] = useState<Set<string>>(new Set());
  const [sourcesExpanded, setSourcesExpanded] = useState(false);

  // Guard: if no audit ID, redirect to new audit
  useEffect(() => {
    if (!id) {
      navigate('/', { replace: true });
      return;
    }
  }, [id, navigate]);

  useEffect(() => {
    if (!id) return;
    
    // If we already have this exact audit loaded from navigation state, don't re-fetch
    if (audit && audit.id === id) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    getAudit(id).then((result) => {
      setLoading(false);
      if (result.success && result.data) {
        setAudit(result.data);
      } else {
        setError(result.error || 'Failed to load audit');
      }
    });
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

  if (loading || (!audit && !error && !apiError)) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto px-6">
            <Loader2 className="loading-spinner mx-auto mb-4" size={48} />
            <p className="text-muted">Loading audit results...</p>
          </div>
        </main>
      </div>
    );
  }

  const effectiveError = error || apiError;
  const isNotFound = effectiveError && (effectiveError.includes('404') || effectiveError.includes('not found'));
  const isNetworkError = effectiveError && (effectiveError.includes('network') || effectiveError.includes('fetch') || effectiveError.includes('connection'));
  const isServerError = effectiveError && (effectiveError.includes('500') || effectiveError.includes('server'));

  if (effectiveError || !audit) {
    let title = 'Audit unavailable';
    let message = 'This audit may have expired or the link may be incorrect.';
    let actionText = 'Run New Audit';
    let showRetry = false;

    if (isNotFound) {
      title = 'Audit unavailable';
      message = 'This audit may have expired or the link may be incorrect.';
    } else if (isNetworkError) {
      title = "Couldn't load audit";
      message = 'A network error occurred. Please check your connection and try again.';
      showRetry = true;
      actionText = 'Retry';
    } else if (isServerError) {
      title = 'Server error';
      message = 'The audit service is temporarily unavailable. Please try again in a moment.';
      showRetry = true;
      actionText = 'Retry';
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

  const { summary, decisions = [], repository } = audit;
  const sources = summary?.sources || [];
  const totalDecisions = summary?.totalDecisions || decisions.length;
  const enforceableCount = summary?.enforceable || 0;
  const partialCount = summary?.partial || 0;
  const guidanceCount = summary?.guidance || 0;
  const coveragePct = summary?.coverage || 0;

  // Compute key finding
  const keyFinding = useMemo(() => {
    const enforceablePct = totalDecisions > 0 
      ? Math.round((enforceableCount / totalDecisions) * 100) 
      : 0;
    
    if (enforceablePct === 0) {
      return 'Most architectural intent is documented, but little is expressed in a form that can be deterministically enforced.';
    } else if (enforceablePct < 25) {
      return 'A small fraction of architectural intent is directly enforceable. Most decisions need stronger machine-testable constraints.';
    } else if (enforceablePct < 50) {
      return 'About half of architectural decisions can be enforced. The remainder need explicit applicability or deterministic rules.';
    } else {
      return 'Strong governability foundation — most decisions have at least partial enforceability.';
    }
  }, [totalDecisions, enforceableCount]);

  // Filter decisions
  const filteredDecisions = useMemo(() => {
    return decisions.filter((decision) => {
      // Governability filter
      if (governabilityFilter !== 'all' && decision.governability !== governabilityFilter) {
        return false;
      }
      
      // Source type filter
      if (sourceTypeFilter !== 'all') {
        const sourceFile = (decision.source?.file || '').toLowerCase();
        let matches = false;
        if (sourceTypeFilter === 'adr' && (sourceFile.includes('adr') || sourceFile.includes('architecture'))) matches = true;
        if (sourceTypeFilter === 'agent-instructions' && (sourceFile.includes('agent') || sourceFile.includes('instruction') || sourceFile.includes('prompt'))) matches = true;
        if (sourceTypeFilter === 'config' && (sourceFile.includes('config') || sourceFile.includes('.json') || sourceFile.includes('.yaml') || sourceFile.includes('.yml') || sourceFile.includes('.toml'))) matches = true;
        if (sourceTypeFilter === 'code' && (sourceFile.includes('.ts') || sourceFile.includes('.js') || sourceFile.includes('.py') || sourceFile.includes('.go') || sourceFile.includes('.rs'))) matches = true;
        if (!matches) return false;
      }
      
      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const titleMatch = (decision.title || '').toLowerCase().includes(query);
        const summaryMatch = (decision.summary || '').toLowerCase().includes(query);
        const requirementMatch = (decision.requirement || '').toLowerCase().includes(query);
        if (!titleMatch && !summaryMatch && !requirementMatch) return false;
      }
      
      return true;
    });
  }, [decisions, governabilityFilter, sourceTypeFilter, searchQuery]);

  // Count by governability
  const counts = useMemo(() => ({
    all: decisions.length,
    enforceable: decisions.filter(d => d.governability === 'enforceable').length,
    partial: decisions.filter(d => d.governability === 'partial').length,
    guidance: decisions.filter(d => d.governability === 'guidance').length,
  }), [decisions]);

  // Group decisions by governability for collapsible sections
  const decisionsByGovernability = useMemo(() => {
    const groups: Record<Governability, ArchitecturalDecision[]> = {
      enforceable: [],
      partial: [],
      guidance: [],
    };
    filteredDecisions.forEach(d => {
      if (groups[d.governability]) {
        groups[d.governability].push(d);
      }
    });
    return groups;
  }, [filteredDecisions]);

  // State for progressive disclosure limits
  const [displayLimits, setDisplayLimits] = useState<Record<Governability, number>>({
    enforceable: DEFAULT_LIMITS.enforceable,
    partial: DEFAULT_LIMITS.partial,
    guidance: DEFAULT_LIMITS.guidance,
  });

  const toggleDecision = (decisionId: string) => {
    setExpandedDecisions(prev => {
      const next = new Set(prev);
      if (next.has(decisionId)) {
        next.delete(decisionId);
      } else {
        next.add(decisionId);
      }
      return next;
    });
  };

  const isExpanded = (decisionId: string) => expandedDecisions.has(decisionId);

  const showAllForGovernability = (gov: Governability) => {
    setDisplayLimits(prev => ({ ...prev, [gov]: Infinity }));
  };

  const getMissingInfo = (decision: ArchitecturalDecision): string => {
    const missing: string[] = [];
    if (!decision.appliesTo || decision.appliesTo.length === 0) missing.push('explicit applicability');
    if (!decision.proposedRule) missing.push('enforceable matcher');
    if (decision.confidence < 0.7) missing.push('high-confidence rule');
    return missing.length > 0 ? missing[0] : '';
  };

  // Section navigation - reordered: Overview, Gaps, Decisions, Coverage, Sources
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
          {/* Above-fold hero: repo, totals, key finding, primary action */}
          <header className="audit-hero" style={{ paddingTop: '2rem', paddingBottom: '2rem', textAlign: 'center' }}>
            <span className="audit-hero-tag">Architecture Governability Audit</span>
            <h1>{repository}</h1>
            
            {/* Dominant totals headline */}
            <div className="audit-headline mt-4">
              <span className="audit-headline-count">{totalDecisions} governance items found</span>
              <span className="audit-headline-enforceable">
                {enforceableCount > 0 
                  ? `${enforceableCount} directly enforceable` 
                  : <><strong>0</strong> directly enforceable</>}
              </span>
            </div>
            
            <p className="mt-2 audit-key-finding">{keyFinding}</p>

            <div className="flex flex-wrap gap-2 mt-4 justify-center">
              <Link 
                to={`/audit/${id}/gaps`} 
                state={{ audit }}
                className="btn btn-primary flex items-center gap-2"
                data-cta-intent="view_gaps"
                data-cta-position="audit_overview"
              >
                View Governance Gaps
              </Link>
              <button 
                onClick={() => handleExport('markdown')} 
                disabled={exporting}
                className="btn btn-ghost flex items-center gap-2"
                data-cta-intent="export_markdown"
                data-cta-position="audit_overview"
              >
                <Download size={16} /> Export
              </button>
            </div>
          </header>

          {/* Sticky Filters */}
          <div className="audit-filters-sticky" role="region" aria-label="Filter decisions">
            <div className="audit-filters" role="region" aria-label="Filter decisions">
              <div className="audit-filters-row">
                <div className="audit-filter-group">
                  <label htmlFor="governability-filter" className="audit-filter-label">Governability</label>
                  <select
                    id="governability-filter"
                    value={governabilityFilter}
                    onChange={(e) => setGovernabilityFilter(e.target.value as FilterType)}
                    className="audit-filter-select"
                    aria-label="Filter by governability"
                  >
                    <option value="all">All ({counts.all})</option>
                    <option value="enforceable">Enforceable ({counts.enforceable})</option>
                    <option value="partial">Partial ({counts.partial})</option>
                    <option value="guidance">Guidance ({counts.guidance})</option>
                  </select>
                </div>
                <div className="audit-filter-group">
                  <label htmlFor="source-type-filter" className="audit-filter-label">Source Type</label>
                  <select
                    id="source-type-filter"
                    value={sourceTypeFilter}
                    onChange={(e) => setSourceTypeFilter(e.target.value as SourceTypeFilter)}
                    className="audit-filter-select"
                    aria-label="Filter by source type"
                  >
                    <option value="all">All Sources</option>
                    <option value="adr">ADRs</option>
                    <option value="agent-instructions">Agent Instructions</option>
                    <option value="config">Configuration</option>
                    <option value="code">Code Evidence</option>
                  </select>
                </div>
                <div className="audit-filter-group audit-filter-search">
                  <label htmlFor="decision-search" className="audit-filter-label sr-only">Search decisions</label>
                  <div className="audit-search-input">
                    <Search size={16} className="audit-search-icon" />
                    <input
                      id="decision-search"
                      type="search"
                      placeholder="Search decisions…"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="audit-search-field"
                      aria-label="Search decisions"
                    />
                  </div>
                </div>
              </div>
              <p className="audit-filter-results">
                Showing {filteredDecisions.length} of {decisions.length} governance items
              </p>
            </div>
          </div>

          {/* Compact summary bar */}
          <div className="audit-summary-bar" role="region" aria-label="Audit summary">
            <div className="audit-summary-stats">
              <span className="audit-summary-total">{totalDecisions} governance items</span>
              <div className="audit-summary-breakdown">
                <span className="audit-summary-item enforceable">
                  <strong>{enforceableCount}</strong> Enforceable
                </span>
                <span className="audit-summary-item partial">
                  <strong>{partialCount}</strong> Partial
                </span>
                <span className="audit-summary-item guidance">
                  <strong>{guidanceCount}</strong> Guidance
                </span>
              </div>
            </div>
            <div className="audit-summary-actions">
              <Link to={`/audit/${id}/gaps`} state={{ audit }} className="btn btn-ghost btn-sm" data-cta-intent="view_gaps" data-cta-position="audit_summary">
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
            <Link to={`/audit/${id}/gaps`} state={{ audit }} className="btn btn-primary" data-cta-intent="view_gaps" data-cta-position="audit_overview">
              View All Governance Gaps
            </Link>
          </section>

          <section id="decisions" className="audit-section" aria-labelledby="decisions-title">
            <h2 id="decisions-title" className="audit-section-title">Governance Items</h2>
            
            {Object.entries(decisionsByGovernability).map(([governability, items]) => {
              const gov = governability as Governability;
              if (items.length === 0) return null;
              
              const Icon = ICONS[gov];
              const badgeClass = BADGE_CLASS[gov];
              const badgeLabel = BADGE_LABEL[gov];
              const iconClass = ICON_CLASS[gov];
              const limit = displayLimits[gov];
              const displayedItems = items.slice(0, limit);
              const hasMore = items.length > limit;
              
              return (
                <div key={gov} className="decision-group">
                  <h3 className="decision-group-title flex items-center gap-2">
                    <span className={`decision-group-icon ${iconClass}`}>
                      <Icon size={16} />
                    </span>
                    <span>{badgeLabel}</span>
                    <span className={`badge ${badgeClass}`}>{items.length} items</span>
                  </h3>
                  <div className="decision-list" role="list" aria-label={`${badgeLabel} decisions`}>
                    {displayedItems.map((decision) => (
                      <CollapsibleDecisionItem
                        key={decision.id}
                        decision={decision}
                        isExpanded={isExpanded(decision.id)}
                        onToggle={() => toggleDecision(decision.id)}
                        onViewDetails={() => navigate(`/audit/${id}/decisions/${decision.id}`, { state: { audit } })}
                        showMissing={getMissingInfo(decision)}
                      />
                    ))}
                  </div>
                  {hasMore && (
                    <button
                      onClick={() => showAllForGovernability(gov)}
                      className="btn btn-ghost btn-sm mt-2"
                      data-cta-intent="show_all"
                      data-cta-position="decision_group"
                    >
                      View all {items.length}
                    </button>
                  )}
                </div>
              );
            })}
            
            {filteredDecisions.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <h3 className="empty-title">No items match your filters</h3>
                <p className="empty-text">Try adjusting your filters or search query.</p>
              </div>
            )}
          </section>

          <section id="coverage" className="audit-section" aria-labelledby="coverage-title">
            <h2 id="coverage-title" className="audit-section-title">Coverage</h2>
            <div className="audit-coverage">
              <div className="audit-coverage-bar">
                <div 
                  className="audit-coverage-fill" 
                  style={{ width: `${coveragePct}%` }}
                />
              </div>
              <p className="audit-coverage-text">
                {coveragePct}% of governance items have at least partial enforceability
              </p>
            </div>
          </section>

          <section id="sources" className="audit-section" aria-labelledby="sources-title">
            <div className="flex items-center justify-between mb-3">
              <h2 id="sources-title" className="audit-section-title" style={{ marginBottom: 0 }}>Sources Examined</h2>
              <button
                onClick={() => setSourcesExpanded(!sourcesExpanded)}
                className="btn btn-ghost btn-sm flex items-center gap-2"
                aria-expanded={sourcesExpanded}
                aria-controls="sources-list"
              >
                {sourcesExpanded ? (
                  <>
                    <ChevronUp size={14} /> Hide Sources
                  </>
                ) : (
                  <>
                    <ChevronDown size={14} /> View Sources ({sources.length})
                  </>
                )}
              </button>
            </div>
            
            <div className="audit-sources-summary">
              <p>
                <strong>{sources.length} source files examined</strong>
              </p>
              <p className="text-muted mt-1">
                {sources.filter(s => s && s.toLowerCase().includes('adr')).length} ADRs · 
                {sources.filter(s => s && (s.toLowerCase().includes('agent') || s.toLowerCase().includes('instruction') || s.toLowerCase().includes('prompt'))).length} agent instruction files · 
                {sources.filter(s => s && (s.toLowerCase().includes('config') || s.toLowerCase().includes('.json') || s.toLowerCase().includes('.yaml') || s.toLowerCase().includes('.yml') || s.toLowerCase().includes('.toml'))).length} config/code evidence sources
              </p>
            </div>
            
            <ul id="sources-list" className="works-grid" style={{ listStyle: 'none', display: sourcesExpanded ? 'grid' : 'none' }}>
              {sources.map((source, i) => (
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