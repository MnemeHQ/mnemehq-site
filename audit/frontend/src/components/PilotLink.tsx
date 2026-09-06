import type { ReactNode } from 'react';
import type { ProtectionAuditResponse } from '../types/audit';
import { buildPilotHref, storePilotContext } from '../utils/pilotContext';

interface PilotLinkProps {
  audit: ProtectionAuditResponse;
  children: ReactNode;
  className?: string;
  ctaPosition: string;
  selectedDecisionId?: string;
  /** Funnel intent; `start_pilot` distinguishes the post-setup CTA. */
  intent?: 'request_pilot' | 'start_pilot';
}

export function PilotLink({ audit, children, className = 'btn btn-primary', ctaPosition, selectedDecisionId, intent = 'request_pilot' }: PilotLinkProps) {
  return (
    <a
      href={buildPilotHref(audit)}
      className={className}
      data-cta-intent={intent}
      data-cta-position={ctaPosition}
      onClick={() => storePilotContext(audit, selectedDecisionId)}
    >
      {children}
    </a>
  );
}
