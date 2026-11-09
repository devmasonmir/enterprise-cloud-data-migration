"""Synthetic-data medallion pipeline example (offline, not deployed)."""
import argparse
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be ISO 8601 text")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def amount_decimal(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError("invalid amount")
    try:
        value = Decimal(str(value))
        if not value.is_finite() or value < 0 or value != value.quantize(Decimal("0.01")):
            raise ValueError("amount must be finite, non-negative, with at most 2 decimal places")
    except InvalidOperation as exc:
        raise ValueError("invalid monetary amount") from exc
    return value


def medallion_batch(records):
    """Validate, quarantine, deduplicate in-batch, and aggregate customer orders."""
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    valid, errors = [], []
    for index, raw in enumerate(records):
        try:
            if not isinstance(raw, dict):
                raise ValueError("record must be an object")
            order_id, customer_id = raw.get("order_id"), raw.get("customer_id")
            if not isinstance(order_id, str) or not order_id.strip():
                raise ValueError("order_id required")
            if not isinstance(customer_id, str) or not customer_id.strip():
                raise ValueError("customer_id required")
            valid.append({
                "order_id": order_id.strip(),
                "customer_id": customer_id.strip(),
                "amount": amount_decimal(raw.get("amount")),
                "event_time": timestamp(raw.get("event_time")),
                "ingested_at": timestamp(raw.get("ingested_at")),
            })
        except (ValueError, TypeError) as exc:
            errors.append({"index": index, "reason": str(exc)})

    deduplicated = {}
    for record in valid:
        previous = deduplicated.get(record["order_id"])
        if previous is None or record["ingested_at"] >= previous["ingested_at"]:
            deduplicated[record["order_id"]] = record

    totals = {}
    for record in deduplicated.values():
        customer = totals.setdefault(record["customer_id"], {
            "count": 0, "amount": Decimal("0.00")
        })
        customer["count"] += 1
        customer["amount"] += record["amount"]

    return {
        "bronze_count": len(records),
        "valid_count": len(valid),
        "silver_count": len(deduplicated),
        "rejected": errors,
        "silver_orders": [
            {"order_id": rec["order_id"], "customer_id": rec["customer_id"],
             "amount": f'{rec["amount"]:.2f}'}
            for rec in sorted(deduplicated.values(), key=lambda item: item["order_id"])
        ],
        "gold_customer_orders": [
            {"customer_id": key, "order_count": val["count"],
             "total_amount": f'{val["amount"]:.2f}'}
            for key, val in sorted(totals.items())
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="Input JSON array (synthetic records only)")
    args = parser.parse_args()
    with open(args.json_file, encoding="utf-8") as handle:
        print(json.dumps(medallion_batch(json.load(handle)), indent=2))
