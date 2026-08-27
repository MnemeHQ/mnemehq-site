import { type AuditSummary } from '../types/audit';
import { CheckCircle, AlertTriangle, Circle, Target } from 'lucide-react';

interface StatsGridProps {
  summary: AuditSummary;
}

const STATS = [
  { key: 'totalDecisions', label: 'DECISIONS IDENTIFIED', icon: Target, color: 'var(--text)' },
  { key: 'enforceable', label: 'ENFORCEABLE NOW', icon: CheckCircle, color: 'var(--teal)' },
  { key: 'partial', label: 'PARTIALLY ENFORCEABLE', icon: AlertTriangle, color: 'var(--warning)' },
  { key: 'guidance', label: 'GUIDANCE ONLY', icon: Circle, color: 'var(--muted)' },
] as const;

export function StatsGrid({ summary }: StatsGridProps) {
  return (
    <div className="stats-grid" role="region" aria-label="Audit statistics">
      {STATS.map(({ key, label, icon: Icon, color }) => (
        <div key={key} className="stat-card">
          <div style={{ color }} className="flex items-center justify-center gap-2 mb-2">
            <Icon size={20} />
          </div>
          <div className="stat-value" style={{ color }}>{summary[key as keyof AuditSummary]}</div>
          <div className="stat-label">{label}</div>
        </div>
      ))}
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