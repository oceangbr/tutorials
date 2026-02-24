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

## Notes
- External sites sometimes block automated requests (403/429/999) or require a different TLS chain than this environment provides; these are reported separately as “blocked/unverifiable” or “TLS/SSL verification failures”.
- For a faster run, you can skip external checks:

```bash
python3 support_site_audit/audit.py --no-external
```

