import React from 'react';
import { RepoMetricsResponse } from '../types/telemetry';

interface Props {
  metrics: RepoMetricsResponse;
}

export const HealthDashboard: React.FC<Props> = ({ metrics }) => {
  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-emerald-400 border-emerald-500/30 bg-emerald-950/20';
    if (score >= 60) return 'text-yellow-400 border-yellow-500/30 bg-yellow-950/20';
    return 'text-rose-400 border-rose-500/30 bg-rose-950/20';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {/* Metric 1: Health Score */}
      <div className={`p-4 rounded-xl border ${getScoreColor(metrics.health_score)} flex flex-col justify-between`}>
        <div className="text-xs font-semibold tracking-wide uppercase text-slate-400">
          Repo Stability Score
        </div>
        <div className="text-3xl font-black mt-2 font-mono">
          {metrics.health_score}<span className="text-sm font-normal text-slate-400">/100</span>
        </div>
        <div className="text-xs text-slate-400 mt-1">
          Atomic DynamoDB Evaluation
        </div>
      </div>

      {/* Metric 2: Total Incidents */}
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
        <div className="text-xs font-semibold tracking-wide uppercase text-slate-400">
          Total Incidents Logged
        </div>
        <div className="text-3xl font-black mt-2 font-mono text-slate-100">
          {metrics.total_incidents_recorded}
        </div>
        <div className="text-xs text-slate-400 mt-1">
          Zero-waste payload ingest
        </div>
      </div>

      {/* Metric 3: Idle Cost */}
      <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-950/10 flex flex-col justify-between">
        <div className="text-xs font-semibold tracking-wide uppercase text-emerald-400">
          Monthly Cloud Floor
        </div>
        <div className="text-3xl font-black mt-2 font-mono text-emerald-300">
          ₹0.00 <span className="text-xs font-normal text-slate-400">($0.00)</span>
        </div>
        <div className="text-xs text-slate-400 mt-1">
          100% Serverless Always-Free
        </div>
      </div>

      {/* Metric 4: Recovery Engine Latency */}
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
        <div className="text-xs font-semibold tracking-wide uppercase text-slate-400">
          Lambda Execution P95
        </div>
        <div className="text-3xl font-black mt-2 font-mono text-indigo-400">
          ~118ms
        </div>
        <div className="text-xs text-slate-400 mt-1">
          ARM64 Graviton2 128MB
        </div>
      </div>
    </div>
  );
};
