import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from osint_source_registry.models import SourceRecord, validate_source_record

ROOT = Path(__file__).resolve().parents[1]


def load_example(name):
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


class SourceRecordTests(unittest.TestCase):

    def test_invalid_url_port_is_rejected(self):
        record = load_example("pending-synthetic-source.json")
        record["canonical_url"] = "https://example.org:invalid/"
        self.assertTrue(any("canonical_url" in error for error in validate_source_record(record)))

    def test_purpose_length_matches_schema(self):
        record = load_example("pending-synthetic-source.json")
        record["permitted_purposes"] = ["x" * 101]
        self.assertTrue(any("permitted_purposes" in error for error in validate_source_record(record)))

    def test_non_datetime_validation_clock_is_rejected(self):
        record = load_example("approved-synthetic-source.json")
        errors = validate_source_record(record, now="2026-11-02T00:00:00Z")
        self.assertTrue(any("validation clock" in error for error in errors))

    def test_approved_synthetic_record_matches_schema_and_model(self):
        record = load_example("approved-synthetic-source.json")
        schema = json.loads((ROOT / "schemas/source-record.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record)),
            [],
        )
        self.assertEqual(validate_source_record(record), [])
        parsed = SourceRecord.from_dict(record)
        self.assertEqual(parsed.source_id, "example.public-api")
        self.assertEqual(parsed.permitted_purposes, ("research", "verification"))

    def test_pending_source_is_valid_metadata_but_not_approved(self):
        record = load_example("pending-synthetic-source.json")
        self.assertEqual(validate_source_record(record), [])
        self.assertEqual(SourceRecord.from_dict(record).review_status, "pending")

    def test_plain_http_is_rejected(self):
        record = load_example("approved-synthetic-source.json")
        record["canonical_url"] = "http://api.example.org/"
        self.assertIn("canonical_url must be an HTTPS URL without embedded credentials", validate_source_record(record))

    def test_oversized_url_is_rejected(self):
        record = load_example("approved-synthetic-source.json")
        record["canonical_url"] = "https://example.org/" + ("x" * 2100)
        self.assertIn("canonical_url must be an HTTPS URL without embedded credentials", validate_source_record(record))

    def test_embedded_url_credentials_are_rejected(self):
        record = load_example("approved-synthetic-source.json")
        record["canonical_url"] = "https://user:secret@example.org/"
        self.assertIn("canonical_url must be an HTTPS URL without embedded credentials", validate_source_record(record))

    def test_approved_record_requires_terms_license_and_purpose(self):
        record = load_example("approved-synthetic-source.json")
        record["terms_url"] = None
        record["license_expression"] = None
        record["permitted_purposes"] = []
        errors = validate_source_record(record)
        self.assertTrue(any("requires a terms_url" in error for error in errors))
        self.assertTrue(any("requires a license_expression" in error for error in errors))
        self.assertTrue(any("requires at least one permitted purpose" in error for error in errors))

    def test_expired_approval_is_rejected(self):
        record = load_example("approved-synthetic-source.json")
        now = datetime(2027, 5, 1, tzinfo=timezone.utc)
        self.assertIn("approved source review has expired", validate_source_record(record, now=now))

    def test_future_review_timestamp_is_rejected(self):
        record = load_example("approved-synthetic-source.json")
        record["reviewed_at"] = "2027-01-01T00:00:00Z"
        errors = validate_source_record(record, now=datetime(2026, 11, 2, tzinfo=timezone.utc))
        self.assertIn("reviewed_at cannot be in the future", errors)

    def test_naive_timestamp_is_rejected(self):
        record = load_example("approved-synthetic-source.json")
        record["reviewed_at"] = "2026-10-01T12:00:00"
        self.assertTrue(any("reviewed_at" in error for error in validate_source_record(record)))

    def test_unknown_fields_are_rejected(self):
        record = load_example("pending-synthetic-source.json")
        record["fetch_url"] = "https://example.org/collect"
        self.assertTrue(any("unknown fields" in error for error in validate_source_record(record)))

    def test_non_string_enum_is_rejected_without_exception(self):
        record = load_example("pending-synthetic-source.json")
        record["source_type"] = []
        self.assertIn("source_type is not supported", validate_source_record(record))

    def test_rate_limit_is_bounded(self):
        record = load_example("pending-synthetic-source.json")
        record["declared_rate_limit_per_minute"] = 100001
        self.assertIn(
            "declared_rate_limit_per_minute must be null or an integer from 1 to 100000",
            validate_source_record(record),
        )


if __name__ == "__main__":
    unittest.main()
