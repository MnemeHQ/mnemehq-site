import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav } from '../components/AuditNav';
import { Loader2, AlertCircle, Terminal, Link as LinkIcon, ExternalLink } from 'lucide-react';
import { track } from '../analytics';

export function NewAuditPage() {
  const navigate = useNavigate();
  const { createAudit, loading, error } = useAuditApi();
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [urlError, setUrlError] = useState('');
  const [submitError, setSubmitError] = useState('');

  const validateUrl = useCallback((url: string) => {
    if (!url) return '';
    try {
      new URL(url);
      if (!url.includes('github.com')) return 'Please enter a GitHub repository URL';
      return '';
    } catch {
      return 'Please enter a valid URL';
    }
  }, []);

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setRepositoryUrl(value);
    setUrlError(validateUrl(value));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError('');
    const currentUrlError = validateUrl(repositoryUrl);
    setUrlError(currentUrlError);

    if (!repositoryUrl) {
      setSubmitError('Please provide a GitHub repository URL');
      track('audit_error', { stage: 'validation', error_code: 'missing_input' });
      return;
    }
    if (currentUrlError) {
      track('audit_error', { stage: 'validation', error_code: 'invalid_repository_url' });
      return;
    }

    track('audit_input_selected', { input_type: 'repository_url', selection_method: 'url' });
    const result = await createAudit({ repositoryUrl }, 'repository_url');
    
    if (result.success && result.data) {
      navigate(`/audit/${result.data.audit_id}`, { state: { audit: result.data } });
    } else {
      setSubmitError(result.error || 'Failed to start audit');
    }
  };

  const handleDemoClick = async () => {
    setSubmitError('');
    track('audit_input_selected', { input_type: 'demo', selection_method: 'url' });
    const result = await createAudit(
      { repositoryUrl: 'https://github.com/MnemeHQ/architecture-protection-demo' },
      'demo',
    );
    if (result.success && result.data) {
      navigate(`/audit/${result.data.audit_id}`, { state: { audit: result.data } });
    } else {
      setSubmitError(result.error || 'Failed to load demo');
    }
  };

  return (
    <div className="audit-layout">
      <AuditNav />
      
      <main className="flex-1">
        <div className="audit-container">
          <header className="audit-hero">
            <span className="audit-hero-tag">Architecture Protection Audit</span>
            <h1>Understand which architectural decisions <br />are protected.</h1>
            <p>Give Mneme a repository. It identifies architectural decisions, reports their protection level, and shows guardrails and protection gaps.</p>
            
            <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
              <div className="mb-4">
                <label htmlFor="repo-url" className="input-label">GitHub Repository URL</label>
                <input
                  id="repo-url"
                  type="url"
                  className={`input-field ${urlError ? 'error' : ''}`}
                  placeholder="https://github.com/owner/repo"
                  value={repositoryUrl}
                  onChange={handleUrlChange}
                  disabled={loading}
                  aria-describedby={urlError ? 'url-error' : undefined}
                />
                {urlError && <p id="url-error" className="input-error" role="alert"><AlertCircle size={12} className="inline" /> {urlError}</p>}
              </div>

              {submitError && (
                <div className="mt-3 p-3 bg-red-900/20 border border-red-500/30 rounded-lg text-red-300 text-sm flex items-center gap-2" role="alert">
                  <AlertCircle size={16} /> {submitError}
                </div>
              )}

              {error && !submitError && (
                <div className="mt-3 p-3 bg-red-900/20 border border-red-500/30 rounded-lg text-red-300 text-sm flex items-center gap-2" role="alert">
                  <AlertCircle size={16} /> {error}
                </div>
              )}

              <div className="cta-group mt-4">
                <button 
                  type="submit" 
                  className="btn btn-primary flex-1 sm:flex-none"
                  disabled={loading}
                  data-cta-intent="run_audit"
                  data-cta-position="new_audit"
                >
                  {loading ? (
                    <>
                      <Loader2 className="loading-spinner w-5 h-5" />
                      Analyzing repository...
                    </>
                  ) : (
                    'Run Architecture Audit'
                  )}
                </button>
                <button 
                  type="button" 
                  className="btn btn-ghost flex-1 sm:flex-none"
                  onClick={handleDemoClick}
                  disabled={loading}
                  data-cta-intent="try_demo"
                  data-cta-position="new_audit"
                >
                  Try Demo Repository
                </button>
              </div>
            </form>
          </header>

          {/* ── PRIVATE REPOSITORY SECTION ── */}
          <div className="audit-section-band audit-section-band-charcoal">
            <section aria-labelledby="private-repo-heading" style={{ maxWidth: '900px', margin: '0 auto' }}>
              <h2 id="private-repo-heading" className="audit-section-title" style={{ textAlign: 'center', marginBottom: '0.5rem' }}>
                Working with a private repository?
              </h2>
              <p style={{ textAlign: 'center', color: 'var(--muted)', maxWidth: '600px', margin: '0 auto 2.5rem', lineHeight: 1.7 }}>
                Install Mneme in your local checkout and use it without granting Mneme HQ access to your repository.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '720px', margin: '0 auto' }}>
                <article style={{ 
                  background: 'var(--surface2)', 
                  border: '1px solid var(--border)', 
                  borderRadius: '10px', 
                  padding: '1.5rem 2rem',
                  textAlign: 'left'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                    <Terminal className="text-teal" size={20} />
                    <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Verified local commands</h3>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{ 
                      background: 'var(--bg)', 
                      border: '1px solid var(--border)', 
                      borderRadius: '8px', 
                      padding: '1rem 1.25rem',
                      fontFamily: '\'DM Mono\', monospace',
                      fontSize: '0.85rem',
                      color: 'var(--accent)',
                      overflowX: 'auto'
                    }}>
                      pip install mneme-hq
                    </div>
                    <div style={{ 
                      background: 'var(--bg)', 
                      border: '1px solid var(--border)', 
                      borderRadius: '8px', 
                      padding: '1rem 1.25rem',
                      fontFamily: '\'DM Mono\', monospace',
                      fontSize: '0.85rem',
                      color: 'var(--accent)',
                      overflowX: 'auto'
                    }}>
                      mneme init
                    </div>
                  </div>
                </article>

                <div style={{ textAlign: 'center' }}>
                  <a 
                    href="/docs/quickstart"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-ghost"
                    style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
                    data-cta-intent="private_repo_docs"
                    data-cta-position="new_audit"
                  >
                    <LinkIcon size={16} /> Set up Mneme locally
                    <ExternalLink size={12} style={{ marginLeft: '0.25rem' }} />
                  </a>
                  <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--muted)' }}>
                    Full installation guide, configuration, and CI/CD integration
                  </p>
                </div>
              </div>
            </section>
          </div>

          <section className="audit-section" aria-labelledby="how-it-works">
            <h2 id="how-it-works" className="audit-section-title">What the audit tells you</h2>
            <p className="audit-section-subtitle">
              The report separates documented intent from controls Mneme can evaluate deterministically, then shows the shortest path to close each gap.
            </p>
            <div className="works-grid">
              <article className="works-card">
                <h3>Decisions discovered</h3>
                <p>ADRs, CLAUDE.md, AGENTS.md, architecture docs, and configuration evidence are grouped into a single inventory of governance items.</p>
              </article>
              <article className="works-card">
                <h3>Protection classified</h3>
                <p>Each decision is <span className="text-teal">Protected</span>, <span className="text-warning">Mneme-ready</span>, <span className="text-warning">Ready to Protect</span>, or <span className="text-muted">Guidance</span>.</p>
              </article>
              <article className="works-card">
                <h3>Mneme guardrails</h3>
                <p>Inspect deterministic guardrails and the evidence behind each decision.</p>
              </article>
              <article className="works-card">
                <h3>Protection gaps</h3>
                <p>Decisions that can't be enforced yet — with specific next steps to make them machine-testable.</p>
              </article>
            </div>
          </section>
        </div>
      </main>

      <footer className="audit-footer">
        <p>Mneme HQ — Architectural drift prevention for the agentic AI SDLC</p>
        <p className="mt-1">
          <a href="https://github.com/MnemeHQ/mneme" target="_blank" rel="noopener noreferrer">Open source on GitHub</a>
          {' · '}
          <a href="/docs/">Documentation</a>
        </p>
      </footer>
    </div>
  );
}
