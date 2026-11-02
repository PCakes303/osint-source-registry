# Source Record Contract — v0.1.0

## Purpose

A source record describes a public information source and the constraints that a future, separately authorized collector would need to consider. It is a metadata record, not a command to access the source.

## Required identity and location fields

- `source_id`: stable, lowercase catalog identifier.
- `name` and `operator`: human-readable labels; these are assertions, not verified identities.
- `source_type`: website, public API, dataset, publication, document repository, or public registry.
- `canonical_url`: HTTPS URL syntax for the source's canonical entrypoint.
- `jurisdiction`: jurisdictional scope or explicit unknown value.

## Access, legal and operational constraints

- `access_method` and `access_auth` describe the declared access model. No credentials are stored.
- `terms_url` and `license_expression` reference terms and licensing information. The registry does not interpret them or decide whether a use is lawful.
- `robots_policy`, `collection_constraints`, and `declared_rate_limit_per_minute` record constraints for a future reviewed collector. Collection-constraint items are 3–500 characters; permitted/prohibited purpose items are 2–100 characters, with at most 20 entries per list.
- `data_sensitivity` and `retention_days` provide conservative handling metadata.
- `permitted_purposes` and `prohibited_purposes` are explicit policy labels; they are not enforcement by themselves.

## Review lifecycle

States are `pending`, `approved`, `suspended`, `rejected`, and `retired`.

An approved record must include:
1. HTTPS terms URL;
2. non-empty license expression;
3. at least one permitted purpose;
4. timezone-aware `reviewed_at` and `review_expires_at`;
5. expiry later than review time.

The local registry is bounded to at most 100,000 records, synchronizes access within one process, and stores a validated snapshot of tuple-backed list fields. It only returns approved records whose review has not expired. Pending and other non-approved states remain stored as metadata but are excluded from approved-source queries. Expired approvals fail closed.

The review status is not cryptographically authenticated. A future governance service must bind approval to an authenticated reviewer and an audit-provenance event.

## Versioning and compatibility

This schema is experimental v0.1.0. Unknown fields are rejected. Breaking changes require a major version; backward-compatible optional additions may use a minor version. Cross-repository dependencies remain declared until tested with reproducible fixtures.
