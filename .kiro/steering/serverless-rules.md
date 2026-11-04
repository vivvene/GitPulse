---
inclusion: always
---
# Serverless & Cost-Optimization Standards

## Architectural Guardrails
- **Zero Idle Cost ($0.00 Floor):** Never provision EC2 instances, RDS databases, NAT Gateways, Elastic Load Balancers, or OpenSearch clusters. The system must scale to absolute zero when not receiving traffic.
- **Stateless Compute:** All compute workloads run inside AWS Lambda targeting the ARM64 architecture (`graviton2`) with strict 128MB to 256MB memory allocations and <15-second execution timeouts.
- **Direct Function URLs over API Gateway:** Prefer Lambda Function URLs (with IAM or custom auth headers + CORS) for CRUD and webhook ingest endpoints to eliminate API Gateway per-million request fees (~$1.00 - $3.50/M) and stay strictly inside the Lambda free tier.
- **Single-Table DynamoDB Design:** All application entities (repositories, incidents, recovery steps, team telemetry, users) must reside inside a single DynamoDB table utilizing generic composite partition/sort keys (`PK`, `SK`) and at most one Global Secondary Index (`GSI1PK`, `GSI1SK`). Provisioning multiple tables is strictly prohibited.
- **Zero Idle Capacity:** Use DynamoDB On-Demand Billing mode (or 25 RCU / 25 WCU Always-Free provisioned mode) so no capacity costs accrue when idle.
- **Lightweight Auth:** Amazon Cognito User Pools on the Lite tier (up to 10,000 monthly active users completely free) for identity and JWT verification.
- **Edge Static Hosting:** Host the frontend using AWS Amplify or S3 + CloudFront (1 TB data transfer out, 10M requests free tier).

## Code & Runtime Performance Guardrails
- **Connection & Client Reuse:** Initialize all AWS SDK clients (`boto3` or `@aws-sdk/client-*`) outside the handler function scope to enable HTTP keep-alive connection reuse across warm invocations.
- **Strict Payload Validation:** Validate incoming request payloads prior to executing any database reads or writes to prevent unnecessary DynamoDB capacity consumption on malformed requests.
- **Minimal Dependencies:** Bundle only lightweight zero-runtime dependencies (standard libraries where possible). Avoid heavy ORMs or heavyweight web frameworks (no Express/Nest/Django).
