import { type ProtectionSummary } from '../types/audit';
import { Shield, CheckCircle, AlertTriangle, Circle, Target } from 'lucide-react';
import { useState } from 'react';

const STATS = [
  { key: 'decisions_discovered', label: 'DECISIONS IDENTIFIED', icon: Target, color: 'var(--text)', tooltip: 'Total architectural decisions discovered in the repository' },
  { key: 'protection_relevant', label: 'PROTECTION-RELEVANT', icon: Shield, color: 'var(--accent)', tooltip: 'Decisions that can meaningfully be protected by Mneme (excludes pure guidance)' },
  { key: 'protected_count', label: 'PROTECTED', icon: CheckCircle, color: 'var(--teal)', tooltip: 'Decisions with deterministic Mneme enforcement evidence identified by the audit' },
  { key: 'mneme_ready_count', label: 'MNEME-READY', icon: AlertTriangle, color: 'var(--warning)', tooltip: 'Decisions with complete specifications ready for rule generation' },
  { key: 'requires_modelling_count', label: 'REQUIRES MODELLING', icon: AlertTriangle, color: 'var(--warning)', tooltip: 'Decisions needing architectural modelling before they can be protected' },
  { key: 'guidance_count', label: 'GUIDANCE ONLY', icon: Circle, color: 'var(--muted)', tooltip: 'Decisions expressing intent without machine-testable constraints' },
] as const;

interface StatsGridProps {
  summary: ProtectionSummary;
}

export function StatsGrid({ summary }: StatsGridProps) {
  const [activeTooltip, setActiveTooltip] = useState<string | null>(null);

  const showTooltip = (tooltip: string) => {
    if (tooltip) setActiveTooltip(tooltip);
  };

  const hideTooltip = () => setActiveTooltip(null);

  return (
    <div className="stats-grid" role="region" aria-label="Protection audit statistics">
      {STATS.map(({ key, label, icon: Icon, color, tooltip }) => {
        const value = summary[key as keyof ProtectionSummary] as number;
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
      <div className="stat-card protection-summary-card">
        <div className="flex items-center justify-center gap-2 mb-2" style={{ color: 'var(--accent)' }}>
          <Shield size={20} />
        </div>
        <div className="stat-value" style={{ color: 'var(--accent)' }}>
          {Math.round(summary.current_protection * 100)}%
        </div>
        <div className="stat-label">CURRENT PROTECTION</div>
        <div className="progress-bar mt-2" role="progressbar" aria-valuenow={Math.round(summary.current_protection * 100)} aria-valuemin={0} aria-valuemax={100}>
          <div className="progress-fill" style={{ width: `${summary.current_protection * 100}%` }}></div>
        </div>
        {summary.mneme_ready_count > 0 && (
          <div className="mt-2 text-xs text-muted">
            Mneme Potential: {Math.round(summary.identified_mneme_potential * 100)}%
          </div>
        )}
      </div>
    </div>
  );
}
