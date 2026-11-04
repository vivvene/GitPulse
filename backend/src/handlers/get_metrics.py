"""
Lambda Handler: Get Metrics & Incident History.
Executes efficient GSI1 query against the Single-Table DynamoDB structure.
"""
import json
from typing import Any, Dict

from utils import dynamo

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization"
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # Handle preflight CORS OPTIONS requests
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {"statusCode": 200, "headers": HEADERS, "body": json.dumps({"status": "ok"})}

    params = event.get("queryStringParameters") or {}
    repo_id = params.get("repo_id", "default-repo")

    # Query GSI1: GSI1PK = REPO#<repo_id>, GSI1SK begins_with INCIDENT#
    gsi1pk = f"REPO#{repo_id}"
    try:
        items = dynamo.query_gsi1(gsi1pk=gsi1pk, begins_with_sk="INCIDENT#", limit=50)
    except Exception as exc:
        print(f"DynamoDB query note: {exc}")
        items = []

    total_incidents = len(items)
    resolved_count = sum(1 for item in items if item.get("status") in ["ANALYZED", "RESOLVED"])

    # Compute deterministic health score (0 - 100)
    # 100 base, -5 per incident, +1 bonus per resolved recovery
    health_score = max(20, min(100, 100 - (total_incidents * 4) + (resolved_count * 2)))

    # Breakdown by incident type
    type_counts: Dict[str, int] = {}
    for it in items:
        st = it.get("state_type", "UNKNOWN")
        type_counts[st] = type_counts.get(st, 0) + 1

    payload = {
        "repo_id": repo_id,
        "health_score": health_score,
        "total_incidents_recorded": total_incidents,
        "breakdown": type_counts,
        "recent_incidents": items[:25]
    }

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps(payload, default=str)
    }
