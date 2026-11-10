"""Unit tests for the offline lakehouse reference implementation."""
import unittest
from lakehouse import medallion_batch


def row(order_id="o1", customer_id="c1", amount="1.00",
        ingested_at="2026-01-01T00:00:00Z",
        event_time="2026-01-01T00:00:00Z"):
    return dict(order_id=order_id, customer_id=customer_id, amount=amount,
                ingested_at=ingested_at, event_time=event_time)


class MedallionTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(medallion_batch([])["gold_customer_orders"], [])

    def test_decimal_aggregate(self):
        output = medallion_batch([row("a", amount="0.10"),
                                  row("b", amount="0.20")])
        self.assertEqual(output["gold_customer_orders"][0]["total_amount"], "0.30")

    def test_latest_ingestion_wins(self):
        output = medallion_batch([
            row("a", amount="4.00", ingested_at="2026-01-01T00:00:00Z"),
            row("a", amount="9.00", ingested_at="2026-01-02T00:00:00Z"),
            row("a", amount="3.00", ingested_at="2025-12-30T00:00:00Z"),
        ])
        self.assertEqual(output["silver_count"], 1)
        self.assertEqual(output["gold_customer_orders"][0]["total_amount"], "9.00")

    def test_conflicting_ingestion_tie_is_quarantined(self):
        output = medallion_batch([
            row("a", amount="4.00", ingested_at="2026-01-01T00:00:00Z"),
            row("a", amount="9.00", ingested_at="2026-01-01T00:00:00Z"),
        ])

        self.assertEqual(output["silver_count"], 1)
        self.assertEqual(output["gold_customer_orders"][0]["total_amount"], "4.00")
        self.assertEqual(output["rejected"], [{
            "index": 1,
            "reason": "conflicting duplicate order_id at identical ingested_at",
        }])

    def test_exact_ingestion_tie_is_idempotent(self):
        duplicate = row("a", amount="4.00")

        output = medallion_batch([duplicate, dict(duplicate)])

        self.assertEqual(output["valid_count"], 2)
        self.assertEqual(output["silver_count"], 1)
        self.assertEqual(output["rejected"], [])

    def test_rejects_bad_records_without_losing_good_ones(self):
        output = medallion_batch([None, row(), row("b", amount="NaN"),
                                  row("c", customer_id="")])
        self.assertEqual(output["silver_count"], 1)
        self.assertEqual([item["index"] for item in output["rejected"]], [0, 2, 3])

    def test_rejects_naive_timestamp(self):
        output = medallion_batch([row(event_time="2026-01-01T00:00:00")])
        self.assertEqual(output["valid_count"], 0)

    def test_rejects_boolean_and_excess_precision(self):
        output = medallion_batch([row("a", amount=True), row("b", amount="3.999")])
        self.assertEqual(len(output["rejected"]), 2)

    def test_requires_list(self):
        with self.assertRaises(TypeError):
            medallion_batch({"foo": "bar"})

    def test_identifier_normalization(self):
        output = medallion_batch([row(" o1 ", " c1 ")])
        self.assertEqual(output["silver_orders"][0]["order_id"], "o1")
        self.assertEqual(output["gold_customer_orders"][0]["customer_id"], "c1")


if __name__ == "__main__":
    unittest.main()
