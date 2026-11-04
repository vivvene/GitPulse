# Design Specification: Git Recovery & Telemetry Hub

## 1. High-Level Architecture Overview

The GitPulse system operates on an event-driven, scale-to-zero serverless architecture designed to eliminate idle costs while delivering sub-200ms recovery generation.

```mermaid
flowchart TD
    subgraph ClientLayer ["Client & Edge Layer"]
        CLI["Developer CLI / Webhook<br/>(gitpulse / git-healer)"]
        Dashboard["React + Vite + Tailwind Dashboard<br/>(Amplify / CloudFront + S3)"]
    end

    subgraph AuthLayer ["Authentication Layer"]
        Cognito["Amazon Cognito User Pool<br/>(Free Tier: 10k MAUs)"]
    end

    subgraph ComputeLayer ["Serverless Compute (Lambda Function URLs)"]
        IngestLambda["Ingest & Recovery Lambda<br/>(ARM64 128MB Python 3.12)"]
        MetricsLambda["Metrics & Query Lambda<br/>(ARM64 128MB Python 3.12)"]
    end

    subgraph DataLayer ["Data & Persistence Layer"]
        Dynamo["Amazon DynamoDB Single-Table<br/>(On-Demand / Free-Tier)"]
    end

    CLI -->|POST /telemetry + API Key| IngestLambda
    Dashboard -->|Authenticate| Cognito
    Dashboard -->|GET /metrics + JWT Bearer| MetricsLambda
    IngestLambda -->|Validate & PutItem / UpdateItem| Dynamo
    MetricsLambda -->|Query GSI1PK / GSI1SK| Dynamo
```

---

## 2. Single-Table DynamoDB Design

All application entities reside in a single table named `gitpulse_core`.

### Primary Keys & GSI Structure
- **Table Partition Key (PK):** `String`
- **Table Sort Key (SK):** `String`
- **GSI1 Partition Key (GSI1PK):** `String`
- **GSI1 Sort Key (GSI1SK):** `String`

### Entity Access Patterns Table

| Entity | PK | SK | GSI1PK | GSI1SK | Attributes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Repository Metadata** | `REPO#<repo_id>` | `METADATA` | `ORG#<org_id>` | `REPO#<repo_id>` | `name`, `default_branch`, `created_at`, `health_score` |
| **Incident Telemetry** | `REPO#<repo_id>` | `INCIDENT#<timestamp>#<incident_id>` | `REPO#<repo_id>` | `INCIDENT#<timestamp>` | `incident_id`, `state_type`, `head_commit`, `reflog_tail`, `recovery_plan`, `status` |
| **Recovery Playbook** | `INCIDENT#<incident_id>` | `RECOVERY` | `REPO#<repo_id>` | `STATUS#<status>` | `steps[]`, `safety_level`, `created_at`, `executed_at` |
| **Repository Daily Metrics** | `REPO#<repo_id>` | `METRICS#<date_YYYY-MM-DD>` | `ORG#<org_id>` | `DATE#<date>` | `total_incidents`, `resolved_incidents`, `avg_resolution_ms` |

---

## 3. Sequence Diagrams

### 3.1 Telemetry Ingestion & Deterministic Recovery Computation

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer / CLI
    participant URL as Lambda Function URL
    participant Handler as Ingest Lambda (ARM64)
    participant Engine as Recovery Engine
    participant DDB as DynamoDB (Single-Table)

    Dev->>URL: POST /telemetry (Git state, reflog tail, repo_id)
    URL->>Handler: Invoke with event payload
    Handler->>Handler: Validate schema (guard zero-wasted-writes)
    alt Invalid Payload
        Handler-->>Dev: 400 Bad Request
    else Valid Payload
        Handler->>Engine: analyze_git_state(state, reflog)
        Engine->>Engine: Compute deterministic rescue steps
        Handler->>DDB: PutItem(PK=REPO#..., SK=INCIDENT#...) with recovery_plan
        Handler->>DDB: UpdateItem (Atomic counter on Daily Metrics)
        Handler-->>Dev: 201 Created (incident_id, recovery_plan)
    end
```

### 3.2 Dashboard Telemetry & Metrics Querying

```mermaid
sequenceDiagram
    autonumber
    actor User as Engineering Lead
    participant Web as React + Vite SPA
    participant Cognito as Amazon Cognito
    participant URL as Lambda Function URL (/metrics)
    participant DDB as DynamoDB (Single-Table)

    User->>Web: Open Dashboard
    Web->>Cognito: Authenticate user & get JWT
    Web->>URL: GET /metrics?repo_id=repo-123 (Authorization: Bearer JWT)
    URL->>DDB: Query GSI1 (GSI1PK = REPO#repo-123)
    DDB-->>URL: Returns recent 50 incidents & health metrics
    URL-->>Web: JSON payload (health_score, incidents, friction_points)
    Web-->>User: Render interactive charts & terminal replay
```

---

## 4. Deterministic Recovery Algorithm Specification

The recovery engine executes state-machine graph traversal on the received `reflog_tail` and `branch_state`:
1. **Detached HEAD State (`DETACHED_HEAD`):**
   - Identify current `HEAD` SHA.
   - Scan reflog backwards to find the last known branch checkout transition (`checkout: moving from <branch> to <hash>`).
   - Emit safe commands:
     ```bash
     git branch rescue-<timestamp> <HEAD_SHA>
     git checkout <last_known_branch>
     git merge rescue-<timestamp> --ff-only || echo "Manual merge inspection required"
     ```
2. **Botched Interactive Rebase (`IN_PROGRESS_REBASE`):**
   - Check presence of `.git/rebase-merge` or `.git/rebase-apply`.
   - Synthesize differential safety patch:
     ```bash
     git diff > gitpulse_emergency.patch
     git rebase --abort
     ```
3. **Accidental Hard Reset (`ACCIDENTAL_RESET`):**
   - Identify prior commit before reset in `HEAD@{1}` or `HEAD@{2}`.
   - Synthesize recovery branch:
     ```bash
     git branch recovered-work HEAD@{1}
     ```

---

## 5. Security & Cost Optimization Verification
- **No NAT Gateway:** Handlers run in default serverless environment with direct AWS service endpoints.
- **Function URLs:** Eliminates API Gateway base cost.
- **Boto3 Client Caching:** Single client instantiated globally across container warm starts.
- **Sub-150ms Execution:** Keeps GB-seconds comfortably inside AWS Always-Free Tier limits.
