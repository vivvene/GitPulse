# Requirements Specification: Git Recovery & Telemetry Hub (EARS Format)

## 1. Scope & Objective
This specification defines the functional and non-functional requirements for the GitPulse Cloud-Synced Git Recovery & Telemetry Hub. All acceptance criteria strictly adhere to the Easy Approach to Requirements Syntax (EARS) standard.

---

## 2. EARS Requirements

### REQ-001: Telemetry Ingestion (Event-Driven)
- **WHEN** a client CLI or webhook posts a Git state snapshot containing a repository identifier, current HEAD commit, branch state, and reflog tail to the `/telemetry` endpoint,
- **THE SYSTEM SHALL** validate the JSON payload schema within 50 milliseconds.
- **THE SYSTEM SHALL** persist the incident event into the single-table DynamoDB instance using partition key `REPO#<repo_id>` and sort key `INCIDENT#<timestamp>#<incident_id>`.
- **THE SYSTEM SHALL** return an HTTP 201 response containing the created `incident_id` and status `ANALYZING`.

### REQ-002: Deterministic Recovery Plan Generation (State-Driven)
- **WHILE** evaluating an incident characterized by a `DETACHED_HEAD` state,
- **THE SYSTEM SHALL** locate the most recent non-dangling commit reference in the reflog history.
- **THE SYSTEM SHALL** generate a non-destructive sequential shell recovery script comprising:
  1. Temporary rescue branch creation (`git branch rescue-<timestamp> <commit_hash>`)
  2. Safe working directory checkout (`git checkout <target_branch>`)
  3. Optional cherry-pick instructions with clean abort rollbacks (`git cherry-pick --abort`)
- **THE SYSTEM SHALL** update the incident item in DynamoDB with the computed recovery steps within 200 milliseconds.

### REQ-003: Botched Rebase & Merge Conflict Recovery (State-Driven)
- **WHILE** evaluating an incident characterized by an `IN_PROGRESS_REBASE` or `CONFLICTED_MERGE` state,
- **THE SYSTEM SHALL** compute both the safe cancellation pathway (`git rebase --abort` / `git merge --abort`) and the state preserve pathway (`git diff > emergency.patch`).
- **THE SYSTEM SHALL** flag conflicting files and classify severity based on reflog distance.

### REQ-004: Malformed Payload Handling (Unwanted Behavior)
- **IF** an incoming telemetry payload is missing mandatory fields (`repo_id`, `state_type`, or `reflog_tail`),
- **THEN THE SYSTEM SHALL** reject the request with HTTP 400 Bad Request and a structured JSON error body without executing any DynamoDB read or write operations.

### REQ-005: Authentication & Rate Limiting (Event-Driven)
- **WHEN** a request arrives at the Lambda Function URL without a valid Authorization token or API key header,
- **THE SYSTEM SHALL** return an HTTP 401 Unauthorized response and drop the execution immediately.

### REQ-006: Repository Health & Aggregation Metrics (Ubiquitous)
- **THE SYSTEM SHALL** maintain pre-aggregated 24-hour and 7-day health metrics for each registered repository using an atomic DynamoDB counter pattern.
- **THE SYSTEM SHALL** calculate an aggregate Repository Stability Score ($0 - 100$) derived from incident frequency, resolution duration, and clean commit ratios.

### REQ-007: Dashboard Telemetry Feed (Event-Driven)
- **WHEN** an authenticated user loads the React + Vite dashboard for a specific repository,
- **THE SYSTEM SHALL** query the DynamoDB table using GSI1 (`GSI1PK = REPO#<repo_id>`, `GSI1SK begins_with INCIDENT#`) with a query limit of 50 items.
- **THE SYSTEM SHALL** respond with latency under 150 milliseconds.

### REQ-008: Zero Idle Cost & Constraint Enforcement (Ubiquitous)
- **THE SYSTEM SHALL** maintain zero provisioned capacity ($0.00 idle cost) across all cloud resources, relying entirely on AWS Lambda Function URLs, DynamoDB On-Demand billing, and static S3/CloudFront hosting.
