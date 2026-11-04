import React from 'react';
import { GitIncident } from '../types/telemetry';

interface Props {
  incidents: GitIncident[];
  selectedId: string | null;
  onSelect: (incident: GitIncident) => void;
}

export const IncidentFeed: React.FC<Props> = ({ incidents, selectedId, onSelect }) => {
  if (!incidents || incidents.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 text-center text-slate-400">
        <p className="font-medium text-slate-300">No Git state incidents logged yet.</p>
        <p className="text-xs text-slate-500 mt-1">Run a local webhook or `gitpulse heal` to send telemetry.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {incidents.map((inc) => {
        const isSelected = selectedId === inc.incident_id;
        const dateStr = new Date(inc.created_at * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        return (
          <div
            key={inc.incident_id}
            onClick={() => onSelect(inc)}
            className={`p-4 rounded-xl border cursor-pointer transition text-left ${
              isSelected 
                ? 'bg-slate-800/90 border-indigo-500 shadow-md ring-1 ring-indigo-500/50' 
                : 'bg-slate-900/80 border-slate-800 hover:border-slate-700 hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-mono font-semibold text-indigo-400 uppercase tracking-wider">
                {inc.state_type.replace(/_/g, ' ')}
              </span>
              <span className="text-xs text-slate-400 font-mono">{dateStr}</span>
            </div>

            <div className="text-sm font-semibold text-slate-200 truncate">
              {inc.branch_name} @ {inc.head_commit.substring(0, 7)}
            </div>

            <div className="flex items-center justify-between mt-3 text-xs text-slate-400">
              <span>Author: <strong className="text-slate-300 font-normal">{inc.author}</strong></span>
              <span className="px-2 py-0.5 rounded-full text-xs font-mono bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                {inc.status}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
