import { type AuditSummary } from '../types/audit';
import { CheckCircle, AlertTriangle, Circle, Target } from 'lucide-react';
import { useState } from 'react';

interface StatsGridProps {
  summary: AuditSummary;
}

const STATS = [
  { key: 'totalDecisions', label: 'DECISIONS IDENTIFIED', icon: Target, color: 'var(--text)', tooltip: '' },
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
  const [activeTooltip, setActiveTooltip] = useState<string | null>(null);

  const showTooltip = (tooltip: string) => {
    if (tooltip) setActiveTooltip(tooltip);
  };
  
  const hideTooltip = () => setActiveTooltip(null);

  return (
    <div className="stats-grid" role="region" aria-label="Audit statistics">
      {STATS.map(({ key, label, icon: Icon, color, tooltip }) => {
        const value = summary[key as keyof AuditSummary] as number;
        const isZero = value === 0 && tooltip;
        return (
          <div 
            key={key} 
            className="stat-card"
            onMouseEnter={() => showTooltip(tooltip)}
            onMouseLeave={hideTooltip}
            onFocus={() => showTooltip(tooltip)}
            onBlur={hideTooltip}
            tabIndex={isZero ? 0 : -1}
            role={isZero ? 'button' : undefined}
            aria-label={isZero ? tooltip : undefined}
          >
            <div style={{ color }} className="flex items-center justify-center gap-2 mb-2">
              <Icon size={20} />
            </div>
            <div className="stat-value" style={{ color }}>{value}</div>
            <div className="stat-label">{label}</div>
            {activeTooltip === tooltip && (
              <div className="stat-tooltip" role="tooltip">
                {tooltip}
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
        <div className="stat-label">COVERAGE</div>
        <div className="progress-bar mt-2" role="progressbar" aria-valuenow={summary.coverage} aria-valuemin={0} aria-valuemax={100}>
          <div className="progress-fill" style={{ width: `${summary.coverage}%` }}></div>
        </div>
      </div>
    </div>
  );
}