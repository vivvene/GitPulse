export type IncidentStatus = 'ANALYZED' | 'RESOLVED' | 'PENDING';

export type GitStateType = 
  | 'DETACHED_HEAD' 
  | 'IN_PROGRESS_REBASE' 
  | 'REBASE_CONFLICT' 
  | 'ACCIDENTAL_RESET' 
  | 'MERGE_CONFLICT';

export interface RecoveryStep {
  step_number: number;
  command: string;
  description: string;
}

export interface RecoveryPlan {
  status: string;
  safety_level: 'NON_DESTRUCTIVE' | 'BACKUP_FIRST' | 'REFLOG_EXTRACTION' | 'PRECAUTIONARY';
  estimated_recovery_time_sec: number;
  rescue_branch?: string;
  target_branch?: string;
  backup_patch?: string;
  steps: RecoveryStep[];
  rollback_command: string;
}

export interface GitIncident {
  incident_id: string;
  repo_id: string;
  state_type: GitStateType;
  head_commit: string;
  branch_name: string;
  author: string;
  created_at: number;
  status: IncidentStatus;
  recovery_plan: RecoveryPlan;
}

export interface RepoMetricsResponse {
  repo_id: string;
  health_score: number;
  total_incidents_recorded: number;
  breakdown: Record<string, number>;
  recent_incidents: GitIncident[];
}
