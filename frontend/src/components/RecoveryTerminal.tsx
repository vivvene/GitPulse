import React, { useState } from 'react';
import { RecoveryPlan } from '../types/telemetry';

interface Props {
  plan: RecoveryPlan;
  incidentId: string;
}

export const RecoveryTerminal: React.FC<Props> = ({ plan, incidentId }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-2xl">
      {/* Terminal Title Bar */}
      <div className="bg-slate-800/80 px-4 py-2.5 flex items-center justify-between border-b border-slate-700">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
          <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
          <span className="text-xs font-mono text-slate-400 ml-2">
            Deterministic Recovery Plan — {incidentId}
          </span>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <span className={`px-2 py-0.5 rounded font-mono font-medium ${
            plan.safety_level === 'NON_DESTRUCTIVE' 
              ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' 
              : 'bg-amber-950 text-amber-400 border border-amber-800'
          }`}>
            {plan.safety_level}
          </span>
          <span className="text-slate-400 font-mono">
            ~{plan.estimated_recovery_time_sec}s
          </span>
        </div>
      </div>

      {/* Terminal Body */}
      <div className="p-4 space-y-4 font-mono text-sm">
        {plan.steps.map((step, idx) => (
          <div key={idx} className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60 hover:border-slate-700 transition">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5">
              <span>Step {step.step_number}: {step.description}</span>
              <button
                onClick={() => copyToClipboard(step.command, idx)}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-sans transition"
              >
                {copiedIndex === idx ? '✓ Copied' : 'Copy'}
              </button>
            </div>
            <div className="flex items-center space-x-2 text-emerald-400 font-bold">
              <span className="text-slate-500 select-none">$</span>
              <code>{step.command}</code>
            </div>
          </div>
        ))}

        {/* Rollback Safeguard */}
        {plan.rollback_command && (
          <div className="mt-4 pt-3 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
            <span className="text-slate-500">Emergency Rollback:</span>
            <code className="text-amber-400/90">{plan.rollback_command}</code>
          </div>
        )}
      </div>
    </div>
  );
};
