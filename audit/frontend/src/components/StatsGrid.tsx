import { type ProtectionSummary } from '../types/audit';
import { Shield, CheckCircle, AlertTriangle, Circle, Target } from 'lucide-react';
import { InfoTooltip } from './InfoTooltip';

const STATS = [
  { key: 'decisions_discovered', label: 'DECISIONS IDENTIFIED', icon: Target, color: 'var(--text)', tooltip: 'Total architectural decisions discovered in the repository' },
  { key: 'protection_relevant', label: 'PROTECTION-RELEVANT', icon: Shield, color: 'var(--accent)', tooltip: 'Decisions that can meaningfully be protected by Mneme (excludes pure guidance)' },
  { key: 'protected_count', label: 'PROTECTED', icon: CheckCircle, color: 'var(--teal)', tooltip: 'Decisions with deterministic Mneme enforcement evidence identified by the audit' },
  { key: 'mneme_ready_count', label: 'MNEME-READY', icon: AlertTriangle, color: 'var(--warning)', tooltip: 'Decisions with a concrete supported Mneme guardrail identified, but not yet enforced' },
  { key: 'requires_modelling_count', label: 'REQUIRES MODELLING', icon: AlertTriangle, color: 'var(--warning)', tooltip: 'Decisions needing architectural modelling before they can be protected' },
  { key: 'guidance_count', label: 'GUIDANCE ONLY', icon: Circle, color: 'var(--muted)', tooltip: 'Decisions expressing intent without machine-testable constraints' },
] as const;

interface StatsGridProps {
  summary: ProtectionSummary;
}

export function StatsGrid({ summary }: StatsGridProps) {
  const categoryBreakdown = [
    ['Architecture decisions', summary.by_category?.architecture_decision],
    ['Agent instructions', summary.by_category?.agent_instruction],
    ['Config evidence', summary.by_category?.config_evidence],
  ].filter((entry): entry is [string, number] => typeof entry[1] === 'number');

  return (
    <div className="stats-grid" role="region" aria-label="Protection audit statistics">
      {STATS.map(({ key, label, icon: Icon, color, tooltip }) => {
        const value = summary[key as keyof ProtectionSummary] as number;
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
            {key === 'decisions_discovered' && categoryBreakdown.length > 0 && (
              <div className="stat-category-breakdown" aria-label="Governance item categories">
                {categoryBreakdown.map(([category, count]) => (
                  <span key={category}><strong>{count}</strong> {category}</span>
                ))}
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
