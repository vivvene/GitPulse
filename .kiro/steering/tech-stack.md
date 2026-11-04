---
inclusion: always
---
# Tech Stack & Implementation Standards

## Backend Stack
- **Runtime:** Python 3.12 or Node.js 20.x on AWS Lambda (ARM64 Graviton2).
- **Infrastructure as Code (IaC):** AWS Serverless Application Model (SAM) or AWS CDK.
- **Database Client:** AWS SDK v3 modular imports (`@aws-sdk/client-dynamodb`, `@aws-sdk/lib-dynamodb`) for TypeScript, or standard `boto3` client initialized at module-level in Python.
- **API Pattern:** AWS Lambda Function URLs with CORS support and lightweight header/JWT authentication.
- **Testing:** Pytest for Python or Vitest for Node.js, targeting unit-level handler isolation with mocked DynamoDB responses.

## Frontend Stack
- **Framework:** React 18+ with TypeScript.
- **Bundler:** Vite (fast ESM build, tiny bundle footprint < 500KB gzipped).
- **Styling:** Tailwind CSS with Lucide Icons.
- **State & Data Fetching:** Lightweight React hooks (`fetch` or `@tanstack/react-query`) with zero unnecessary external runtime bloat.
- **Type Sharing:** Shared TypeScript interfaces synchronized between backend payloads and frontend components via `.kiro/hooks/sync-api-schema.json`.

## Code Quality Standards
- Strict TypeScript configuration (`noImplicitAny`, `strictNullChecks`).
- Clean separation of concerns:
  - `handlers/`: Lambda entrypoints, request validation, response serialization.
  - `domain/`: Business logic, deterministic Git state graph analysis, graph repair algorithms.
  - `storage/`: DynamoDB Single-Table data access layer.
