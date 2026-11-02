# Security Policy

## Scope

This repository stores source metadata and provides local validation and lookup. It does not fetch URLs, authenticate to providers, collect source content, or execute source-provided material.

## Reporting

Report vulnerabilities privately through GitHub Security Advisories for this repository when enabled, or contact the repository owner through the GitHub profile.

## Security assumptions and limitations

- Source URLs, terms URLs, operators, licenses, jurisdiction, and review claims are untrusted input.
- HTTPS syntax validation does not establish that a host is safe, trustworthy, reachable, or controlled by the named operator.
- The registry does not resolve DNS, make HTTP requests, follow redirects, or protect a future collector from SSRF.
- Review status is unsigned metadata and is not proof of reviewer identity or legal approval.
- The in-memory registry is process-local and is not durable or distributed.
- Do not store credentials, secrets, personal data, or collected source content.

Any future network collector requires a separate threat model, SSRF defenses, authentication, policy enforcement, rate limiting, audit provenance, and privacy/legal review.
