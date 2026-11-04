---
inclusion: always
---
# Product Context & Domain Standards

## Product Name: GitPulse (Cloud-Synced Git Recovery & Telemetry Hub)

### Problem Statement
Software engineering teams lose thousands of collective hours when developers botch complex Git operations:
- Accidental `git reset --hard` losing uncommitted or stashed work.
- Botched interactive rebases with conflicts that leave repositories in detached HEAD or halfway through a rebase (`.git/rebase-merge`).
- Stale, dangling commit histories and corrupt reflogs that cause developers to nuke their local repository and re-clone, discarding unpushed work.
- Engineering leadership lacks visibility into developer friction, repository instability hotspots, and recurring workflow anti-patterns.

### Solution Overview
**GitPulse** is a lightweight, zero-idle-cost cloud-synced Git recovery and telemetry hub:
1. **Lightweight Local Telemetry / CLI Plugin:** When a developer encounters a broken git state or runs `gitpulse heal`, local git state metadata (reflog head diffs, rebase status, head commit hash, branch topology) is captured and pushed via a lightweight JSON payload.
2. **Deterministic Serverless Recovery Engine:** An AWS Lambda function executes graph-traversal algorithms against the git state machine to generate a safe, idempotent step-by-step shell recovery script (e.g., `git branch rescue-xyz <hash>`, `git cherry-pick ...`).
3. **Engineering Telemetry Dashboard:** A React + Vite dashboard displaying repository health scores, incident resolution times, team recovery playbooks, and friction analytics.

### Target Personas
- **Developer / Contributor:** Needs instant, deterministic recovery without the fear of destroying work or asking a senior engineer for help.
- **Engineering Lead / Staff Architect:** Wants visibility into team-wide Git failure modes, rebase bottlenecks, and repository health metrics.
