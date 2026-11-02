import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from osint_source_registry import SourceRecord, SourceRegistry

ROOT = Path(__file__).resolve().parents[1]


def load_record(name):
    value = json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))
    return SourceRecord.from_dict(value)


class SourceRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = SourceRegistry(max_records=3)
        self.approved = load_record("approved-synthetic-source.json")
        self.pending = load_record("pending-synthetic-source.json")

    def test_approved_sources_are_returned_in_deterministic_order(self):
        second = self.approved.to_dict()
        second["source_id"] = "example.z-public-api"
        self.registry.add(SourceRecord.from_dict(second))
        self.registry.add(self.approved)
        self.assertEqual(
            [item.source_id for item in self.registry.approved_sources()],
            ["example.public-api", "example.z-public-api"],
        )

    def test_pending_sources_are_not_returned_by_approved_query(self):
        self.registry.add(self.pending)
        self.assertEqual(self.registry.approved_sources(), ())
        self.assertIsNotNone(self.registry.get(self.pending.source_id))

    def test_purpose_filter_is_exact_and_fail_closed(self):
        self.registry.add(self.approved)
        self.assertEqual(len(self.registry.approved_sources(purpose="research")), 1)
        self.assertEqual(self.registry.approved_sources(purpose="credential harvesting"), ())

    def test_source_type_filter_is_exact(self):
        self.registry.add(self.approved)
        self.assertEqual(len(self.registry.approved_sources(source_type="public_api")), 1)
        self.assertEqual(self.registry.approved_sources(source_type="website"), ())

    def test_expired_approval_is_not_returned(self):
        self.registry.add(self.approved)
        future = datetime(2027, 5, 1, tzinfo=timezone.utc)
        self.assertEqual(self.registry.approved_sources(now=future), ())

    def test_duplicate_source_id_is_rejected(self):
        self.registry.add(self.approved)
        with self.assertRaisesRegex(ValueError, "duplicate source_id"):
            self.registry.add(self.approved)

    def test_capacity_is_enforced(self):
        self.registry.add(self.approved)
        self.registry.add(self.pending)
        second = self.approved.to_dict()
        second["source_id"] = "example.second-api"
        self.registry.add(SourceRecord.from_dict(second))
        third = self.approved.to_dict()
        third["source_id"] = "example.third-api"
        with self.assertRaisesRegex(ValueError, "capacity reached"):
            self.registry.add(SourceRecord.from_dict(third))

    def test_invalid_capacity_is_rejected(self):
        for value in (0, -1, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                SourceRegistry(max_records=value)

    def test_naive_query_clock_is_rejected(self):
        self.registry.add(self.approved)
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            self.registry.approved_sources(now=datetime(2026, 11, 2))


if __name__ == "__main__":
    unittest.main()
