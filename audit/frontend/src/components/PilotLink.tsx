import type { ReactNode } from 'react';
import type { ProtectionAuditResponse } from '../types/audit';
import { buildPilotHref, storePilotContext } from '../utils/pilotContext';

interface PilotLinkProps {
  audit: ProtectionAuditResponse;
  children: ReactNode;
  className?: string;
  ctaPosition: string;
  selectedDecisionId?: string;
}

export function PilotLink({ audit, children, className = 'btn btn-primary', ctaPosition, selectedDecisionId }: PilotLinkProps) {
  return (
    <a
      href={buildPilotHref(audit)}
      className={className}
      data-cta-intent="request_pilot"
      data-cta-position={ctaPosition}
      onClick={() => storePilotContext(audit, selectedDecisionId)}
    >
      {children}
    </a>
  );
}
