# Contributing

1. Open an issue describing the source-record or registry change.
2. Update the JSON Schema, Python validation, tests, and contract documentation together.
3. Add only synthetic examples using reserved example domains.
4. Include negative tests for missing terms, expired approval, invalid URLs, prohibited purposes, and capacity limits.
5. Never change a source to `approved` without documented human review evidence.
6. Run:

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_source.py examples/approved-synthetic-source.json
python -m unittest discover -s tests -v
```

7. Explain security, privacy, legal/terms, and compatibility implications in the pull request.

Do not add collection clients or network access as incidental scope.
