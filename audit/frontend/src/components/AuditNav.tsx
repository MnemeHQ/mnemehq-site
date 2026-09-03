import { Link, useLocation } from 'react-router-dom';
import { Github, ArrowLeft } from 'lucide-react';

export function AuditNav() {
  const location = useLocation();
  
  return (
    <nav className="audit-nav" role="navigation" aria-label="Audit navigation">
      <div className="audit-nav-brand">
        <a href="https://mnemehq.com/" className="audit-nav-logo" aria-label="Mneme HQ - Home" target="_blank" rel="noopener noreferrer">
          <img src="/logo-v3.png" alt="Mneme HQ" />
        </a>
        <Link to="/" className="audit-nav-product" aria-label="Architecture Audit">
          Architecture Audit
        </Link>
      </div>
      <div className="audit-nav-links">
        <Link 
          to="/" 
          className={location.pathname === '/' ? 'active' : ''}
          data-cta-intent="nav_new_audit"
          data-cta-position="audit_nav"
        >
          New Audit
        </Link>
        <Link 
          to="https://github.com/MnemeHQ/mneme" 
          target="_blank" 
          rel="noopener noreferrer"
          data-cta-intent="nav_github"
          data-cta-position="audit_nav"
        >
          <Github className="flex items-center gap-2" size={16} /> GitHub
        </Link>
      </div>
    </nav>
  );
}

interface BackLinkProps {
  to?: string;
}

export function BackLink({ to = '/' }: BackLinkProps) {
  const location = useLocation();
  if (location.pathname === '/') return null;
  
  return (
    <Link to={to} className="btn btn-tertiary btn-sm audit-back-link mt-2" data-cta-intent="back" data-cta-position="audit_detail">
      <ArrowLeft size={14} /> Back to Audit
    </Link>
  );
}
