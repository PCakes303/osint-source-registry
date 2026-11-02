# ADR 0001: Catalog-Only Boundary

- **Status:** Accepted for initial scaffold
- **Date:** 2026-11-02

## Context

The ecosystem needs a governed inventory of public information sources before implementing collection. Mixing source discovery metadata with collection execution would blur legal review, access authorization, and technical controls.

## Decision

The initial repository is a metadata catalog and local validation library only. It will not contain network clients, crawlers, scrapers, downloaders, API integrations, or enrichment. Source approvals are explicit, time-bounded metadata. Only approved and unexpired records are returned by the approved-source query.

Dependencies on Resource Manifest, Schema Registry, and Audit & Provenance remain declared until integration tests exist.

## Consequences

The scaffold is intentionally limited and cannot collect information. A later collector must be a separate reviewed component with authenticated policy decisions, SSRF protection, privacy controls, rate limits, retention, and audit events.
