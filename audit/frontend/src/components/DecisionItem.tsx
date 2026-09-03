import { type ProtectionDecision, type ProtectionClassification } from '../types/audit';
import { CheckCircle, AlertTriangle, Circle, ChevronRight, Zap, Brain } from 'lucide-react';

const ICONS: Record<ProtectionClassification, typeof CheckCircle> = {
  Protected: CheckCircle,
  'Mneme-ready': Zap,
  'Requires modelling': Brain,
  Guidance: Circle,
};

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

const CLASSIFICATION_DESC: Record<ProtectionClassification, string> = {
  Protected: 'Mneme enforces this decision deterministically in CI/CD.',
  'Mneme-ready': 'Complete specification exists; ready for rule generation.',
  'Requires modelling': 'Needs architectural modelling before protection is possible.',
  Guidance: 'Expresses intent without machine-testable constraints.',
};

const CONFIDENCE_ICONS: Record<'high' | 'medium' | 'low', typeof CheckCircle> = {
  high: CheckCircle,
  medium: AlertTriangle,
  low: Circle,
};

const CONFIDENCE_COLORS: Record<'high' | 'medium' | 'low', string> = {
  high: 'var(--teal)',
  medium: 'var(--warning)',
  low: 'var(--muted)',
};

interface DecisionItemProps {
  decision: ProtectionDecision;
  onClick: () => void;
}

export function DecisionItem({ decision, onClick }: DecisionItemProps) {
  const Icon = ICONS[decision.protection_classification];
  const iconClass = ICON_CLASS[decision.protection_classification];
  const badgeClass = BADGE_CLASS[decision.protection_classification];
  const badgeLabel = BADGE_LABEL[decision.protection_classification];

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

interface CollapsibleDecisionItemProps {
  decision: ProtectionDecision;
  isExpanded: boolean;
  onToggle: () => void;
  onViewDetails: () => void;
}

export function CollapsibleDecisionItem({ decision, isExpanded, onToggle, onViewDetails }: CollapsibleDecisionItemProps) {
  const Icon = ICONS[decision.protection_classification];
  const iconClass = ICON_CLASS[decision.protection_classification];
  const badgeClass = BADGE_CLASS[decision.protection_classification];
  const badgeLabel = BADGE_LABEL[decision.protection_classification];
  const description = CLASSIFICATION_DESC[decision.protection_classification];

  const ConfidenceIcon = CONFIDENCE_ICONS[decision.evidence_confidence];
  const confidenceColor = CONFIDENCE_COLORS[decision.evidence_confidence];

  return (
    <article className={`decision-item ${isExpanded ? 'is-expanded' : ''}`} role="listitem">
      <div className="decision-item-header" onClick={onToggle} style={{ cursor: 'pointer' }}>
        <div className={`decision-icon ${iconClass}`}>
          <Icon size={20} />
        </div>
        <div className="decision-content">
          <div className="decision-header-top">
            <h3 className="decision-title">{decision.title}</h3>
            <span className="decision-source-badge">{decision.source.file}</span>
          </div>
          <div className="flex flex-wrap items-center gap-2 mt-1">
            <span className={`badge ${badgeClass}`}>{badgeLabel}</span>
            <span className="decision-classification-desc" style={{ fontSize: '0.7rem', color: 'var(--muted)' }}>{description}</span>
          </div>
        </div>
        <div className="decision-chevron">
          <ChevronRight size={18} style={{ color: 'var(--muted)', transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)', transition: 'transform 0.15s ease' }} />
        </div>
      </div>

      {isExpanded && (
        <div className="decision-item-expanded">
          <div className="decision-expanded-content">
            <div className="decision-expanded-row">
              <span className="decision-expanded-label">Requirement</span>
              <p className="decision-expanded-value">{decision.requirement}</p>
            </div>
            <div className="decision-expanded-row">
              <span className="decision-expanded-label">Applies To</span>
              <div className="decision-expanded-value">
                {decision.applies_to.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {decision.applies_to.map((path, i) => (
                      <span key={i} className="font-mono text-xs px-2 py-1 bg-surface2 border border-border rounded">{path}</span>
                    ))}
                  </div>
                ) : (
                  <span className="text-muted">Not specified</span>
                )}
              </div>
            </div>
            <div className="decision-expanded-row">
              <span className="decision-expanded-label">Proposed Mneme Rule</span>
              <div className="decision-expanded-value">
                {decision.proposed_rule ? (
                  <>
                    <code>{decision.proposed_rule.type} "{decision.proposed_rule.pattern}"</code>
                    <p className="mt-1 text-sm text-muted font-normal font-sans">{decision.proposed_rule.description}</p>
                  </>
                ) : (
                  <span className="text-muted">No deterministic rule defined</span>
                )}
              </div>
            </div>
            <div className="decision-expanded-row">
              <span className="decision-expanded-label">Evidence Confidence</span>
              <div className="flex items-center gap-2">
                <ConfidenceIcon size={16} style={{ color: confidenceColor }} />
                <span className="decision-expanded-value font-mono" style={{ color: confidenceColor }}>
                  {decision.evidence_confidence.charAt(0).toUpperCase() + decision.evidence_confidence.slice(1)}
                </span>
              </div>
            </div>
            <div className="decision-expanded-row">
              <span className="decision-expanded-label">Source</span>
              <span className="decision-expanded-value font-mono text-xs">{decision.source.file} (Lines {decision.source.lines})</span>
            </div>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); onViewDetails(); }}
            className="btn btn-ghost btn-sm mt-3"
            data-cta-intent="view_details"
            data-cta-position="decision_list"
          >
            View Full Details
          </button>
        </div>
      )}
    </article>
  );
}