import { type AuditSummary } from '../types/audit';
import { CheckCircle, AlertTriangle, Circle, Target } from 'lucide-react';
import { InfoTooltip } from './InfoTooltip';
import { FIELD_HELP } from '../utils/auditInsights';

interface StatsGridProps {
  summary: AuditSummary;
}

const STATS = [
  { key: 'totalDecisions', label: 'GOVERNANCE ITEMS', icon: Target, color: 'var(--text)', tooltip: 'All documented decisions, agent instructions, and configuration evidence Mneme found in the repository.' },
  { 
    key: 'enforceable', 
    label: 'ENFORCEABLE NOW', 
    icon: CheckCircle, 
    color: 'var(--teal)',
    tooltip: 'Enforceable means Mneme can translate the decision into a deterministic control. A zero does not mean no architecture decisions were found.'
  },
  { 
    key: 'partial', 
    label: 'PARTIALLY ENFORCEABLE', 
    icon: AlertTriangle, 
    color: 'var(--warning)',
    tooltip: 'Partially enforceable means some aspects can be tested but the decision lacks complete specification for deterministic enforcement.'
  },
  { key: 'guidance', label: 'GUIDANCE ONLY', icon: Circle, color: 'var(--muted)', tooltip: 'Guidance means the decision describes intent but does not specify a machine-testable constraint.' },
] as const;

export function StatsGrid({ summary }: StatsGridProps) {
  const categoryBreakdown = [
    ['Architecture decisions', summary.byCategory?.architecture_decision],
    ['Agent instructions', summary.byCategory?.agent_instruction],
    ['Config evidence', summary.byCategory?.config_evidence],
  ].filter((entry): entry is [string, number] => typeof entry[1] === 'number');

  return (
    <div className="stats-grid" role="region" aria-label="Audit statistics">
      {STATS.map(({ key, label, icon: Icon, color, tooltip }) => {
        const value = summary[key as keyof AuditSummary] as number;
        return (
          <div 
            key={key} 
            className="stat-card"
          >
            <div style={{ color }} className="flex items-center justify-center gap-2 mb-2">
              <Icon size={20} />
            </div>
            <div className="stat-value" style={{ color }}>{value}</div>
            <div className="stat-label-row">
              <div className="stat-label">{label}</div>
              <InfoTooltip label={label}>{tooltip}</InfoTooltip>
            </div>
            {key === 'totalDecisions' && categoryBreakdown.length > 0 && (
              <div className="stat-category-breakdown" aria-label="Governance item categories">
                {categoryBreakdown.map(([category, count]) => (
                  <span key={category}><strong>{count}</strong> {category}</span>
                ))}
              </div>
            )}
          </div>
        );
      })}
      <div className="stat-card">
        <div className="flex items-center justify-center gap-2 mb-2" style={{ color: 'var(--accent)' }}>
          <Target size={20} />
        </div>
        <div className="stat-value" style={{ color: 'var(--accent)' }}>{summary.coverage}%</div>
        <div className="stat-label-row">
          <div className="stat-label">COVERAGE</div>
          <InfoTooltip label="Coverage">{FIELD_HELP.coverage}</InfoTooltip>
        </div>
        <div className="progress-bar mt-2" role="progressbar" aria-valuenow={summary.coverage} aria-valuemin={0} aria-valuemax={100}>
          <div className="progress-fill" style={{ width: `${summary.coverage}%` }}></div>
        </div>
      </div>
    </div>
  );
}
