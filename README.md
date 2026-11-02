# OSINT Source Registry

**Repository:** `PCakes303/osint-source-registry`  
**Maturity:** scaffolding  
**License:** [Scoped mixed-license policy](LICENSE.md).

## Purpose

Maintain a structured, review-gated catalog of public information sources, datasets, APIs, and publication repositories, including their access conditions, license/terms references, permitted purposes, collection limits, sensitivity, retention constraints, and review status.

This repository catalogs source metadata. It does not collect, crawl, download, query, enrich, or redistribute source content.

## Initial implementation

- Strict source-record JSON Schema.
- Typed source-record validation with HTTPS-only canonical and terms URLs.
- Explicit source review states and time-bounded approval.
- Bounded in-memory registry with deterministic results.
- Purpose- and source-type-filtered retrieval of approved, unexpired records.
- Synthetic examples only; no real source is pre-approved.
- Unit tests and Python 3.10–3.12 CI.

## Quick start

Requires Python 3.10+.

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_source.py examples/approved-synthetic-source.json
python -m unittest discover -s tests -v
```

## Trust and compliance boundary

A catalog entry is not legal advice, proof that a source is lawful to access, proof that terms permit a particular use, a guarantee of source accuracy, or authorization to collect data. Approval is a local review assertion and is not cryptographically signed or independently authenticated. Operators must review current terms, licensing, privacy, jurisdiction, robots/access rules, rate limits, and retention before use.

No collection or network client is included. Future collectors must enforce policy at execution time and emit provenance through the Audit & Provenance contract.
