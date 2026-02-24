#!/usr/bin/env python3
"""
Beaufort12 Support site audit

What it does:
- Pulls https://www.beaufort12.com/sitemap.xml
- Filters URLs containing "/support"
- Crawls each support page and extracts:
  - metadata (title, meta description, canonical, first h1)
  - anchor links with source context (raw href + normalized url + anchor text)
  - visible-ish text (for low-noise consistency checks)
- Validates:
  - internal links (HTTP status + fragment target presence)
  - external links (HTTP status, and categorizes SSL / blocked / error)
- Writes:
  - JSON results
  - Markdown report

No third-party parsing libraries are required (uses stdlib HTMLParser).
"""

from __future__ import annotations

import argparse
import dataclasses
import html
from html.parser import HTMLParser
import json
import re
import ssl
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse

import requests


USER_AGENT = "beaufort12-support-audit/1.0 (+https://www.beaufort12.com/support)"


def is_internal(netloc: str, internal_suffix: str) -> bool:
    # internal_suffix is "beaufort12.com"
    return netloc == internal_suffix or netloc.endswith("." + internal_suffix)


def should_ignore_href(href: str) -> bool:
    href = (href or "").strip()
    return (
        not href
        or href.startswith(("mailto:", "tel:", "javascript:"))
        or href == "#"
    )


def normalize_url(base_url: str, href: str) -> str | None:
    href = (href or "").strip()
    if should_ignore_href(href):
        return None
    if href.startswith("#"):
        return base_url + href
    return urljoin(base_url, href)


def strip_tags(s: str) -> str:
    # Very small tag stripper for metadata captures.
    s = re.sub(r"<script\b[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style\b[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def extract_visible_text(html_text: str) -> str:
    # Keep it simple: remove script/style, then strip tags.
    return strip_tags(html_text)


def extract_title(html_text: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", html_text, flags=re.I | re.S)
    return strip_tags(m.group(1)) if m else None


def extract_meta_description(html_text: str) -> str | None:
    m = re.search(
        r'<meta\s+[^>]*name=["\']description["\'][^>]*>',
        html_text,
        flags=re.I,
    )
    if not m:
        return None
    tag = m.group(0)
    m2 = re.search(r'content=["\']([^"\']*)["\']', tag, flags=re.I)
    return html.unescape(m2.group(1)).strip() if m2 else None


def extract_canonical(html_text: str) -> str | None:
    m = re.search(
        r'<link\s+[^>]*rel=["\']canonical["\'][^>]*>',
        html_text,
        flags=re.I,
    )
    if not m:
        return None
    tag = m.group(0)
    m2 = re.search(r'href=["\']([^"\']+)["\']', tag, flags=re.I)
    return html.unescape(m2.group(1)).strip() if m2 else None


def extract_first_h1(html_text: str) -> str | None:
    m = re.search(r"<h1\b[^>]*>(.*?)</h1>", html_text, flags=re.I | re.S)
    return strip_tags(m.group(1)) if m else None


def url_suspicious_punctuation(raw_href: str) -> str | None:
    raw_href = (raw_href or "").strip()
    if not raw_href:
        return None
    # Common authoring mistakes: punctuation accidentally included in href.
    m = re.search(r"[\)\]\.,;:]$", raw_href)
    return m.group(0) if m else None


class AnchorParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.anchors: list[Anchor] = []
        self._in_a = False
        self._current_href: str | None = None
        self._current_text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag.lower() != "a":
            return
        href = None
        for k, v in attrs:
            if k.lower() == "href":
                href = v
                break
        self._in_a = True
        self._current_href = href
        self._current_text_parts = []

    def handle_data(self, data: str):
        if self._in_a and data:
            self._current_text_parts.append(data)

    def handle_endtag(self, tag: str):
        if tag.lower() != "a":
            return
        raw_href = (self._current_href or "").strip()
        normalized = normalize_url(self.base_url, raw_href) if raw_href else None
        text = re.sub(r"\s+", " ", "".join(self._current_text_parts)).strip()
        if normalized:
            self.anchors.append(
                Anchor(
                    source_page=self.base_url,
                    raw_href=raw_href,
                    normalized_url=normalized,
                    anchor_text=text or None,
                    suspicious_trailing_punct=url_suspicious_punctuation(raw_href),
                )
            )
        self._in_a = False
        self._current_href = None
        self._current_text_parts = []


@dataclass(frozen=True)
class Anchor:
    source_page: str
    raw_href: str
    normalized_url: str
    anchor_text: str | None
    suspicious_trailing_punct: str | None


@dataclass
class PageResult:
    url: str
    status_code: int | None
    final_url: str | None
    error: str | None
    title: str | None
    meta_description: str | None
    canonical: str | None
    h1: str | None
    anchors: list[Anchor]
    visible_text: str


@dataclass
class LinkCheck:
    url: str
    url_no_fragment: str
    fragment: str | None
    is_internal: bool
    status_code: int | None
    final_url: str | None
    error_category: str | None  # http_error / ssl_error / blocked / timeout / connection_error / other_error
    error: str | None
    redirects_http_to_https: bool
    missing_fragment_target: bool


def fetch(session: requests.Session, url: str, timeout_s: int) -> tuple[int, str, str]:
    r = session.get(
        url,
        timeout=timeout_s,
        allow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    )
    return r.status_code, r.url, r.text


def parse_sitemap_support_pages(sitemap_url: str, include_substring: str) -> list[str]:
    xml_text = requests.get(
        sitemap_url,
        timeout=30,
        headers={"User-Agent": USER_AGENT},
    ).text
    root = ET.fromstring(xml_text)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [u.find("sm:loc", ns).text for u in root.findall("sm:url", ns)]
    urls = sorted({loc for loc in locs if loc and include_substring in loc})
    return urls


def crawl_pages(pages: list[str], timeout_s: int, max_workers: int) -> list[PageResult]:
    session = requests.Session()

    def crawl_one(url: str) -> PageResult:
        try:
            status, final_url, body = fetch(session, url, timeout_s=timeout_s)
            parser = AnchorParser(base_url=final_url)
            parser.feed(body)
            return PageResult(
                url=url,
                status_code=status,
                final_url=final_url,
                error=None,
                title=extract_title(body),
                meta_description=extract_meta_description(body),
                canonical=extract_canonical(body),
                h1=extract_first_h1(body),
                anchors=parser.anchors,
                visible_text=extract_visible_text(body),
            )
        except Exception as e:
            return PageResult(
                url=url,
                status_code=None,
                final_url=None,
                error=f"{type(e).__name__}: {e}",
                title=None,
                meta_description=None,
                canonical=None,
                h1=None,
                anchors=[],
                visible_text="",
            )

    results: list[PageResult] = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(crawl_one, u) for u in pages]
        for f in as_completed(futs):
            results.append(f.result())
    results.sort(key=lambda r: r.url)
    return results


def categorize_request_exception(e: Exception) -> str:
    # Keep categories stable for reporting.
    if isinstance(e, requests.exceptions.SSLError) or isinstance(e, ssl.SSLError):
        return "ssl_error"
    if isinstance(e, requests.exceptions.Timeout):
        return "timeout"
    if isinstance(e, requests.exceptions.ConnectionError):
        return "connection_error"
    return "other_error"


def check_links(
    urls: list[str],
    internal_suffix: str,
    timeout_s: int,
    max_workers: int,
    validate_fragments: bool,
) -> list[LinkCheck]:
    session = requests.Session()
    html_cache: dict[str, str] = {}  # url_no_fragment -> body

    def has_fragment_target(body: str, fragment: str) -> bool:
        # Conservative: accept id or name.
        frag = re.escape(fragment)
        return bool(
            re.search(rf'\bid=["\']{frag}["\']', body)
            or re.search(rf'\bname=["\']{frag}["\']', body)
        )

    def check_one(full_url: str) -> LinkCheck:
        url_no_frag, frag = urldefrag(full_url)
        parsed = urlparse(url_no_frag)
        internal = is_internal(parsed.netloc, internal_suffix)
        redirects_http_to_https = False
        missing_fragment_target = False

        try:
            r = session.get(
                url_no_frag,
                timeout=timeout_s,
                allow_redirects=True,
                headers={"User-Agent": USER_AGENT},
            )
            status_code = r.status_code
            final_url = r.url
            if urlparse(url_no_frag).scheme == "http" and urlparse(final_url).scheme == "https":
                redirects_http_to_https = True

            error_category = None
            error = None
            if status_code in (403, 429, 999):
                error_category = "blocked"
                error = f"HTTP {status_code}"
            elif status_code >= 400:
                error_category = "http_error"
                error = f"HTTP {status_code}"

            if validate_fragments and internal and frag:
                body = html_cache.get(final_url)
                if body is None:
                    body = r.text
                    html_cache[final_url] = body
                if not has_fragment_target(body, frag):
                    missing_fragment_target = True

            return LinkCheck(
                url=full_url,
                url_no_fragment=url_no_frag,
                fragment=frag or None,
                is_internal=internal,
                status_code=status_code,
                final_url=final_url,
                error_category=error_category,
                error=error,
                redirects_http_to_https=redirects_http_to_https,
                missing_fragment_target=missing_fragment_target,
            )
        except Exception as e:
            cat = categorize_request_exception(e)
            return LinkCheck(
                url=full_url,
                url_no_fragment=url_no_frag,
                fragment=frag or None,
                is_internal=internal,
                status_code=None,
                final_url=None,
                error_category=cat,
                error=f"{type(e).__name__}: {e}",
                redirects_http_to_https=False,
                missing_fragment_target=False,
            )

    checks: list[LinkCheck] = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(check_one, u) for u in urls]
        for f in as_completed(futs):
            checks.append(f.result())
    checks.sort(key=lambda c: c.url)
    return checks


def term_consistency_findings(pages: list[PageResult], per_rule_limit: int = 10) -> list[dict[str, Any]]:
    # Keep these rules minimal/high-confidence to avoid noisy “grammar check” output.
    rules = [
        {
            "id": "sales_force",
            "pattern": re.compile(r"\bSales\s+force\b", re.I),
            "suggestion": "Use “Salesforce”.",
        },
        {
            "id": "app_exchange",
            "pattern": re.compile(r"\bApp\s+Exchange\b", re.I),
            "suggestion": "Use “AppExchange”.",
        },
        {
            "id": "mail_chimp",
            "pattern": re.compile(r"\bMail\s+Chimp\b", re.I),
            "suggestion": "Use “Mailchimp”.",
        },
        {
            "id": "premuim_typo",
            "pattern": re.compile(r"\bpremuim\b", re.I),
            "suggestion": "Typo: “premuim” → “premium”.",
        },
        {
            "id": "segement_typo",
            "pattern": re.compile(r"\bsegement\b", re.I),
            "suggestion": "Typo: “segement” → “segment”.",
        },
        {
            "id": "duplicate_word",
            "pattern": re.compile(r"\b(the|a|an|to|of)\s+\1\b", re.I),
            "suggestion": "Remove duplicated word (e.g., “the the”).",
        },
        {
            "id": "space_before_punct",
            "pattern": re.compile(r"\b\w+\s+[\.,;:!?]"),
            "suggestion": "Remove the extra space before punctuation.",
        },
        {
            "id": "double_space",
            "pattern": re.compile(r"[A-Za-z][ ]{2,}[A-Za-z]"),
            "suggestion": "Reduce double spaces.",
        },
    ]

    findings: list[dict[str, Any]] = []
    counts: dict[str, int] = {r["id"]: 0 for r in rules}

    for page in pages:
        text = page.visible_text
        if not text:
            continue
        for rule in rules:
            if counts[rule["id"]] >= per_rule_limit:
                continue
            for m in rule["pattern"].finditer(text):
                if counts[rule["id"]] >= per_rule_limit:
                    break
                start = max(0, m.start() - 60)
                end = min(len(text), m.end() + 60)
                snippet = text[start:end].strip()
                findings.append(
                    {
                        "rule_id": rule["id"],
                        "page": page.final_url or page.url,
                        "match": m.group(0),
                        "snippet": snippet,
                        "suggestion": rule["suggestion"],
                    }
                )
                counts[rule["id"]] += 1

    return findings


def group_sources(anchors: list[Anchor]) -> dict[str, list[dict[str, Any]]]:
    # normalized_url -> list of {source_page, raw_href, anchor_text}
    out: dict[str, list[dict[str, Any]]] = {}
    for a in anchors:
        out.setdefault(a.normalized_url, []).append(
            {
                "source_page": a.source_page,
                "raw_href": a.raw_href,
                "anchor_text": a.anchor_text,
                "suspicious_trailing_punct": a.suspicious_trailing_punct,
            }
        )
    return out


def render_report(
    *,
    started_at: str,
    pages: list[PageResult],
    anchor_sources: dict[str, list[dict[str, Any]]],
    checks: list[LinkCheck],
    term_findings: list[dict[str, Any]],
) -> str:
    pages_ok = sum(1 for p in pages if p.status_code == 200 and not p.error)
    pages_err = len(pages) - pages_ok

    broken_internal = [
        c
        for c in checks
        if c.is_internal and (c.error_category in {"http_error", "connection_error", "timeout", "other_error", "ssl_error"} or c.status_code is None or (c.status_code and c.status_code >= 400))
    ]
    broken_external = [
        c
        for c in checks
        if not c.is_internal and c.error_category == "http_error"
    ]
    external_ssl = [c for c in checks if not c.is_internal and c.error_category == "ssl_error"]
    external_blocked = [c for c in checks if not c.is_internal and c.error_category == "blocked"]

    missing_frags = [c for c in checks if c.is_internal and c.fragment and c.missing_fragment_target]
    http_to_https = [c for c in checks if c.is_internal and c.redirects_http_to_https]

    lines: list[str] = []
    lines.append(f"# Beaufort12 Support Site Audit Report")
    lines.append("")
    lines.append(f"- Started at (UTC): **{started_at}**")
    lines.append(f"- Support pages audited: **{len(pages)}**")
    lines.append(f"- Pages fetched successfully (HTTP 200): **{pages_ok}**")
    if pages_err:
        lines.append(f"- Pages with fetch errors / non-200: **{pages_err}**")
    lines.append("")
    lines.append("## Summary (links)")
    lines.append("")
    lines.append(f"- Unique anchor links checked: **{len(checks)}**")
    lines.append(f"- Broken internal links: **{len(broken_internal)}**")
    lines.append(f"- Internal links with missing `#fragment` targets: **{len(missing_frags)}**")
    lines.append(f"- Internal links redirecting http→https (inconsistency): **{len(http_to_https)}**")
    lines.append(f"- Broken external links (HTTP 4xx/5xx): **{len(broken_external)}**")
    lines.append(f"- External links with TLS/SSL verification failures: **{len(external_ssl)}**")
    lines.append(f"- External links blocked/unverifiable automatically: **{len(external_blocked)}**")
    lines.append("")

    def fmt_sources(u: str, max_sources: int = 3) -> str:
        srcs = anchor_sources.get(u, [])
        if not srcs:
            return "_(source unknown)_"
        shown = srcs[:max_sources]
        remainder = len(srcs) - len(shown)
        parts = []
        for s in shown:
            txt = s.get("anchor_text") or ""
            raw = s.get("raw_href")
            punct = s.get("suspicious_trailing_punct")
            extra = []
            if punct:
                extra.append(f"trailing-punct={punct!r}")
            if raw and raw != u:
                extra.append(f"raw={raw!r}")
            extra_s = f" ({', '.join(extra)})" if extra else ""
            parts.append(f"- {s['source_page']}{extra_s}" + (f" — “{txt}”" if txt else ""))
        out = "\n".join(parts)
        if remainder > 0:
            out += f"\n- _(and {remainder} more source page(s))_"
        return out

    if broken_internal:
        lines.append("## Broken internal links (beaufort12.com)")
        lines.append("")
        for c in broken_internal:
            lines.append(f"### {c.url}")
            lines.append("")
            lines.append(f"- Status: **{c.status_code if c.status_code is not None else 'ERROR'}**")
            if c.final_url and c.final_url != c.url_no_fragment:
                lines.append(f"- Final URL after redirects: `{c.final_url}`")
            if c.error:
                lines.append(f"- Error: `{c.error}`")
            lines.append("")
            lines.append("Source pages:")
            lines.append(fmt_sources(c.url))
            lines.append("")

    if missing_frags:
        lines.append("## Internal links with missing fragment targets")
        lines.append("")
        for c in missing_frags:
            lines.append(f"- `{c.url}` (fragment `#{c.fragment}` not found on `{c.final_url or c.url_no_fragment}`)")
            lines.append("  Source pages:")
            lines.append("  " + fmt_sources(c.url).replace("\n", "\n  "))
        lines.append("")

    if broken_external:
        lines.append("## Broken external links (HTTP 4xx/5xx)")
        lines.append("")
        for c in broken_external:
            lines.append(f"- `{c.url}` → **{c.status_code}**")
            lines.append("  Source pages:")
            lines.append("  " + fmt_sources(c.url).replace("\n", "\n  "))
        lines.append("")

    if external_ssl:
        lines.append("## External links with TLS/SSL verification failures")
        lines.append("")
        lines.append("_These could be real certificate/chain issues or an environment CA-chain limitation; verify in a normal browser._")
        lines.append("")
        for c in external_ssl:
            lines.append(f"- `{c.url}` → **TLS/SSL verification failed**")
            if c.error:
                lines.append(f"  - Error: `{c.error}`")
            lines.append("  Source pages:")
            lines.append("  " + fmt_sources(c.url).replace("\n", "\n  "))
        lines.append("")

    if external_blocked:
        lines.append("## External links blocked / unverifiable automatically")
        lines.append("")
        lines.append("_These returned 403/429/999 (bot protection/rate limiting). They may still work for human users._")
        lines.append("")
        for c in external_blocked:
            lines.append(f"- `{c.url}` → **{c.status_code}**")
            lines.append("  Source pages:")
            lines.append("  " + fmt_sources(c.url).replace("\n", "\n  "))
        lines.append("")

    if http_to_https:
        lines.append("## Internal http→https redirect inconsistencies (non-breaking)")
        lines.append("")
        # dedupe to keep report small
        shown = http_to_https[:30]
        for c in shown:
            lines.append(f"- `{c.url_no_fragment}` → `{c.final_url}`")
        if len(http_to_https) > len(shown):
            lines.append(f"- _(and {len(http_to_https) - len(shown)} more)_")
        lines.append("")

    if term_findings:
        lines.append("## Potential text inconsistencies / typos (rule-based)")
        lines.append("")
        for f in term_findings:
            lines.append(f"- **{f['rule_id']}** on {f['page']}")
            lines.append(f"  - Match: `{f['match']}`")
            lines.append(f"  - Suggestion: {f['suggestion']}")
            lines.append(f"  - Snippet: “{f['snippet']}”")
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://www.beaufort12.com")
    ap.add_argument("--sitemap-path", default="/sitemap.xml")
    ap.add_argument("--include", default="/support")
    ap.add_argument("--out-dir", default="support_site_audit_reports")
    ap.add_argument("--timeout-s", type=int, default=20)
    ap.add_argument("--crawl-workers", type=int, default=12)
    ap.add_argument("--link-workers", type=int, default=20)
    ap.add_argument("--no-external", action="store_true", help="Skip external link checks")
    args = ap.parse_args(argv)

    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sitemap_url = args.base.rstrip("/") + args.sitemap_path
    internal_suffix = urlparse(args.base).netloc.split(":")[0]
    if internal_suffix.startswith("www."):
        internal_suffix = internal_suffix[len("www.") :]

    pages = parse_sitemap_support_pages(sitemap_url, include_substring=args.include)
    page_results = crawl_pages(pages, timeout_s=args.timeout_s, max_workers=args.crawl_workers)

    all_anchors: list[Anchor] = []
    for p in page_results:
        all_anchors.extend(p.anchors)
    anchor_sources = group_sources(all_anchors)

    unique_urls = sorted(anchor_sources.keys())
    internal_urls = [u for u in unique_urls if is_internal(urlparse(urldefrag(u)[0]).netloc, internal_suffix)]
    external_urls = [u for u in unique_urls if u not in set(internal_urls)]

    internal_checks = check_links(
        internal_urls,
        internal_suffix=internal_suffix,
        timeout_s=args.timeout_s,
        max_workers=args.link_workers,
        validate_fragments=True,
    )
    external_checks: list[LinkCheck] = []
    if not args.no_external and external_urls:
        external_checks = check_links(
            external_urls,
            internal_suffix=internal_suffix,
            timeout_s=args.timeout_s,
            max_workers=args.link_workers,
            validate_fragments=False,
        )
    checks = sorted(internal_checks + external_checks, key=lambda c: c.url)

    term_findings = term_consistency_findings(page_results, per_rule_limit=10)

    # Keep the JSON output reasonably sized: `visible_text` is used to compute
    # `term_findings` but is not typically useful in the exported report.
    pages_payload: list[dict[str, Any]] = []
    for p in page_results:
        d = dataclasses.asdict(p)
        d.pop("visible_text", None)
        pages_payload.append(d)

    payload = {
        "started_at": started_at,
        "config": {
            "base": args.base,
            "sitemap_url": sitemap_url,
            "include": args.include,
            "timeout_s": args.timeout_s,
            "crawl_workers": args.crawl_workers,
            "link_workers": args.link_workers,
            "no_external": args.no_external,
        },
        "pages": pages_payload,
        "anchors_by_url": anchor_sources,
        "link_checks": [dataclasses.asdict(c) for c in checks],
        "term_findings": term_findings,
    }

    out_dir = args.out_dir
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = f"{out_dir}/beaufort12_support_audit_{ts}.json"
    report_path = f"{out_dir}/beaufort12_support_audit_{ts}.md"

    # Create output directory (without using external tools).
    import os

    os.makedirs(out_dir, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=False, ensure_ascii=False)

    report = render_report(
        started_at=started_at,
        pages=page_results,
        anchor_sources=anchor_sources,
        checks=checks,
        term_findings=term_findings,
    )
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

