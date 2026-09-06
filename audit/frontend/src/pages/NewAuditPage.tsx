import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav } from '../components/AuditNav';
import { Upload, Loader2, AlertCircle, CheckCircle, Link as LinkIcon, ExternalLink } from 'lucide-react';
import { track } from '../analytics';

export function NewAuditPage() {
  const navigate = useNavigate();
  const { createAudit, loading, error } = useAuditApi();
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [urlError, setUrlError] = useState('');
  const [repositorySubmitError, setRepositorySubmitError] = useState('');
  const [zipSubmitError, setZipSubmitError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const selectZip = (file: File, selectionMethod: 'drop' | 'file_picker') => {
    if (!file.name.toLowerCase().endsWith('.zip')) {
      setZipFile(null);
      setZipSubmitError('Please upload a .zip file');
      return;
    }
    setZipFile(file);
    setZipSubmitError('');
    track('audit_input_selected', { input_type: 'zip', selection_method: selectionMethod });
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files.length > 0) selectZip(e.dataTransfer.files[0], 'drop');
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) selectZip(e.target.files[0], 'file_picker');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setRepositorySubmitError('');
    const currentUrlError = validateUrl(repositoryUrl);
    setUrlError(currentUrlError);

    if (!repositoryUrl) {
      setRepositorySubmitError('Please provide a GitHub repository URL');
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
      setRepositorySubmitError(result.error || 'Failed to start audit');
    }
  };

  const handleZipSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setZipSubmitError('');
    if (!zipFile) {
      setZipSubmitError('Please upload a repository ZIP file');
      track('audit_error', { stage: 'validation', error_code: 'missing_input' });
      return;
    }

    const result = await createAudit({ zipFile }, 'zip');
    if (result.success && result.data) {
      navigate(`/audit/${result.data.audit_id}`, { state: { audit: result.data } });
    } else {
      setZipSubmitError(result.error || 'Failed to start audit');
    }
  };

  const handleDemoClick = async () => {
    setRepositorySubmitError('');
    track('audit_input_selected', { input_type: 'demo', selection_method: 'url' });
    const result = await createAudit(
      { repositoryUrl: 'https://github.com/MnemeHQ/architecture-protection-demo' },
      'demo',
    );
    if (result.success && result.data) {
      navigate(`/audit/${result.data.audit_id}`, { state: { audit: result.data } });
    } else {
      setRepositorySubmitError(result.error || 'Failed to load demo');
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

              {repositorySubmitError && (
                <div className="mt-3 p-3 bg-red-900/20 border border-red-500/30 rounded-lg text-red-300 text-sm flex items-center gap-2" role="alert">
                  <AlertCircle size={16} /> {repositorySubmitError}
                </div>
              )}

              {error && !repositorySubmitError && !zipSubmitError && (
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
                Upload a repository ZIP for the Audit without granting Mneme HQ access to GitHub.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '720px', margin: '0 auto' }}>
                <article style={{
                  background: 'var(--surface2)',
                  border: '1px solid var(--border)',
                  borderRadius: '10px',
                  padding: '1.5rem 2rem',
                  textAlign: 'left'
                }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Prepare and upload the repository</h3>
                  <p className="text-muted" style={{ marginBottom: '0.5rem' }}>
                    Upload a ZIP of the repository source.
                  </p>
                  <p className="text-muted" style={{ marginBottom: '1rem' }}>
                    Exclude <code>.git</code>, <code>node_modules</code>, build artifacts, <code>.env</code> files, credentials, and other secrets.
                  </p>
                  <form onSubmit={handleZipSubmit}>
                    <div
                      className={`upload-area ${dragActive ? 'drag-active' : ''}`}
                      onDragEnter={handleDrag}
                      onDragLeave={handleDrag}
                      onDragOver={handleDrag}
                      onDrop={handleDrop}
                      onClick={() => fileInputRef.current?.click()}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && fileInputRef.current?.click()}
                      aria-label="Upload repository ZIP file"
                    >
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".zip,application/zip"
                        className="upload-input"
                        onChange={handleFileSelect}
                        onClick={(e) => e.stopPropagation()}
                        disabled={loading}
                        aria-label="Choose repository ZIP"
                      />
                      <Upload className="upload-icon" size={40} />
                      <p className="upload-text">Upload repository ZIP</p>
                      <p className="upload-hint">Drag and drop a .zip file, or click to browse</p>
                    </div>

                    {zipFile && (
                      <div className="mt-2 flex items-center justify-center gap-2 text-sm text-teal">
                        <CheckCircle size={16} /> {zipFile.name} ({(zipFile.size / 1024).toFixed(1)} KB)
                      </div>
                    )}

                    {zipSubmitError && (
                      <div className="mt-2 p-3 bg-red-900/20 border border-red-500/30 rounded-lg text-red-300 text-sm flex items-center gap-2" role="alert">
                        <AlertCircle size={16} /> {zipSubmitError}
                      </div>
                    )}

                    <p className="text-muted" style={{ marginTop: '1rem', fontSize: '0.8rem' }}>
                      The ZIP and extracted repository are deleted after Audit processing. Mneme retains the resulting Audit record.
                    </p>
                    <div className="cta-group mt-2">
                      <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? (
                          <><Loader2 className="loading-spinner w-5 h-5" />Analyzing repository...</>
                        ) : 'Run Private Repository Audit'}
                      </button>
                    </div>
                  </form>
                </article>

                <div style={{ textAlign: 'center' }}>
                  <p className="text-muted" style={{ marginBottom: '0.75rem', fontSize: '0.85rem' }}>
                    After the Audit, save a baseline to generate the setup command for your local checkout.
                  </p>
                  <a 
                    href="/docs/#quickstart"
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
                <p className="font-mono text-muted text-center" style={{ fontSize: '0.78rem' }} aria-label="Private repository journey">
                  Prepare ZIP → Upload → Audit → Save baseline → Install Mneme → Setup → Start Pilot
                </p>
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
