import type { ProtectionAuditResponse } from '../types/audit';
import { PilotLink } from './PilotLink';

interface AuditSetupProps {
  audit: ProtectionAuditResponse;
  ctaPosition: string;
  selectedDecisionId?: string;
}

export function AuditSetup({ audit, ctaPosition, selectedDecisionId }: AuditSetupProps) {
  return (
    <aside id="setup" className="pilot-cta" aria-labelledby="setup-title">
      <span className="pilot-cta-eyebrow">Next step after your audit</span>
      <h2 id="setup-title">Install Mneme and set up your repository</h2>
      <p>The audit identifies decisions and protection gaps without changing your repository. Installing Mneme does not automatically enable enforcement or activate the proposed guardrails.</p>
      <ol>
        <li><strong>Install</strong> Mneme and initialize project memory using the setup guide.</li>
        <li><strong>Review</strong> the relevant decisions, scope, and proposed constraints with the decision owner.</li>
        <li><strong>Configure and validate</strong> supported checks in your chosen integration before explicitly enabling enforcement.</li>
      </ol>
      <a href="/docs/#quickstart" className="btn btn-primary" data-cta-intent="install" data-cta-position={ctaPosition}>Install Mneme</a>
      <p>After setup, want help validating a small set of controls with your team? Request a pilot using these audit findings.</p>
      <PilotLink audit={audit} selectedDecisionId={selectedDecisionId} ctaPosition={ctaPosition} className="btn btn-ghost">Request a pilot</PilotLink>
    </aside>
  );
}
