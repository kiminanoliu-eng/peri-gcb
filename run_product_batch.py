#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
import subprocess
import traceback
from datetime import UTC, date, datetime
from pathlib import Path

from audit_publish_gate import audit_products
from extract_product_sources import (
    BASE_DIR,
    REPORTS_DIR,
    build_slug_variants,
    build_report,
    fetch_text,
    first_group,
    load_products,
)
from translate_products import translate_description
from verify_product import verify_product


STATUS_PATH = BASE_DIR / "batch_status.json"
TODAY = date.today().isoformat()


def utc_now_iso():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")

ENGLISH_PAGE_TEMPLATES = [
    "https://www.peri.com/en/products/{slug}.html",
    "https://www.peri.ltd.uk/products/{slug}.html",
    "https://www.peri.co.za/products/{slug}.html",
    "https://www.peri.be/en/products/{slug}.html",
    "https://www.peri.com.au/products/{slug}.html",
]

GERMAN_PAGE_TEMPLATES = [
    "https://www.peri.de/produkte/{slug}.html",
]


def contains_cjk(value):
    return bool(re.search(r"[\u4e00-\u9fff]", value or ""))


def load_pending_slugs():
    products = load_products()
    complete = {
        path.name[:-14]
        for path in BASE_DIR.glob("*_complete.json")
    }
    return [slug for slug in products if slug not in complete]


def fetch_first_meta_description(slug, templates):
    for variant in build_slug_variants(slug):
        for template in templates:
            url = template.format(slug=variant)
            html = fetch_text(url)
            if not html:
                continue
            description = first_group(r'<meta name="description" content="([^"]+)"', html)
            if description:
                return description, url
    return "", ""


def build_description_bundle(slug, product, report):
    base_zh = (product.get("desc_zh") or "").strip()
    zh_desc = (report.get("page_description") or base_zh).strip()
    translations = translate_description(base_zh)

    en_desc, en_source = fetch_first_meta_description(slug, ENGLISH_PAGE_TEMPLATES)
    de_desc, de_source = fetch_first_meta_description(slug, GERMAN_PAGE_TEMPLATES)

    description = {
        "zh": zh_desc or base_zh,
        "en": (translations.get("en") or "").strip(),
        "es": (translations.get("es") or "").strip(),
        "de": (translations.get("de") or "").strip(),
        "pt": (translations.get("pt") or "").strip(),
        "sr": (translations.get("sr") or "").strip(),
        "hu": (translations.get("hu") or "").strip(),
    }

    if not description["en"] or contains_cjk(description["en"]):
        description["en"] = en_desc or zh_desc or base_zh

    if not description["de"] or contains_cjk(description["de"]):
        description["de"] = de_desc or description["en"]

    for lang in ("es", "pt", "sr", "hu"):
        if not description[lang] or contains_cjk(description[lang]):
            description[lang] = description["en"]

    return description, {
        "en_source": en_source,
        "de_source": de_source,
    }


def build_complete_payload(slug, product, report):
    description, desc_sources = build_description_bundle(slug, product, report)
    pdf_candidates = report.get("pdf_candidates") or []
    youtube_decision = report.get("youtube_decision") or {}

    return {
        "slug": slug,
        "name_zh": product["name_zh"],
        "category": product["category"],
        "subcategory": product["subcategory"],
        "cn_url": report["cn_url"],
        "image": product.get("image") or report.get("page_image") or "",
        "thumbnail": product.get("image") or report.get("page_image") or "",
        "description": description,
        "projects": report.get("projects") or [],
        "pdf_link": pdf_candidates[0]["url"] if pdf_candidates else "",
        "youtube_video_id": youtube_decision.get("selected_video_id", ""),
        "verified": True,
        "verification_date": TODAY,
        "sources": {
            "cn_url": report["cn_url"],
            "pdf_source": pdf_candidates[0]["source"] if pdf_candidates else "",
            "youtube_reason": youtube_decision.get("reason", ""),
            "description_sources": desc_sources,
        },
    }


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def save_status(status):
    write_json(STATUS_PATH, status)


def run_command(args, cwd=BASE_DIR):
    result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(args)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result.stdout


def publish_changes(processed_slugs, commit_message):
    run_command(["git", "add", "-A"])
    run_command(["git", "commit", "-m", commit_message])
    run_command(["git", "push"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="只处理前 N 个待处理产品")
    parser.add_argument("--publish", action="store_true", help="处理完成并验证通过后自动提交发布")
    parser.add_argument(
        "--audit-scope",
        choices=["none", "processed", "all"],
        default="processed",
        help="发布前门禁范围：none=关闭，processed=仅本次处理产品，all=全站",
    )
    args = parser.parse_args()

    products = load_products()
    pending = load_pending_slugs()
    if args.limit > 0:
        pending = pending[:args.limit]

    status = {
        "started_at": utc_now_iso(),
        "mode": "publish" if args.publish else "local",
        "audit_scope": args.audit_scope,
        "pending_queue": pending,
        "processed": [],
        "failed": [],
        "validation_errors": {},
        "audit_errors": {},
    }
    save_status(status)

    if not pending:
        status["finished_at"] = utc_now_iso()
        save_status(status)
        print("没有待处理产品。")
        return

    for index, slug in enumerate(pending, 1):
        try:
            product = products[slug]
            report = build_report(slug)
            REPORTS_DIR.mkdir(exist_ok=True)
            write_json(REPORTS_DIR / f"{slug}_sources.json", report)

            payload = build_complete_payload(slug, product, report)
            write_json(BASE_DIR / f"{slug}_complete.json", payload)

            status["processed"].append({
                "slug": slug,
                "index": index,
                "projects": len(payload["projects"]),
                "has_pdf": bool(payload["pdf_link"]),
                "has_youtube": bool(payload["youtube_video_id"]),
            })
            status["current_slug"] = slug
            save_status(status)
            print(f"[{index}/{len(pending)}] 已生成 {slug}")
        except Exception as exc:
            status["failed"].append({
                "slug": slug,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            })
            save_status(status)
            print(f"[{index}/{len(pending)}] 失败 {slug}: {exc}")

    run_command(["python3", "add_pdf_links.py"])
    run_command(["python3", "rebuild_site_v2.py"])

    for item in status["processed"]:
        slug = item["slug"]
        errors, warnings = verify_product(slug)
        if errors:
            status["validation_errors"][slug] = {
                "errors": errors,
                "warnings": warnings,
            }
        save_status(status)

    remaining_pending = load_pending_slugs()
    processed_slugs = [item["slug"] for item in status["processed"]]
    status["remaining_pending"] = remaining_pending
    if args.publish and not status["failed"] and not status["validation_errors"] and not remaining_pending:
        if args.audit_scope == "all":
            audit_slugs = list(products.keys())
        elif args.audit_scope == "processed":
            audit_slugs = processed_slugs
        else:
            audit_slugs = []

        full_results = audit_products(audit_slugs) if audit_slugs else {}
        status["audit_errors"] = {
            slug: result for slug, result in full_results.items() if result["errors"]
        }
        status["audit_checked_slugs"] = audit_slugs
    else:
        status["audit_errors"] = {}
        status["audit_checked_slugs"] = []
    save_status(status)

    status["finished_at"] = utc_now_iso()
    save_status(status)

    if args.publish:
        if status["failed"] or status["validation_errors"] or status["audit_errors"] or status.get("remaining_pending"):
            raise SystemExit("批处理存在失败或验证错误，未自动发布。")
        commit_message = f"Batch process {len(status['processed'])} products"
        publish_changes([item["slug"] for item in status["processed"]], commit_message)
        status["published_at"] = utc_now_iso()
        save_status(status)
        print("✅ 批处理完成并已发布。")
    else:
        print("✅ 批处理完成（本地模式）。")


if __name__ == "__main__":
    main()
