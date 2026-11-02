# Security Policy

## Scope

This repository stores source metadata and provides local validation and lookup. It does not fetch URLs, authenticate to providers, collect source content, or execute source-provided material.

## Reporting

Do not publish exploitable vulnerabilities, credentials, tokens, or private operational data in public issues. Use GitHub private vulnerability reporting or a private security advisory if enabled for this repository. A dedicated private reporting address is not published here; if private reporting is unavailable, the owner must configure an owner-approved private channel before production use.

## Security assumptions and limitations

- Source URLs, terms URLs, operators, licenses, jurisdiction, rate limits, and review claims are untrusted input.
- HTTPS validation checks syntax, host presence and port syntax only; it does not establish host safety, trustworthiness, reachability or operator control.
- The registry does not resolve DNS, make HTTP requests, follow redirects, or protect a future collector from SSRF.
- Review status is unsigned metadata and is not proof of reviewer identity or legal approval.
- Source records are copied into tuple-backed snapshots on insertion so caller-owned mutable lists cannot alter the catalog after validation.
- Registry capacity is bounded to at most 100,000 records and access is synchronized within one process.
- The in-memory registry is not durable or distributed.
- Do not store credentials, secrets, personal data, or collected source content.

Any future network collector requires a separate threat model, SSRF defenses, authentication, policy enforcement, rate limiting, audit provenance, and privacy/legal review.
