import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuditApi } from '../hooks/useAuditApi';
import { AuditNav } from '../components/AuditNav';
import { Upload, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { track } from '../analytics';

export function NewAuditPage() {
  const navigate = useNavigate();
  const { createAudit, loading, error } = useAuditApi();
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [urlError, setUrlError] = useState('');
  const [submitError, setSubmitError] = useState('');
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
    if (e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith('.zip')) {
        setZipFile(file);
        setRepositoryUrl('');
        setSubmitError('');
        track('audit_input_selected', { input_type: 'zip', selection_method: 'drop' });
      } else {
        setSubmitError('Please upload a .zip file');
        track('audit_error', { stage: 'validation', error_code: 'invalid_zip' });
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      if (file.name.endsWith('.zip')) {
        setZipFile(file);
        setRepositoryUrl('');
        setSubmitError('');
        track('audit_input_selected', { input_type: 'zip', selection_method: 'file_picker' });
      } else {
        setSubmitError('Please upload a .zip file');
        track('audit_error', { stage: 'validation', error_code: 'invalid_zip' });
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError('');
    setUrlError(validateUrl(repositoryUrl));

    if (!repositoryUrl && !zipFile) {
      setSubmitError('Please provide a repository URL or upload a ZIP file');
      track('audit_error', { stage: 'validation', error_code: 'missing_input' });
      return;
    }
    const currentUrlError = validateUrl(repositoryUrl);
    if (repositoryUrl && currentUrlError) {
      track('audit_error', { stage: 'validation', error_code: 'invalid_repository_url' });
      return;
    }

    const inputType = zipFile ? 'zip' : 'repository_url';
    if (inputType === 'repository_url') {
      track('audit_input_selected', { input_type: inputType, selection_method: 'url' });
    }
    const result = await createAudit(
      { repositoryUrl: repositoryUrl || undefined, zipFile: zipFile || undefined },
      inputType,
    );
    
    if (result.success && result.data) {
      navigate(`/audit/${result.data.audit_id}`, { state: { audit: result.data } });
    } else {
      setSubmitError(result.error || 'Failed to start audit');
    }
  };

  const handleDemoClick = async () => {
    setSubmitError('');
    track('audit_input_selected', { input_type: 'demo', selection_method: 'url' });
    const result = await createAudit({ repositoryUrl: 'https://github.com/MnemeHQ/mneme' }, 'demo');
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

              <div className="mb-4 text-center text-muted font-mono text-xs">or</div>

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
                  accept=".zip"
                  className="upload-input"
                  onChange={handleFileSelect}
                  disabled={loading}
                  aria-hidden="true"
                />
                <Upload className="upload-icon" size={48} />
                <p className="upload-text">Upload repository ZIP</p>
                <p className="upload-hint">Drag and drop a .zip file, or click to browse</p>
              </div>

              {zipFile && (
                <div className="mt-3 flex items-center justify-center gap-2 text-sm text-teal">
                  <CheckCircle size={16} /> {zipFile.name} ({(zipFile.size / 1024).toFixed(1)} KB)
                </div>
              )}

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
                <p>Each decision is <span className="text-teal">Protected</span>, <span className="text-warning">Mneme-ready</span>, <span className="text-warning">Requires modelling</span>, or <span className="text-muted">Guidance</span>.</p>
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
