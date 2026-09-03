import { useEffect, useState, useMemo } from 'react';
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav } from '../components/AuditNav';
import { StatsGrid } from '../components/StatsGrid';
import { CollapsibleDecisionItem } from '../components/DecisionItem';
import { Loader2, Download, FileText, AlertCircle, ChevronDown, ChevronUp, Search, CheckCircle, Zap, Brain, Circle, Save } from 'lucide-react';
import type { ProtectionAuditResponse, ProtectionDecision, ProtectionClassification } from '../types/audit';

type FilterType = 'all' | 'Protected' | 'Mneme-ready' | 'Requires modelling' | 'Guidance';
type SourceTypeFilter = 'all' | 'adr' | 'agent-instructions' | 'config' | 'code';

const DEFAULT_LIMITS: Record<ProtectionClassification, number> = {
  Protected: 10,
  'Mneme-ready': 10,
  'Requires modelling': 10,
  Guidance: 5,
};

const CLASSIFICATION_ORDER: ProtectionClassification[] = ['Protected', 'Mneme-ready', 'Requires modelling', 'Guidance'];

const ICON_CLASS: Record<ProtectionClassification, string> = {
  Protected: 'protected',
  'Mneme-ready': 'mneme-ready',
  'Requires modelling': 'requires-modelling',
  Guidance: 'guidance',
};

const BADGE_CLASS: Record<ProtectionClassification, string> = {
  Protected: 'badge-protected',
  'Mneme-ready': 'badge-mneme-ready',
  'Requires modelling': 'badge-requires-modelling',
  Guidance: 'badge-guidance',
};

const BADGE_LABEL: Record<ProtectionClassification, string> = {
  Protected: 'PROTECTED',
  'Mneme-ready': 'MNEME-READY',
  'Requires modelling': 'REQUIRES MODELLING',
  Guidance: 'GUIDANCE ONLY',
};

function CollapsibleDecisionItemWrapper({ decision, isExpanded, onToggle, onViewDetails }: {
  decision: ProtectionDecision;
  isExpanded: boolean;
  onToggle: () => void;
  onViewDetails: () => void;
}) {
  return <CollapsibleDecisionItem decision={decision} isExpanded={isExpanded} onToggle={onToggle} onViewDetails={onViewDetails} />;
}

export function AuditOverviewPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams<{ id: string }>();
  const { getAudit, exportAudit, error: apiError, createProject } = useAuditApi();
  
  const stateAudit = (location.state as { audit?: ProtectionAuditResponse } | null)?.audit;
  const [audit, setAudit] = useState<ProtectionAuditResponse | null>(stateAudit ?? null);
  const [loading, setLoading] = useState<boolean>(!stateAudit);
  const [error, setError] = useState<string | null>(null);
  
  const [exporting, setExporting] = useState(false);
  const [classificationFilter, setClassificationFilter] = useState<FilterType>('all');
  const [sourceTypeFilter, setSourceTypeFilter] = useState<SourceTypeFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedDecisions, setExpandedDecisions] = useState<Set<string>>(new Set());
  const [sourcesExpanded, setSourcesExpanded] = useState(false);
  const [activeSection, setActiveSection] = useState<string>('overview');
  const [savingBaseline, setSavingBaseline] = useState(false);

  const [displayLimits, setDisplayLimits] = useState<Record<ProtectionClassification, number>>({
    Protected: DEFAULT_LIMITS.Protected,
    'Mneme-ready': DEFAULT_LIMITS['Mneme-ready'],
    'Requires modelling': DEFAULT_LIMITS['Requires modelling'],
    Guidance: DEFAULT_LIMITS.Guidance,
  });

  const sections = useMemo(() => [
    { id: 'overview', label: 'Overview' },
    { id: 'decisions', label: 'Decisions' },
    { id: 'sources', label: 'Sources' },
  ], []);

  useEffect(() => {
    if (!id) {
      navigate('/', { replace: true });
      return;
    }
  }, [id, navigate]);

  useEffect(() => {
    if (!id) return;
    
    if (audit && audit.audit_id === id) {
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

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.pageYOffset + 150;
      for (const section of sections) {
        const el = document.getElementById(section.id);
        if (el) {
          const top = el.offsetTop;
          const height = el.offsetHeight;
          if (scrollPosition >= top && scrollPosition < top + height) {
            setActiveSection(section.id);
            break;
          }
        }
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [sections]);

  const summary = audit?.summary;
  const decisions = useMemo(() => audit?.decisions || [], [audit]);
  const repository = audit?.repository || '';
  const sources = useMemo(() => summary?.sources || [], [summary]);
  const totalDecisions = summary?.decisions_discovered || decisions.length;
  const protectionRelevant = summary?.protection_relevant || 0;
  const protectedCount = summary?.protected_count || 0;
  const mnemeReadyCount = summary?.mneme_ready_count || 0;
  const requiresModellingCount = summary?.requires_modelling_count || 0;
  const guidanceCount = summary?.guidance_count || 0;
  const currentProtection = summary?.current_protection || 0;
  const mnemePotential = summary?.identified_mneme_potential || 0;

  const keyFinding = useMemo(() => {
    if (protectionRelevant === 0) {
      return 'No protection-relevant architectural decisions found. All identified decisions are guidance-only.';
    }
    
    const protectionPct = Math.round(currentProtection * 100);
    
    if (protectedCount === 0) {
      return `${mnemeReadyCount + requiresModellingCount} protection gaps identified — ${mnemeReadyCount} Mneme-ready, ${requiresModellingCount} require modelling.`;
    } else if (protectionPct < 25) {
      return `Low architecture protection (${protectionPct}%). ${mnemeReadyCount} decisions are Mneme-ready for immediate protection gains.`;
    } else if (protectionPct < 50) {
      return `Moderate protection (${protectionPct}%). ${requiresModellingCount} decisions need modelling to reach full coverage.`;
    } else {
      return `Strong architecture protection (${protectionPct}%). Well-governed architectural baseline.`;
    }
  }, [protectionRelevant, protectedCount, mnemeReadyCount, requiresModellingCount, currentProtection, mnemePotential]);

  const filteredDecisions = useMemo(() => {
    return decisions.filter((decision) => {
      if (classificationFilter !== 'all' && decision.protection_classification !== classificationFilter) {
        return false;
      }
      
      if (sourceTypeFilter !== 'all') {
        const sourceFile = (decision.source?.file || '').toLowerCase();
        let matches = false;
        if (sourceTypeFilter === 'adr' && (sourceFile.includes('adr') || sourceFile.includes('architecture'))) matches = true;
        if (sourceTypeFilter === 'agent-instructions' && (sourceFile.includes('agent') || sourceFile.includes('instruction') || sourceFile.includes('prompt'))) matches = true;
        if (sourceTypeFilter === 'config' && (sourceFile.includes('config') || sourceFile.includes('.json') || sourceFile.includes('.yaml') || sourceFile.includes('.yml') || sourceFile.includes('.toml'))) matches = true;
        if (sourceTypeFilter === 'code' && (sourceFile.includes('.ts') || sourceFile.includes('.js') || sourceFile.includes('.py') || sourceFile.includes('.go') || sourceFile.includes('.rs'))) matches = true;
        if (!matches) return false;
      }
      
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const titleMatch = (decision.title || '').toLowerCase().includes(query);
        const summaryMatch = (decision.summary || '').toLowerCase().includes(query);
        const requirementMatch = (decision.requirement || '').toLowerCase().includes(query);
        if (!titleMatch && !summaryMatch && !requirementMatch) return false;
      }
      
      return true;
    });
  }, [decisions, classificationFilter, sourceTypeFilter, searchQuery]);

  const counts = useMemo(() => ({
    all: decisions.length,
    Protected: decisions.filter(d => d.protection_classification === 'Protected').length,
    'Mneme-ready': decisions.filter(d => d.protection_classification === 'Mneme-ready').length,
    'Requires modelling': decisions.filter(d => d.protection_classification === 'Requires modelling').length,
    Guidance: decisions.filter(d => d.protection_classification === 'Guidance').length,
  }), [decisions]);

  const decisionsByClassification = useMemo(() => {
    const groups: Record<ProtectionClassification, ProtectionDecision[]> = {
      Protected: [],
      'Mneme-ready': [],
      'Requires modelling': [],
      Guidance: [],
    };
    filteredDecisions.forEach(d => {
      if (groups[d.protection_classification]) {
        groups[d.protection_classification].push(d);
      }
    });
    return groups;
  }, [filteredDecisions]);

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

  const showAllForClassification = (classification: ProtectionClassification) => {
    setDisplayLimits(prev => ({ ...prev, [classification]: Infinity }));
  };

  const scrollToSection = (sectionId: string) => {
    setActiveSection(sectionId);
    const element = document.getElementById(sectionId);
    if (!element) return;
    const navOffset = 130;
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo({
      top: Math.max(0, elementPosition - navOffset),
      behavior: 'smooth',
    });
  };

  const handleExport = async (format: 'markdown' | 'json') => {
    if (!id) return;
    setExporting(true);
    try {
      const blob = await exportAudit(id, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `protection-audit-${id}.${format === 'markdown' ? 'md' : 'json'}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setExporting(false);
    }
  };

  const handleSaveBaseline = async () => {
    if (!audit) return;
    setSavingBaseline(true);
    try {
      const slug = audit.repository.replace(/[^a-zA-Z0-9-]/g, '-').toLowerCase().substring(0, 50);
      const projectName = audit.repository;
      const result = await createProject({
        name: projectName,
        slug: slug,
        source_locator: audit.repository_url || audit.repository,
        source_type: 'github',
      });
      if (result.success && result.data) {
        navigate(`/project/${result.data.id}`, { state: { audit } });
      } else {
        setError(result.error || 'Failed to save baseline');
      }
    } catch (err) {
      console.error('Save baseline failed:', err);
      setError('Failed to save baseline');
    } finally {
      setSavingBaseline(false);
    }
  };

  if (loading || (!audit && !error && !apiError)) {
    return (
      <div className="audit-layout">
        <AuditNav />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto px-6">
            <Loader2 className="loading-spinner mx-auto mb-4" size={48} />
            <p className="text-muted">Loading protection audit...</p>
          </div>
        </main>
      </div>
    );
  }

  const effectiveError = error || apiError;
  const isNotFound = effectiveError && (effectiveError.includes('404') || effectiveError.includes('not found'));
  const isNetworkError = effectiveError && (effectiveError.includes('network') || effectiveError.includes('fetch') || effectiveError.includes('connection'));
  const isServerError = effectiveError && (effectiveError.includes('500') || effectiveError.includes('server'));

  if (effectiveError || !audit || !summary) {
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

  const protectionPct = Math.round(currentProtection * 100);

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <div className="audit-container">
          <header className="audit-hero" style={{ paddingTop: '2rem', paddingBottom: '2rem', textAlign: 'center' }}>
            <span className="audit-hero-tag">Architecture Protection Audit</span>
            <h1>{repository}</h1>
            
            <div className="audit-protection-headline mt-4">
              <div className="protection-score-large">
                <span className="protection-score-value">{protectionPct}%</span>
                <span className="protection-score-label">Current Protection</span>
              </div>
              <p className="protection-subtext">
                {protectedCount} of {protectionRelevant} protection-relevant decisions protected
              </p>
            </div>
            
            <div className="protection-breakdown mt-4 flex flex-wrap gap-3 justify-center">
              <span className="badge badge-protected flex items-center gap-1">
                <CheckCircle size={12} /> {protectedCount} Protected
              </span>
              {mnemeReadyCount > 0 && (
                <span className="badge badge-mneme-ready flex items-center gap-1">
                  <Zap size={12} /> {mnemeReadyCount} Mneme-ready
                </span>
              )}
              {requiresModellingCount > 0 && (
                <span className="badge badge-requires-modelling flex items-center gap-1">
                  <Brain size={12} /> {requiresModellingCount} Requires modelling
                </span>
              )}
              {guidanceCount > 0 && (
                <span className="badge badge-guidance flex items-center gap-1">
                  <Circle size={12} /> {guidanceCount} Guidance
                </span>
              )}
            </div>

            {mnemeReadyCount > 0 && protectionRelevant > 0 && (
              <div className="mneme-potential-uplift mt-3">
                <p className="text-muted">
                  Current: <strong>{protectionPct}%</strong>
                  {' '}
                  <span style={{ color: 'var(--warning)' }}>
                    With {mnemeReadyCount} identified Mneme guardrail{mnemeReadyCount > 1 ? 's' : ''}: 
                    <strong>{Math.round(((protectedCount + mnemeReadyCount) / protectionRelevant) * 100)}%</strong>
                  </span>
                </p>
              </div>
            )}

            <p className="mt-3 audit-key-finding">{keyFinding}</p>

            <div className="flex flex-wrap gap-2 mt-4 justify-center">
              <Link 
                to={`/audit/${id}/decisions`} 
                state={{ audit }}
                className="btn btn-primary flex items-center gap-2"
                data-cta-intent="view_all_decisions"
                data-cta-position="audit_overview"
              >
                View All Decisions
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
              <button 
                onClick={handleSaveBaseline}
                disabled={savingBaseline}
                className="btn btn-ghost flex items-center gap-2"
                data-cta-intent="save_baseline"
                data-cta-position="audit_overview"
              >
                <Save size={16} /> Save Baseline
              </button>
            </div>
          </header>

          <div className="audit-filters-sticky" role="region" aria-label="Filter decisions">
            <div className="audit-filters" role="region" aria-label="Filter decisions">
              <div className="audit-filters-row">
                <div className="audit-filter-group">
                  <label htmlFor="classification-filter" className="audit-filter-label">Protection Classification</label>
                  <select
                    id="classification-filter"
                    value={classificationFilter}
                    onChange={(e) => setClassificationFilter(e.target.value as FilterType)}
                    className="audit-filter-select"
                    aria-label="Filter by protection classification"
                  >
                    <option value="all">All ({counts.all})</option>
                    <option value="Protected">Protected ({counts.Protected})</option>
                    <option value="Mneme-ready">Mneme-ready ({counts['Mneme-ready']})</option>
                    <option value="Requires modelling">Requires modelling ({counts['Requires modelling']})</option>
                    <option value="Guidance">Guidance ({counts.Guidance})</option>
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

          <nav className="audit-section-nav" aria-label="Audit sections">
            <div className="audit-section-nav-inner">
              {sections.map((section) => (
                <button 
                  key={section.id}
                  type="button"
                  onClick={() => scrollToSection(section.id)}
                  className={`audit-section-nav-item ${activeSection === section.id ? 'active' : ''}`}
                  data-section={section.id}
                >
                  {section.label}
                </button>
              ))}
            </div>
          </nav>

          <section id="overview" className="audit-section" aria-labelledby="stats">
            <StatsGrid summary={summary} />
            
            <div className="protection-summary-detail">
              <h3 className="audit-section-title" style={{ marginBottom: '1rem' }}>Protection Detail</h3>
              <div className="protection-detail-grid">
                <div className="protection-detail-item">
                  <span className="protection-detail-label">Decisions Discovered</span>
                  <span className="protection-detail-value font-mono text-accent">{totalDecisions}</span>
                </div>
                <div className="protection-detail-item">
                  <span className="protection-detail-label">Protection-Relevant</span>
                  <span className="protection-detail-value font-mono text-accent">{protectionRelevant}</span>
                </div>
                <div className="protection-detail-item">
                  <span className="protection-detail-label">Guidance Only</span>
                  <span className="protection-detail-value font-mono text-muted">{guidanceCount}</span>
                </div>
              </div>
              
              {protectionRelevant > 0 && (
                <div className="protection-progress-bar mt-4">
                  <div className="protection-progress-track">
                    <div 
                      className="protection-progress-segment protected"
                      style={{ width: `${(protectedCount / protectionRelevant) * 100}%` }}
                    />
                    {mnemeReadyCount > 0 && (
                      <div 
                        className="protection-progress-segment mneme-ready"
                        style={{ width: `${(mnemeReadyCount / protectionRelevant) * 100}%` }}
                      />
                    )}
                    {requiresModellingCount > 0 && (
                      <div 
                        className="protection-progress-segment requires-modelling"
                        style={{ width: `${(requiresModellingCount / protectionRelevant) * 100}%` }}
                      />
                    )}
                  </div>
                  <div className="protection-progress-legend">
                    <span className="legend-item protected"><span className="legend-color" /><span>Protected ({protectedCount})</span></span>
                    {mnemeReadyCount > 0 && <span className="legend-item mneme-ready"><span className="legend-color" /><span>Mneme-ready ({mnemeReadyCount})</span></span>}
                    {requiresModellingCount > 0 && <span className="legend-item requires-modelling"><span className="legend-color" /><span>Requires modelling ({requiresModellingCount})</span></span>}
                  </div>
                </div>
              )}
            </div>
          </section>

          <section id="decisions" className="audit-section" aria-labelledby="decisions-title">
            <h2 id="decisions-title" className="audit-section-title">Protection Decisions</h2>
            <p className="audit-section-subtitle">
              Each decision shows its protection classification. Evidence and reasoning available on expand.
            </p>
            
            {CLASSIFICATION_ORDER.map((classification) => {
              const items = decisionsByClassification[classification];
              if (items.length === 0) return null;
              
              const Icon = classification === 'Protected' ? CheckCircle : 
                          classification === 'Mneme-ready' ? Zap :
                          classification === 'Requires modelling' ? Brain : Circle;
              const badgeClass = BADGE_CLASS[classification];
              const iconClass = ICON_CLASS[classification];
              const limit = displayLimits[classification];
              const displayedItems = items.slice(0, limit);
              const hasMore = items.length > limit;
              
              return (
                <div key={classification} className="decision-group">
                  <h3 className="decision-group-title flex items-center gap-2">
                    <span className={`decision-group-icon ${iconClass}`}>
                      <Icon size={16} />
                    </span>
                    <span>{BADGE_LABEL[classification]}</span>
                    <span className={`badge ${badgeClass}`}>{items.length} items</span>
                  </h3>
                  <div className="decision-list" role="list" aria-label={`${BADGE_LABEL[classification]} decisions`}>
                    {displayedItems.map((decision) => (
                      <CollapsibleDecisionItemWrapper
                        key={decision.id}
                        decision={decision}
                        isExpanded={isExpanded(decision.id)}
                        onToggle={() => toggleDecision(decision.id)}
                        onViewDetails={() => navigate(`/audit/${id}/decisions/${decision.id}`, { state: { audit } })}
                      />
                    ))}
                  </div>
                  {hasMore && (
                    <button
                      onClick={() => showAllForClassification(classification)}
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