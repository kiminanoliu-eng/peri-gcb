#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

from extract_product_sources import BASE_DIR, load_products
from verify_product import verify_product


AUDIT_PATH = BASE_DIR / "audit_report.json"


def utc_now_iso():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def normalize_url(url):
    if not url:
        return ""
    url = str(url).replace("&amp;", "&").strip()
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}{unquote(parsed.path)}"
    return unquote(url)


def html_contains_url(html, url):
    normalized = normalize_url(url)
    if not normalized:
        return False
    return normalized in normalize_url(html)


def main():
    products = load_products()
    search_html = (BASE_DIR / "search.html").read_text(encoding="utf-8") if (BASE_DIR / "search.html").exists() else ""

    report = {
        "started_at": utc_now_iso(),
        "checked": [],
        "errors": {},
        "warnings": {},
    }

    total_errors = 0
    total_warnings = 0

    for slug, product in products.items():
        json_path = BASE_DIR / f"{slug}_complete.json"
        if not json_path.exists():
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        errors, warnings = verify_product(slug)
        html_path = BASE_DIR / "products" / f"{slug}.html"
        html_content = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
        image_url = data.get("image") or data.get("thumbnail") or product.get("image") or ""

        if image_url and not html_contains_url(html_content, image_url):
            errors.append(f"产品主图未在HTML中找到: {image_url}")

        if slug not in search_html:
            errors.append(f"search.html 未包含 slug: {slug}")

        report["checked"].append(slug)
        if errors:
            report["errors"][slug] = errors
            total_errors += len(errors)
        if warnings:
            report["warnings"][slug] = warnings
            total_warnings += len(warnings)

        AUDIT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    report["finished_at"] = utc_now_iso()
    report["total_checked"] = len(report["checked"])
    report["total_errors"] = total_errors
    report["total_warnings"] = total_warnings
    AUDIT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Checked {report['total_checked']} products")
    print(f"Errors: {total_errors}")
    print(f"Warnings: {total_warnings}")

    if total_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
