"""Bounded in-memory index for reviewed source metadata; performs no I/O."""

from __future__ import annotations

from datetime import datetime, timezone
import threading

from .models import SourceRecord, validate_source_record


class SourceRegistry:
    def __init__(self, *, max_records: int = 1000) -> None:
        if isinstance(max_records, bool) or not isinstance(max_records, int) or not 1 <= max_records <= 100_000:
            raise ValueError("max_records must be an integer in [1, 100000]")
        self._max_records = max_records
        self._records: dict[str, SourceRecord] = {}
        self._lock = threading.RLock()

    def add(self, record: SourceRecord) -> None:
        if not isinstance(record, SourceRecord):
            raise TypeError("record must be a SourceRecord")
        errors = validate_source_record(record.to_dict())
        if errors:
            raise ValueError("; ".join(errors))
        with self._lock:
            if record.source_id in self._records:
                raise ValueError("duplicate source_id")
            if len(self._records) >= self._max_records:
                raise ValueError("source registry capacity reached")
            self._records[record.source_id] = record

    def get(self, source_id: str) -> SourceRecord | None:
        with self._lock:
            return self._records.get(source_id)

    def approved_sources(
        self,
        *,
        purpose: str | None = None,
        source_type: str | None = None,
        now: datetime | None = None,
    ) -> tuple[SourceRecord, ...]:
        if now is not None and not isinstance(now, datetime):
            raise ValueError("now must be a timezone-aware datetime")
        current = datetime.now(timezone.utc) if now is None else now
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        current = current.astimezone(timezone.utc)
        with self._lock:
            records = tuple(self._records.values())

        selected = []
        for record in records:
            if record.review_status != "approved":
                continue
            if purpose is not None:
                if purpose not in record.permitted_purposes or purpose in record.prohibited_purposes:
                    continue
            if source_type is not None and record.source_type != source_type:
                continue
            try:
                expiry = datetime.fromisoformat(record.review_expires_at.replace("Z", "+00:00"))
            except (AttributeError, ValueError):
                continue
            if expiry.tzinfo is None or expiry.astimezone(timezone.utc) <= current:
                continue
            selected.append(record)
        return tuple(sorted(selected, key=lambda item: item.source_id))

    def __len__(self) -> int:
        with self._lock:
            return len(self._records)
