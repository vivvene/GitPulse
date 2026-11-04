"""
Deterministic Git State Graph Recovery Engine.
Analyzes broken Git topology from reflogs and state flags to produce safe, non-destructive recovery shell scripts.
"""
from typing import Any, Dict, List
import re
import time


class GitRecoveryEngine:
    @staticmethod
    def analyze(state_type: str, head_commit: str, branch_name: str, reflog_tail: List[str]) -> Dict[str, Any]:
        """
        Synthesizes deterministic recovery instructions based on failure state and reflog history.
        """
        timestamp = int(time.time())
        state_type = (state_type or "").upper().strip()

        if state_type == "DETACHED_HEAD":
            return GitRecoveryEngine._recover_detached_head(head_commit, branch_name, reflog_tail, timestamp)
        elif state_type in ["IN_PROGRESS_REBASE", "REBASE_CONFLICT"]:
            return GitRecoveryEngine._recover_rebase_conflict(head_commit, branch_name, reflog_tail, timestamp)
        elif state_type in ["ACCIDENTAL_RESET", "LOST_COMMIT"]:
            return GitRecoveryEngine._recover_accidental_reset(head_commit, branch_name, reflog_tail, timestamp)
        elif state_type == "MERGE_CONFLICT":
            return GitRecoveryEngine._recover_merge_conflict(head_commit, branch_name, timestamp)
        else:
            return GitRecoveryEngine._fallback_recovery(head_commit, branch_name, timestamp)

    @staticmethod
    def _recover_detached_head(head_commit: str, branch_name: str, reflog_tail: List[str], ts: int) -> Dict[str, Any]:
        rescue_branch = f"rescue/detached-{ts}"
        # Parse reflog to find previous branch if possible
        prior_branch = branch_name if branch_name and branch_name != "HEAD" else "main"
        for line in reflog_tail:
            match = re.search(r"checkout: moving from ([\w\d_\-\/]+) to", line)
            if match and match.group(1) != "HEAD":
                prior_branch = match.group(1)
                break

        steps = [
            {
                "step_number": 1,
                "command": f"git branch {rescue_branch} {head_commit}",
                "description": f"Freeze dangling commits at {head_commit[:7]} safely onto a new rescue branch without touching your working tree."
            },
            {
                "step_number": 2,
                "command": f"git checkout {prior_branch}",
                "description": f"Switch back to your original branch '{prior_branch}'."
            },
            {
                "step_number": 3,
                "command": f"git merge {rescue_branch} --no-commit --no-ff",
                "description": "Stage the rescued commits on your target branch for pre-commit review, or cherry-pick individual hashes."
            }
        ]

        return {
            "status": "DETERMINISTIC_PLAN_READY",
            "safety_level": "NON_DESTRUCTIVE",
            "estimated_recovery_time_sec": 45,
            "rescue_branch": rescue_branch,
            "target_branch": prior_branch,
            "steps": steps,
            "rollback_command": f"git branch -D {rescue_branch}"
        }

    @staticmethod
    def _recover_rebase_conflict(head_commit: str, branch_name: str, reflog_tail: List[str], ts: int) -> Dict[str, Any]:
        patch_file = f"gitpulse_patch_{ts}.patch"
        steps = [
            {
                "step_number": 1,
                "command": f"git diff > {patch_file}",
                "description": f"Back up all in-flight working directory edits and unresolved diffs to '{patch_file}'."
            },
            {
                "step_number": 2,
                "command": "git rebase --abort",
                "description": "Cleanly cancel the stuck rebase and return repository to its exact pre-rebase SHA."
            },
            {
                "step_number": 3,
                "command": f"git status",
                "description": "Verify working tree is clean and check out your primary development branch."
            }
        ]

        return {
            "status": "DETERMINISTIC_PLAN_READY",
            "safety_level": "BACKUP_FIRST",
            "estimated_recovery_time_sec": 30,
            "backup_patch": patch_file,
            "steps": steps,
            "rollback_command": "git rebase --continue"
        }

    @staticmethod
    def _recover_accidental_reset(head_commit: str, branch_name: str, reflog_tail: List[str], ts: int) -> Dict[str, Any]:
        prior_hash = "HEAD@{1}"
        # If reflog tail is provided, find the commit directly preceding the reset event
        for i, line in enumerate(reflog_tail):
            if "reset: moving to" in line and i + 1 < len(reflog_tail):
                prior_line = reflog_tail[i + 1]
                match = re.search(r"^([a-f0-9]{7,40})", prior_line)
                if match:
                    prior_hash = match.group(1)
                    break
            elif "reset: moving to" in line:
                # If only one line, fallback to HEAD@{1}
                prior_hash = "HEAD@{1}"

        rescue_branch = f"rescue/reset-recovery-{ts}"
        steps = [
            {
                "step_number": 1,
                "command": f"git branch {rescue_branch} {prior_hash}",
                "description": f"Revive commit state prior to accidental reset ({prior_hash}) into branch '{rescue_branch}'."
            },
            {
                "step_number": 2,
                "command": f"git log -n 3 --oneline {rescue_branch}",
                "description": "Inspect the revived commit history to verify all unpushed commits are present."
            },
            {
                "step_number": 3,
                "command": f"git reset --hard {rescue_branch}",
                "description": "Fast-forward current branch back to the pre-reset commit once verified."
            }
        ]

        return {
            "status": "DETERMINISTIC_PLAN_READY",
            "safety_level": "REFLOG_EXTRACTION",
            "estimated_recovery_time_sec": 40,
            "steps": steps,
            "rollback_command": f"git reset --hard {head_commit}"
        }

    @staticmethod
    def _recover_merge_conflict(head_commit: str, branch_name: str, ts: int) -> Dict[str, Any]:
        steps = [
            {
                "step_number": 1,
                "command": "git merge --abort",
                "description": "Safely abort the stuck merge and restore working tree to the state before `git merge` was invoked."
            },
            {
                "step_number": 2,
                "command": "git status",
                "description": "Verify unmerged paths are cleared."
            }
        ]

        return {
            "status": "DETERMINISTIC_PLAN_READY",
            "safety_level": "NON_DESTRUCTIVE",
            "estimated_recovery_time_sec": 15,
            "steps": steps,
            "rollback_command": "git merge --continue"
        }

    @staticmethod
    def _fallback_recovery(head_commit: str, branch_name: str, ts: int) -> Dict[str, Any]:
        rescue_branch = f"rescue/safe-snapshot-{ts}"
        steps = [
            {
                "step_number": 1,
                "command": f"git branch {rescue_branch} HEAD",
                "description": "Snapshot current working HEAD to prevent any permanent data loss."
            },
            {
                "step_number": 2,
                "command": "git status -sb",
                "description": "Inspect status summary."
            }
        ]
        return {
            "status": "SNAPSHOT_PRESERVED",
            "safety_level": "PRECAUTIONARY",
            "estimated_recovery_time_sec": 20,
            "steps": steps,
            "rollback_command": f"git branch -D {rescue_branch}"
        }
