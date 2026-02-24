#!/usr/bin/env python3
"""
Render a saved Beaufort12 audit JSON as a single HTML report.

This is useful if you want a shareable report without re-running the crawler.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
from typing import Any


def _esc(s: object) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def _as_int(v: Any) -> int | None:
    try:
        return int(v)
    except Exception:
        return None


def _linkify(url: str) -> str:
    u = _esc(url)
    return f'<a href="{u}" target="_blank" rel="noreferrer noopener">{u}</a>'


def _status_bad(status_code: int | None) -> bool:
    return status_code is None or status_code >= 400


def _render_sources(anchors_by_url: dict[str, list[dict[str, Any]]], url: str) -> str:
    srcs = anchors_by_url.get(url) or []
    if not srcs:
        return "<em>(source unknown)</em>"

    items = []
    for s in srcs:
        sp = _esc(s.get("source_page"))
        txt = _esc(s.get("anchor_text") or "")
        raw = s.get("raw_href")
        punct = s.get("suspicious_trailing_punct")
        meta = []
        if punct:
            meta.append(f"trailing-punct={_esc(punct)!r}".replace("&quot;", '"'))
        if raw and raw != url:
            meta.append(f"raw={_esc(raw)!r}".replace("&quot;", '"'))
        meta_s = f" <span class='muted'>({', '.join(meta)})</span>" if meta else ""
        text_s = f" — <span class='muted'>“{txt}”</span>" if txt else ""
        items.append(f"<li><a href=\"{sp}\" target=\"_blank\" rel=\"noreferrer noopener\">{sp}</a>{meta_s}{text_s}</li>")
    return "<ul class='sources'>" + "".join(items) + "</ul>"


def render_html_report(payload: dict[str, Any]) -> str:
    started_at = payload.get("started_at")
    pages = payload.get("pages") or []
    anchors_by_url: dict[str, list[dict[str, Any]]] = payload.get("anchors_by_url") or {}
    checks = payload.get("link_checks") or []
    term_findings = payload.get("term_findings") or []

    pages_ok = sum(1 for p in pages if _as_int(p.get("status_code")) == 200 and not p.get("error"))
    pages_total = len(pages)

    def is_internal(c: dict[str, Any]) -> bool:
        return bool(c.get("is_internal"))

    def status_code(c: dict[str, Any]) -> int | None:
        return _as_int(c.get("status_code"))

    def error_cat(c: dict[str, Any]) -> str | None:
        return c.get("error_category")

    broken_internal = [
        c
        for c in checks
        if is_internal(c) and (_status_bad(status_code(c)) or error_cat(c) in {"ssl_error", "timeout", "connection_error", "other_error"})
    ]
    missing_frags = [
        c
        for c in checks
        if is_internal(c) and c.get("fragment") and c.get("missing_fragment_target")
    ]
    http_to_https = [
        c for c in checks if is_internal(c) and c.get("redirects_http_to_https")
    ]

    broken_external = [
        c for c in checks if (not is_internal(c)) and error_cat(c) == "http_error"
    ]
    external_ssl = [
        c for c in checks if (not is_internal(c)) and error_cat(c) == "ssl_error"
    ]
    external_blocked = [
        c for c in checks if (not is_internal(c)) and error_cat(c) == "blocked"
    ]

    def render_check_card(c: dict[str, Any], extra: str = "") -> str:
        url = c.get("url") or ""
        st = status_code(c)
        err = c.get("error")
        final_url = c.get("final_url")

        parts = [
            "<div class='card'>",
            f"<div class='url'>{_linkify(url)}</div>",
            "<div class='meta'>",
            f"<span class='badge'>{_esc(st) if st is not None else 'ERROR'}</span>",
        ]
        if final_url and final_url != c.get("url_no_fragment"):
            parts.append(f"<span class='muted'>Final:</span> {_linkify(final_url)}")
        if err:
            parts.append(f"<span class='muted'>Error:</span> <code>{_esc(err)}</code>")
        if extra:
            parts.append(extra)
        parts.append("</div>")
        parts.append("<details><summary>Source pages</summary>")
        parts.append(_render_sources(anchors_by_url, url))
        parts.append("</details>")
        parts.append("</div>")
        return "\n".join(parts)

    def render_section(title: str, items: list[dict[str, Any]], empty_msg: str) -> str:
        if not items:
            return f"<h2>{_esc(title)}</h2><p class='muted'>{_esc(empty_msg)}</p>"
        body = "\n".join(render_check_card(i) for i in items)
        return f"<h2>{_esc(title)}</h2>\n{body}"

    html_parts: list[str] = []
    html_parts.append("<!doctype html>")
    html_parts.append("<html lang='en'>")
    html_parts.append("<head>")
    html_parts.append("<meta charset='utf-8'/>")
    html_parts.append("<meta name='viewport' content='width=device-width, initial-scale=1'/>")
    html_parts.append("<title>Beaufort12 Support Site Audit Report</title>")
    html_parts.append(
        "<style>"
        "body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.45;margin:24px;color:#111}"
        "h1{margin:0 0 8px 0} h2{margin-top:28px;border-top:1px solid #eee;padding-top:18px}"
        ".muted{color:#555} code{background:#f6f8fa;padding:2px 6px;border-radius:4px}"
        ".badge{display:inline-block;background:#111;color:#fff;border-radius:999px;padding:2px 10px;font-size:12px;margin-right:10px}"
        ".card{border:1px solid #e6e6e6;border-radius:10px;padding:14px 14px 10px 14px;margin:12px 0}"
        ".url{font-weight:600;margin-bottom:6px;word-break:break-all}"
        ".meta{display:flex;flex-wrap:wrap;gap:10px;align-items:center;font-size:14px}"
        "summary{cursor:pointer} details{margin-top:10px}"
        ".sources{margin:8px 0 0 18px} .sources li{margin:6px 0} a{color:#0b66c3;text-decoration:none} a:hover{text-decoration:underline}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}"
        ".stat{border:1px solid #eee;border-radius:10px;padding:10px}"
        ".stat .num{font-weight:700;font-size:20px}"
        "</style>"
    )
    html_parts.append("</head>")
    html_parts.append("<body>")
    html_parts.append("<h1>Beaufort12 Support Site Audit Report</h1>")
    html_parts.append(f"<p class='muted'>Started at (UTC): <strong>{_esc(started_at)}</strong></p>")

    html_parts.append("<div class='grid'>")
    stats = [
        ("Support pages audited", pages_total),
        ("Pages fetched successfully (HTTP 200)", pages_ok),
        ("Unique anchor links checked", len(checks)),
        ("Broken internal links", len(broken_internal)),
        ("Internal links missing #fragment targets", len(missing_frags)),
        ("Internal http→https redirects", len(http_to_https)),
        ("Broken external links (HTTP 4xx/5xx)", len(broken_external)),
        ("External links with TLS/SSL failures", len(external_ssl)),
        ("External links blocked/unverifiable", len(external_blocked)),
    ]
    for label, val in stats:
        html_parts.append(f"<div class='stat'><div class='num'>{_esc(val)}</div><div class='muted'>{_esc(label)}</div></div>")
    html_parts.append("</div>")

    html_parts.append(render_section("Broken internal links (beaufort12.com)", broken_internal, "None found."))

    # Fragment section: show clearer context
    if missing_frags:
        cards = []
        for c in missing_frags:
            frag = c.get("fragment")
            extra = f"<span class='muted'>Fragment:</span> <code>#{_esc(frag)}</code>"
            cards.append(render_check_card(c, extra=extra))
        html_parts.append("<h2>Internal links with missing fragment targets</h2>")
        html_parts.append("\n".join(cards))
    else:
        html_parts.append("<h2>Internal links with missing fragment targets</h2><p class='muted'>None found.</p>")

    html_parts.append(render_section("Broken external links (HTTP 4xx/5xx)", broken_external, "None found."))
    html_parts.append(render_section("External links with TLS/SSL verification failures", external_ssl, "None found."))
    html_parts.append(render_section("External links blocked / unverifiable automatically", external_blocked, "None found."))

    if http_to_https:
        html_parts.append("<h2>Internal http→https redirect inconsistencies (non-breaking)</h2>")
        html_parts.append("<div class='card'><ul class='sources'>")
        for c in http_to_https[:100]:
            u = c.get("url_no_fragment") or ""
            final = c.get("final_url") or ""
            html_parts.append(f"<li>{_linkify(u)} → {_linkify(final)}</li>")
        if len(http_to_https) > 100:
            html_parts.append(f"<li class='muted'>(and {len(http_to_https) - 100} more)</li>")
        html_parts.append("</ul></div>")

    if term_findings:
        html_parts.append("<h2>Potential text inconsistencies / typos (rule-based)</h2>")
        for f in term_findings:
            html_parts.append("<div class='card'>")
            html_parts.append(f"<div class='url'><code>{_esc(f.get('rule_id'))}</code> — {_linkify(f.get('page') or '')}</div>")
            html_parts.append("<div class='meta'>")
            html_parts.append(f"<span class='muted'>Match:</span> <code>{_esc(f.get('match'))}</code>")
            html_parts.append(f"<span class='muted'>Suggestion:</span> {_esc(f.get('suggestion'))}")
            html_parts.append("</div>")
            html_parts.append(f"<p><span class='muted'>Snippet:</span> “{_esc(f.get('snippet'))}”</p>")
            html_parts.append("</div>")
    else:
        html_parts.append("<h2>Potential text inconsistencies / typos (rule-based)</h2><p class='muted'>None found.</p>")

    html_parts.append("</body></html>")
    return "\n".join(html_parts)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audit_json", help="Path to the audit JSON output file")
    ap.add_argument(
        "--out",
        help="Output HTML path (default: alongside JSON, with .html extension)",
        default=None,
    )
    args = ap.parse_args(argv)

    with open(args.audit_json, "r", encoding="utf-8") as f:
        payload = json.load(f)

    out_path = args.out
    if not out_path:
        base, _ = os.path.splitext(args.audit_json)
        out_path = base + ".html"

    report = render_html_report(payload)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Wrote HTML report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

