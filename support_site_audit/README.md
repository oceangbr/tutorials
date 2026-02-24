# Beaufort12 support-site audit

This folder contains a small, dependency-light crawler to audit the Beaufort12 support site for:
- broken links (internal + external)
- common link inconsistencies (trailing punctuation in `href`, http→https redirects, missing `#fragment` targets)
- a small set of high-confidence text consistency / typo checks

## Run

From the repo root:

```bash
python3 support_site_audit/audit.py
```

Outputs are written to `./support_site_audit_reports/`:
- `beaufort12_support_audit_<timestamp>.md` (human report)
- `beaufort12_support_audit_<timestamp>.json` (machine-readable raw results)

## Render an HTML report (from an existing JSON)

If you already have a saved audit JSON and want a shareable HTML report without re-running the crawl:

```bash
python3 support_site_audit/render_html.py support_site_audit_report/beaufort12_support_audit_*.json
```

This will write an `.html` file alongside the JSON.

## Notes
- External sites sometimes block automated requests (403/429/999) or require a different TLS chain than this environment provides; these are reported separately as “blocked/unverifiable” or “TLS/SSL verification failures”.
- For a faster run, you can skip external checks:

```bash
python3 support_site_audit/audit.py --no-external
```

