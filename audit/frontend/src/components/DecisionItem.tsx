import { type ArchitecturalDecision } from '../types/audit';
import { CheckCircle, AlertTriangle, Circle, ChevronRight } from 'lucide-react';

interface DecisionItemProps {
  decision: ArchitecturalDecision;
  onClick: () => void;
}

const ICONS = {
  enforceable: CheckCircle,
  partial: AlertTriangle,
  guidance: Circle,
};

const ICON_CLASS = {
  enforceable: 'enforceable',
  partial: 'partial',
  guidance: 'guidance',
};

const BADGE_CLASS = {
  enforceable: 'badge-enforceable',
  partial: 'badge-partial',
  guidance: 'badge-guidance',
};

const BADGE_LABEL = {
  enforceable: 'ENFORCEABLE',
  partial: 'PARTIALLY ENFORCEABLE',
  guidance: 'GUIDANCE ONLY',
};

export function DecisionItem({ decision, onClick }: DecisionItemProps) {
  const Icon = ICONS[decision.governability];
  const iconClass = ICON_CLASS[decision.governability];
  const badgeClass = BADGE_CLASS[decision.governability];
  const badgeLabel = BADGE_LABEL[decision.governability];

  return (
    <article className="decision-item" onClick={onClick} tabIndex={0} onKeyDown={(e) => e.key === 'Enter' && onClick()} role="button" aria-label={`View details for ${decision.title}`}>
      <div className={`decision-icon ${iconClass}`}>
        <Icon size={20} />
      </div>
      <div className="decision-content">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="decision-title">{decision.title}</h3>
          <span className={`badge ${badgeClass}`}>{badgeLabel}</span>
        </div>
        <p className="decision-summary">{decision.summary}</p>
      </div>
      <div className="decision-meta">
        <span className="decision-source">{decision.source.file}</span>
        <ChevronRight size={16} style={{ color: 'var(--muted)' }} />
      </div>
    </article>
  );
}