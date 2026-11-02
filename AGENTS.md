# Agent Instructions

- Treat the master registry as the authority for repository identity, role, dependencies, and maturity.
- This project is a source metadata catalog only. Do not add crawlers, scrapers, downloaders, API clients, enrichment, or collection automation without a separately reviewed design and explicit policy boundary.
- Never mark a source approved merely because its URL is reachable or publicly accessible.
- Do not invent source terms, licenses, jurisdictions, rate limits, or permissions. Unknown facts must remain unknown or pending review.
- Use synthetic reserved-domain examples only.
- Approval is time-bounded and must include a terms URL, license expression, permitted purposes, reviewer timestamp, and expiry.
- Keep dependencies declared until reproducible cross-repository tests prove interoperability.
- Do not store credentials, API keys, cookies, session tokens, personal datasets, or collected source content.
- Run the unit tests and source validator before proposing changes.
- Preserve fail-closed behavior: pending, suspended, rejected, retired, or expired sources must not appear in approved-source queries.
