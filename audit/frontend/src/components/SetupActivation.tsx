import { useState } from 'react';
import { useAuditApi } from '../hooks/useAuditApi';
import { PilotLink } from './PilotLink';
import { track } from '../analytics';
import type { ProjectWithHistory, ProtectionAuditResponse } from '../types/audit';

const INSTALL_PROMISE = 'Connect this architecture baseline to your repository without enabling enforcement. Mneme starts in setup mode, so nothing is blocked.';

/**
 * M1.3c before-setup activation panel.
 *
 * Renders the "Install Mneme" promise and a copyable setup command built
 * from an opaque, scoped, expiring setup reference created on demand (so no
 * long-lived reference sits in the page). A reference requires a saved
 * baseline: for ephemeral audits the backend refuses and the panel points
 * at saving the baseline first.
 */
export function SetupCommandPanel({ auditId, ctaPosition = 'audit_result', compact = false }: {
  auditId: string;
  ctaPosition?: string;
  compact?: boolean;
}) {
  const { createSetupReference } = useAuditApi();
  const [reference, setReference] = useState<{ setupCommand: string; installCommand: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const install = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await createSetupReference(auditId);
      if (!result.success || !result.data) throw new Error(result.error || 'Could not create a setup reference.');
      setReference({ setupCommand: result.data.setup_command, installCommand: result.data.install_command });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not create a setup reference.');
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    if (!reference) return;
    const text = `${reference.installCommand}\n${reference.setupCommand}`;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
    } catch {
      track('audit_error', { stage: 'setup', error_code: 'clipboard_unavailable' });
      setError('Copy failed — select the commands manually.');
    }
  };

  return <div className="setup-activation">
    {!compact && <p className="setup-promise">{INSTALL_PROMISE}</p>}
    {!reference && <button
      type="button"
      className="btn btn-primary"
      onClick={install}
      disabled={loading}
      data-cta-intent="install_mneme_setup"
      data-cta-position={ctaPosition}
    >
      {loading ? 'Preparing setup command…' : 'Install Mneme'}
    </button>}
    {reference && <div className="setup-commands">
      <pre className="setup-command-block"><code>{reference.installCommand}{'\n'}{reference.setupCommand}</code></pre>
      <button type="button" className="btn btn-ghost" onClick={copy} data-cta-intent="setup_command_copy" data-cta-position={ctaPosition}>
        {copied ? 'Copied' : 'Copy commands'}
      </button>
    </div>}
    {reference && <p className="setup-note">Mneme runs in setup mode: nothing is blocked. Enabling enforcement is always a separate, explicit decision.</p>}
    {error && <p role="alert" className="action-error">{error}</p>}
  </div>;
}

/**
 * M1.3c after-setup activation state.
 *
 * Recognizes the project's Mneme activation state (distinct from the Audit
 * lifecycle) and exposes the correct next action. Only server-reported
 * values are shown — the panel never implies enforcement is on in setup
 * state, and never reports a decision as Protected beyond the audit's own
 * frozen metrics.
 */
export function SetupStatePanel({ project, baseline }: {
  project: ProjectWithHistory;
  baseline: ProtectionAuditResponse | null;
}) {
  if (project.activation_state === 'not_installed') return null;
  if (project.activation_state === 'active') {
    return <section className="audit-section" aria-label="Mneme activation status">
      <h2>Mneme is active</h2>
      <p>Preventive enforcement has been explicitly enabled for this project.</p>
      <p className="setup-note">Run re-audit to measure protection against the baseline.</p>
    </section>;
  }
  const decisions = baseline?.summary?.decisions_discovered;
  return <section className="audit-section setup-mode-panel" aria-label="Mneme setup status">
    <h2>Mneme installed — Setup mode</h2>
    <ul className="setup-checklist">
      <li><span className="setup-check-done">✓</span> Architecture baseline connected</li>
      {typeof decisions === 'number' &&
        <li><span className="setup-check-done">✓</span> {decisions} architectural decisions to review</li>}
      <li><span className="setup-check-pending">○</span> Preventive enforcement not enabled</li>
    </ul>
    <p className="setup-note">Mneme is observing in setup mode. Nothing is blocked. Choosing which protections to activate starts the pilot — an explicit, separate decision.</p>
    <div className="flex flex-wrap gap-3">
      {baseline && <PilotLink audit={baseline} ctaPosition="project" className="btn btn-primary">Start Pilot</PilotLink>}
    </div>
  </section>;
}
