"""Source record model and fail-closed metadata validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping
from urllib.parse import urlsplit

SOURCE_TYPES = {
    "website", "public_api", "dataset", "publication",
    "document_repository", "public_registry",
}
ACCESS_METHODS = {"public_web", "public_api", "downloadable_dataset", "manual_review"}
ACCESS_AUTH = {"none", "api_key_required", "oauth_required", "account_required", "unknown"}
SENSITIVITY = {"public", "personal_data_possible", "sensitive_personal_data", "unknown"}
ROBOTS_POLICIES = {"respect", "manual_review_required", "not_applicable", "unknown"}
REVIEW_STATES = {"pending", "approved", "suspended", "rejected", "retired"}

REQUIRED = {
    "source_id", "name", "source_type", "operator", "canonical_url",
    "jurisdiction", "access_method", "access_auth", "data_sensitivity",
    "robots_policy", "collection_constraints", "permitted_purposes",
    "prohibited_purposes", "declared_rate_limit_per_minute",
    "retention_days", "review_status",
}
ALLOWED = REQUIRED | {
    "terms_url", "license_expression", "reviewed_at",
    "review_expires_at", "review_notes",
}


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _valid_https_url(value: Any) -> bool:
    if not isinstance(value, str) or not value or len(value) > 2048 or any(ch.isspace() for ch in value):
        return False
    try:
        parts = urlsplit(value)
        parts.port  # Access validates malformed and out-of-range port syntax.
        return (
            parts.scheme == "https"
            and bool(parts.hostname)
            and parts.username is None
            and parts.password is None
        )
    except ValueError:
        return False


def validate_source_record(
    record: Mapping[str, Any], *, now: datetime | None = None
) -> list[str]:
    """Return validation errors; approval invariants are deliberately fail-closed."""
    errors: list[str] = []
    if not isinstance(record, Mapping):
        return ["record must be an object"]

    missing = REQUIRED - set(record)
    unknown = set(record) - ALLOWED
    if missing:
        errors.append(f"missing required fields: {', '.join(sorted(missing))}")
    if unknown:
        errors.append(f"unknown fields: {', '.join(sorted(unknown))}")
    if missing or unknown:
        return errors

    if not isinstance(record["source_id"], str) or not (
        3 <= len(record["source_id"]) <= 100
    ):
        errors.append("source_id must contain 3 to 100 characters")
    elif record["source_id"][0] not in "abcdefghijklmnopqrstuvwxyz0123456789" or any(
        ch not in "abcdefghijklmnopqrstuvwxyz0123456789._-" for ch in record["source_id"]
    ):
        errors.append("source_id must use lowercase letters, digits, dot, underscore or hyphen")

    for field, maximum in (("name", 200), ("operator", 200), ("jurisdiction", 120)):
        value = record[field]
        if not isinstance(value, str) or not (2 <= len(value) <= maximum):
            errors.append(f"{field} must contain 2 to {maximum} characters")

    if not isinstance(record["source_type"], str) or record["source_type"] not in SOURCE_TYPES:
        errors.append("source_type is not supported")
    if not _valid_https_url(record["canonical_url"]):
        errors.append("canonical_url must be an HTTPS URL without embedded credentials")
    if not isinstance(record["access_method"], str) or record["access_method"] not in ACCESS_METHODS:
        errors.append("access_method is not supported")
    if not isinstance(record["access_auth"], str) or record["access_auth"] not in ACCESS_AUTH:
        errors.append("access_auth is not supported")
    if not isinstance(record["data_sensitivity"], str) or record["data_sensitivity"] not in SENSITIVITY:
        errors.append("data_sensitivity is not supported")
    if not isinstance(record["robots_policy"], str) or record["robots_policy"] not in ROBOTS_POLICIES:
        errors.append("robots_policy is not supported")
    if not isinstance(record["review_status"], str) or record["review_status"] not in REVIEW_STATES:
        errors.append("review_status is not supported")

    for field, min_item_length, max_item_length in (("collection_constraints", 3, 500), ("permitted_purposes", 2, 100), ("prohibited_purposes", 2, 100)):
        value = record[field]
        if not isinstance(value, (list, tuple)) or len(value) > 20:
            errors.append(f"{field} must be a list with at most 20 items")
        elif any(not isinstance(item, str) or len(item) < min_item_length or len(item) > max_item_length for item in value):
            errors.append(f"{field} contains an invalid item (maximum {max_item_length} characters)")

    rate = record["declared_rate_limit_per_minute"]
    if rate is not None and (isinstance(rate, bool) or not isinstance(rate, int) or not 1 <= rate <= 100000):
        errors.append("declared_rate_limit_per_minute must be null or an integer from 1 to 100000")
    retention = record["retention_days"]
    if retention is not None and (isinstance(retention, bool) or not isinstance(retention, int) or not 1 <= retention <= 36500):
        errors.append("retention_days must be null or an integer from 1 to 36500")

    terms = record.get("terms_url")
    if terms is not None and not _valid_https_url(terms):
        errors.append("terms_url must be null or an HTTPS URL without embedded credentials")
    license_expression = record.get("license_expression")
    if license_expression is not None and (
        not isinstance(license_expression, str) or len(license_expression) > 120
    ):
        errors.append("license_expression must be null or a string of at most 120 characters")

    if record["review_status"] == "approved":
        if not isinstance(terms, str) or not terms:
            errors.append("approved source requires a terms_url")
        if not isinstance(license_expression, str) or not license_expression.strip():
            errors.append("approved source requires a license_expression")
        if not record["permitted_purposes"]:
            errors.append("approved source requires at least one permitted purpose")
        reviewed = _parse_time(record.get("reviewed_at"))
        expires = _parse_time(record.get("review_expires_at"))
        if reviewed is None:
            errors.append("approved source requires timezone-aware reviewed_at")
        if expires is None:
            errors.append("approved source requires timezone-aware review_expires_at")
        if reviewed is not None and expires is not None and expires <= reviewed:
            errors.append("review_expires_at must be later than reviewed_at")
        if now is None:
            current = datetime.now(timezone.utc)
        elif not isinstance(now, datetime):
            errors.append("validation clock must be a timezone-aware datetime")
            current = datetime.now(timezone.utc)
        else:
            current = now
        if current.tzinfo is None or current.utcoffset() is None:
            errors.append("validation clock must be timezone-aware")
        elif reviewed is not None and reviewed > current.astimezone(timezone.utc):
            errors.append("reviewed_at cannot be in the future")
        elif expires is not None and expires <= current.astimezone(timezone.utc):
            errors.append("approved source review has expired")

    notes = record.get("review_notes", "")
    if not isinstance(notes, str) or len(notes) > 1000:
        errors.append("review_notes must be a string of at most 1000 characters")
    for optional_time in ("reviewed_at", "review_expires_at"):
        value = record.get(optional_time)
        if value is not None and _parse_time(value) is None:
            errors.append(f"{optional_time} must be a timezone-aware ISO-8601 timestamp")

    return errors


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    name: str
    source_type: str
    operator: str
    canonical_url: str
    jurisdiction: str
    access_method: str
    access_auth: str
    data_sensitivity: str
    robots_policy: str
    collection_constraints: tuple[str, ...]
    permitted_purposes: tuple[str, ...]
    prohibited_purposes: tuple[str, ...]
    declared_rate_limit_per_minute: int | None
    retention_days: int | None
    review_status: str
    terms_url: str | None = None
    license_expression: str | None = None
    reviewed_at: str | None = None
    review_expires_at: str | None = None
    review_notes: str = ""

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SourceRecord":
        errors = validate_source_record(value)
        if errors:
            raise ValueError("; ".join(errors))
        data = dict(value)
        for field in ("collection_constraints", "permitted_purposes", "prohibited_purposes"):
            data[field] = tuple(data[field])
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        result = dict(self.__dict__)
        for field in ("collection_constraints", "permitted_purposes", "prohibited_purposes"):
            result[field] = list(result[field])
        return result
