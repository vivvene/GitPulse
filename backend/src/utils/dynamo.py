"""
DynamoDB Single-Table Client Utility.
Adheres to Serverless Standards: Global client instantiation for connection reuse across warm invocations.
Includes lightweight local mock fallback when running outside AWS Lambda / without boto3.
"""
import os
from typing import Any, Dict, List, Optional

TABLE_NAME = os.environ.get("TABLE_NAME", "gitpulse_core")

_local_mock_store: Dict[str, Dict[str, Any]] = {}

try:
    import boto3
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)
    HAS_BOTO3 = True
except Exception:
    boto3 = None
    dynamodb = None
    table = None
    HAS_BOTO3 = False


def put_item(item: Dict[str, Any]) -> None:
    """Store an item into the single table."""
    if HAS_BOTO3 and table is not None:
        table.put_item(Item=item)
    else:
        key = f"{item.get('PK')}_{item.get('SK')}"
        _local_mock_store[key] = item


def get_item(pk: str, sk: str) -> Optional[Dict[str, Any]]:
    """Retrieve an item by primary composite key."""
    if HAS_BOTO3 and table is not None:
        response = table.get_item(Key={"PK": pk, "SK": sk})
        return response.get("Item")
    key = f"{pk}_{sk}"
    return _local_mock_store.get(key)


def query_gsi1(gsi1pk: str, begins_with_sk: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Query items using GSI1 with optional sort key prefix."""
    if HAS_BOTO3 and table is not None:
        key_condition = boto3.dynamodb.conditions.Key("GSI1PK").eq(gsi1pk)
        if begins_with_sk:
            key_condition = key_condition & boto3.dynamodb.conditions.Key("GSI1SK").begins_with(begins_with_sk)

        response = table.query(
            IndexName="GSI1",
            KeyConditionExpression=key_condition,
            ScanIndexForward=False,
            Limit=limit
        )
        return response.get("Items", [])
    
    # Offline fallback matching
    results = []
    for item in _local_mock_store.values():
        if item.get("GSI1PK") == gsi1pk:
            if not begins_with_sk or str(item.get("GSI1SK", "")).startswith(begins_with_sk):
                results.append(item)
    return sorted(results, key=lambda x: str(x.get("GSI1SK", "")), reverse=True)[:limit]


def increment_atomic_counter(pk: str, sk: str, counter_attribute: str, increment_value: int = 1) -> None:
    """Update atomic counter in single table without read-then-write overhead."""
    if HAS_BOTO3 and table is not None:
        table.update_item(
            Key={"PK": pk, "SK": sk},
            UpdateExpression=f"ADD {counter_attribute} :val",
            ExpressionAttributeValues={":val": increment_value}
        )
    else:
        key = f"{pk}_{sk}"
        item = _local_mock_store.setdefault(key, {"PK": pk, "SK": sk, counter_attribute: 0})
        item[counter_attribute] = item.get(counter_attribute, 0) + increment_value

