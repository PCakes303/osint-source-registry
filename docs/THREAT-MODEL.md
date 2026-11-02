# Threat Model

## Assets

- Source metadata and review decisions.
- Terms, license, jurisdiction, access and retention constraints.
- Integrity of the approved-source view.
- Downstream systems that may consume source records.

## Trust boundaries

All record fields are untrusted input, including operator names, URLs, terms references, license expressions, review notes, and review status. Public accessibility does not imply permission to access or reuse content.

## Threats and controls in this scaffold

| Threat | Current control | Residual risk |
|---|---|---|
| Malformed or ambiguous records | Strict schema and model validation | Schema correctness does not establish factual accuracy |
| Plain HTTP or malformed source URLs | HTTPS URL syntax required | No DNS, host ownership, redirect, or SSRF validation; no network requests occur |
| Expired approval reused | Approved-only query checks expiry | Approval is unsigned and reviewer identity is not authenticated |
| Unknown or unreviewed source treated as approved | Pending/non-approved records excluded from approved query | Downstream consumers must preserve this gate |
| Registry exhaustion | Bounded in-memory record capacity | Process-local memory only; no durable store |
| Misleading license/terms claims | Required terms and license for approved state | No automated legal interpretation or external verification |
| Personal or sensitive data exposure | Sensitivity and retention metadata; no content collection | Metadata may be inaccurate; downstream collector needs independent privacy controls |

## Explicit non-goals

This project does not crawl, scrape, download, query APIs, resolve DNS, follow redirects, inspect robots.txt, authenticate providers, interpret legal terms, verify source operators, or collect personal data.

## Requirements before any collector integration

- Separate reviewed design and threat model.
- SSRF defenses including DNS rebinding and redirect handling.
- Per-source and global rate limits, backoff, and circuit breakers.
- Authentication and authorization through the ecosystem identity/policy boundaries.
- Privacy review, minimization, retention and deletion controls.
- Auditable approval and collection events through Audit & Provenance.
- Human review of current terms, licenses, jurisdiction, and permitted purposes.
