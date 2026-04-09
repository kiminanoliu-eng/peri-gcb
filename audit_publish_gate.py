#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from urllib.parse import unquote, urlparse

from extract_product_sources import load_products
from verify_product import verify_product

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "source_reports"


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def load_product_index_meta():
    with open(BASE_DIR / "products_v2.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    product_meta = {}
    for category_name, category in data.items():
        if "subcategories" in category:
            for subcategory_name, subcategory in category["subcategories"].items():
                for item in subcategory["products"]:
                    product_meta[item[0]] = {
                        "category_slug": category["slug"],
                        "subcategory_slug": subcategory["slug"],
                        "listing_image": item[3],
                    }
        else:
            for item in category.get("products", []):
                product_meta[item[0]] = {
                    "category_slug": category["slug"],
                    "subcategory_slug": None,
                    "listing_image": item[3],
                }
    return product_meta


def audit_slug(slug, products_meta):
    errors = []
    warnings = []

    complete_path = BASE_DIR / f"{slug}_complete.json"
    report_path = REPORTS_DIR / f"{slug}_sources.json"
    html_path = BASE_DIR / "products" / f"{slug}.html"
    search_path = BASE_DIR / "search.html"

    if not complete_path.exists():
        return {"errors": [f"缺少完整JSON: {complete_path.name}"], "warnings": []}
    if not report_path.exists():
        return {"errors": [f"缺少源报告: {report_path.name}"], "warnings": []}
    if not html_path.exists():
        return {"errors": [f"缺少HTML页面: products/{slug}.html"], "warnings": []}

    data = read_json(complete_path)
    report = read_json(report_path)
    html = html_path.read_text(encoding="utf-8")
    search_html = search_path.read_text(encoding="utf-8") if search_path.exists() else ""

    # Reuse the live validator as the baseline gate.
    verify_errors, verify_warnings = verify_product(slug)
    errors.extend(verify_errors)
    warnings.extend(verify_warnings)

    # Projects must match the source report exactly by link.
    report_projects = report.get("projects") or []
    data_projects = data.get("projects") or []
    report_links = [item["link"] for item in report_projects]
    data_links = [item["link"] for item in data_projects]
    if report_links != data_links:
        errors.append("项目案例与源报告不一致")

    # PDF selection must match the top audited source candidate, or be empty when none exists.
    pdf_candidates = report.get("pdf_candidates") or []
    pdf_link = data.get("pdf_link") or ""
    if pdf_candidates:
        expected_pdf = pdf_candidates[0]["url"]
        if pdf_link != expected_pdf:
            errors.append(f"PDF链接与源报告首选候选不一致: {pdf_link} != {expected_pdf}")
    elif pdf_link:
        errors.append("JSON含有PDF，但源报告没有PDF候选")

    # YouTube selection must match the source decision exactly.
    youtube_decision = report.get("youtube_decision") or {}
    selected_video_id = youtube_decision.get("selected_video_id", "")
    youtube_video_id = data.get("youtube_video_id") or ""
    if youtube_video_id != selected_video_id:
        errors.append(f"YouTube视频与源报告决策不一致: {youtube_video_id} != {selected_video_id}")

    # Product hero image must be present in the product page.
    hero_image = data.get("image") or data.get("thumbnail") or ""
    if hero_image and not html_contains_url(html, hero_image):
        errors.append("产品页未渲染JSON中的主图")

    # Listing/search image gate: either the canonical listing image or the complete JSON image must appear.
    meta = products_meta.get(slug)
    if meta:
        listing_page_name = meta["subcategory_slug"] or meta["category_slug"]
        listing_page_path = BASE_DIR / "categories" / f"{listing_page_name}.html"
        if listing_page_path.exists():
            listing_html = listing_page_path.read_text(encoding="utf-8")
            if f"products/{slug}.html" not in listing_html:
                errors.append("分类页缺少该产品入口")
            expected_images = [value for value in {meta.get("listing_image", ""), hero_image} if value]
            if expected_images and not any(html_contains_url(listing_html, value) for value in expected_images):
                errors.append("分类页中的索引图缺失或不匹配")
        else:
            errors.append(f"缺少分类页: {listing_page_path.name}")

        if search_html:
            if slug not in search_html:
                errors.append("搜索页缺少该产品索引")
            expected_images = [value for value in {meta.get("listing_image", ""), hero_image} if value]
            if expected_images and not any(html_contains_url(search_html, value) for value in expected_images):
                errors.append("搜索页中的索引图缺失或不匹配")

    return {"errors": errors, "warnings": warnings}


def audit_products(slugs=None):
    products = load_products()
    products_meta = load_product_index_meta()
    target_slugs = slugs or list(products.keys())

    results = {}
    for slug in target_slugs:
        complete_path = BASE_DIR / f"{slug}_complete.json"
        if not complete_path.exists():
            results[slug] = {"errors": [f"缺少完整JSON: {complete_path.name}"], "warnings": []}
            continue
        results[slug] = audit_slug(slug, products_meta)
    return results


def main():
    products = load_products()
    results = audit_products(list(products.keys()))
    blocking = {slug: result for slug, result in results.items() if result["errors"]}
    print(json.dumps({"blocking": blocking, "results": results}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if blocking else 0)


if __name__ == "__main__":
    main()
