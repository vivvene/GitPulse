# Implementation Tasks: Git Recovery & Telemetry Hub

This document defines the discrete, sequenced implementation tasks required to deliver the core functionality described in `requirements.md` and `design.md`.

---

## Phase 1: Foundation & Steering Verification
- [x] **Task 1.1: Initialize Steering & Guardrails**
  - Verify `.kiro/steering/serverless-rules.md` is active.
  - Verify `.kiro/steering/tech-stack.md` defines AWS SDK v3 / boto3 reuse rules.
  - Set up `.kiro/hooks/guard-serverless-saves.json` for automated linting on file save.

## Phase 2: Serverless Infrastructure (IaC)
- [x] **Task 2.1: Author AWS SAM Template**
  - Configure `template.yaml` with ARM64 (`graviton2`) Lambda architecture.
  - Provision Single-Table DynamoDB (`gitpulse_core`) with On-Demand billing.
  - Define composite keys (`PK`, `SK`) and GSI (`GSI1PK`, `GSI1SK`).
  - Configure Lambda Function URLs with CORS and Auth headers.
  - Provision Cognito User Pool with client app credentials (Lite Tier).

## Phase 3: Core Backend & Recovery Engine
- [x] **Task 3.1: Ingestion & Schema Validation Handler**
  - Create `backend/src/handlers/ingest_telemetry.py`.
  - Implement zero-allocation payload validation for `repo_id`, `state_type`, and `reflog_tail`.
  - Return early 400 Bad Request on invalid payloads to preserve DynamoDB capacity units.
- [x] **Task 3.2: Deterministic Git Graph Recovery Engine**
  - Create `backend/src/utils/git_graph.py`.
  - Implement graph resolution for `DETACHED_HEAD`, `IN_PROGRESS_REBASE`, and `ACCIDENTAL_RESET`.
  - Generate idempotent shell script sequences with fail-safe abort options.
- [x] **Task 3.3: Metrics & Dashboard Query Handler**
  - Create `backend/src/handlers/get_metrics.py`.
  - Query DynamoDB GSI1 for the latest 50 repository incidents.
  - Calculate repository stability score ($0 - 100$).
- [x] **Task 3.4: Automated Unit & Recovery Test Suite**
  - Create `backend/tests/test_recovery.py`.
  - Verify recovery script synthesis against mock reflog traces.

## Phase 4: Frontend Dashboard & Replay Terminal
- [x] **Task 4.1: React + Vite + Tailwind Scaffolding**
  - Configure `frontend/package.json` with minimal dependencies.
  - Create TypeScript type contracts in `frontend/src/types/telemetry.ts`.
- [x] **Task 4.2: Repository Health & Incident Feed UI**
  - Build `frontend/src/components/HealthDashboard.tsx` with metrics cards.
  - Build `frontend/src/components/IncidentFeed.tsx` for real-time failure log inspection.
- [x] **Task 4.3: Interactive Recovery Script Terminal**
  - Build `frontend/src/components/RecoveryTerminal.tsx` allowing developers to copy verified recovery commands.

## Phase 5: Submission & Verification Deliverables
- [x] **Task 5.1: AWS Pricing Calculator Breakdown**
  - Complete the exact itemized cost calculations for 1,000 MAUs.
  - Document $0.00 Free Tier total and $0.38 Pay-As-You-Go sub-$1 bonus proof.
- [x] **Task 5.2: README & Submission Note**
  - Add the 3–5 line Kiro reflection in `README.md`.
  - Add quickstart guide for local execution and cloud deployment.
