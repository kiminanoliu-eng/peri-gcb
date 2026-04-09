#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取单个产品最容易出错的三类来源信息：
1. cn.peri.com 产品页中的项目案例
2. 官方 PERI PDF 候选
3. @perigroup 频道内的 YouTube 视频候选

用法:
  python3 extract_product_sources.py mxk-bracket-system
  python3 extract_product_sources.py mxk-bracket-system --save
"""

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import quote, urljoin

from http_helpers import http_get, http_head
from source_rules import (
    PDF_GENERIC_TOKENS,
    YOUTUBE_MAX_REVIEW_COUNT,
    YOUTUBE_MIN_REVIEW_COUNT,
    header_value,
    is_english_youtube_title,
    is_official_peri_youtube,
    is_verified_pdf_url,
    parse_content_disposition_filename,
    slug_keywords,
    slug_match_count,
    is_suitable_product_youtube,
    text_matches_slug,
)

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "source_reports"
REQUEST_TIMEOUT = 20
CN_URL_OVERRIDES = {
    "liwa": "https://cn.peri.com/products/liwa-%E9%92%A2%E6%A1%86%E6%A8%A1%E6%9D%BF.html",
}

REGION_PRODUCT_PAGES = [
    "https://cn.peri.com/products/{slug}.html",
    "https://www.peri.com/en/products/{slug}.html",
    "https://www.peri.ltd.uk/products/{slug}.html",
    "https://www.peri.de/produkte/{slug}.html",
    "https://www.peri.co.za/products/{slug}.html",
    "https://www.peri.be/en/products/{slug}.html"
]

SLUG_TRANSLATION_MAP = {
    "rundschalung": "circular-formwork",
    "saeulenrundschalung": "column-formwork",
    "saeulenschalung": "column-formwork"
}

def fetch_text(url):
    status_code, body, _ = http_get(url, timeout=REQUEST_TIMEOUT)
    return body if status_code == 200 else ""


def fetch_head_ok(url):
    status_code, headers = http_head(url, timeout=REQUEST_TIMEOUT)
    return status_code == 200, headers


def strip_tags(value):
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip(" ,")


def first_group(pattern, text, flags=re.S | re.I):
    match = re.search(pattern, text, flags)
    return strip_tags(match.group(1)) if match else ""


def load_products():
    with open(BASE_DIR / "products_v2.json", encoding="utf-8") as f:
        data = json.load(f)

    products = {}
    for category_name, category in data.items():
        if "subcategories" in category:
            for subcategory_name, subcategory in category["subcategories"].items():
                for item in subcategory["products"]:
                    products[item[0]] = {
                        "slug": item[0],
                        "name_zh": item[1],
                        "desc_zh": item[2],
                        "image": item[3],
                        "category": category_name,
                        "subcategory": subcategory_name
                    }
        else:
            for item in category.get("products", []):
                products[item[0]] = {
                    "slug": item[0],
                    "name_zh": item[1],
                    "desc_zh": item[2],
                    "image": item[3],
                    "category": category_name,
                    "subcategory": None
                }
    return products


def build_slug_variants(slug):
    parts = slug.split("-")
    variants = [slug]

    if parts[-1] in PDF_GENERIC_TOKENS and len(parts) > 1:
        variants.append("-".join(parts[:-1]))
    if len(parts) > 2 and parts[-2] in PDF_GENERIC_TOKENS:
        variants.append("-".join(parts[:-2]))

    compact = "-".join(part for part in parts if part not in PDF_GENERIC_TOKENS)
    if compact and compact != slug:
        variants.append(compact)

    if parts:
        variants.append(parts[0])

    translated = [SLUG_TRANSLATION_MAP.get(part, part) for part in parts]
    translated_slug = "-".join(translated)
    if translated_slug != slug:
        variants.append(translated_slug)

    seen = []
    for variant in variants:
        variant = variant.strip("-")
        if variant and variant not in seen:
            seen.append(variant)
    return seen


def load_pdf_overrides():
    path = BASE_DIR / "pdf_overrides.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_complete_json(slug):
    path = BASE_DIR / f"{slug}_complete.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_projects_from_product_page(product_html):
    projects = []
    blocks = re.findall(
        r'(<li class="project-teasers__item-regular-list.*?</li>)',
        product_html,
        re.S | re.I
    )

    for block in blocks:
        link = first_group(r'href="(https://cn\.peri\.com/projects/[^"]+\.html)"', block)
        if not link or "projects-overview" in link:
            continue

        teaser_location = first_group(r'project-teasers__item-regular-list-kicker">\s*(.*?)\s*</span>', block)
        teaser_headline = first_group(r'project-teasers__item-regular-list-headline">\s*(.*?)\s*</span>', block)
        teaser_desc = first_group(r'project-teasers__item-regular-list-description[^"]*">\s*(.*?)\s*</div>', block)
        teaser_image = first_group(r'<img[^>]+src="([^"]+)"', block)

        project_html = fetch_text(link)
        title = first_group(r"<title>(.*?)</title>", project_html)
        page_desc = first_group(r'<meta name="description" content="([^"]+)"', project_html)
        page_image = first_group(r'<meta property="og:image" content="([^"]+)"', project_html)

        country = ""
        if "，" in title:
            country = title.split("，", 1)[0].strip()
        elif "，" in teaser_headline:
            country = teaser_headline.split("，", 1)[0].strip()

        location = teaser_location
        if country and country not in location:
            location = f"{location}, {country}" if location else country

        projects.append({
            "name": title or teaser_headline,
            "location": location,
            "description": page_desc or teaser_desc,
            "image": page_image or teaser_image,
            "link": link
        })

    deduped = []
    seen_links = set()
    for project in projects:
        link = project["link"]
        if link not in seen_links:
            seen_links.add(link)
            deduped.append(project)
    return deduped


def add_pdf_candidate(candidates, seen_urls, url, source, slug, score, trusted_url=""):
    url = (url or "").strip()
    if not url:
        return
    if url in seen_urls:
        return

    ok, headers = fetch_head_ok(url)
    content_type = header_value(headers, "content-type")
    filename = parse_content_disposition_filename(headers)
    if not ok:
        return
    if "/.rest/downloads/" not in url and "pdf" not in content_type.lower():
        return
    if not is_verified_pdf_url(url, slug, headers=headers, trusted_url=trusted_url):
        return

    seen_urls.add(url)
    candidates.append({
        "url": url,
        "source": source,
        "score": score,
        "content_type": content_type,
        "filename": filename
    })


def extract_pdf_candidates(slug):
    candidates = []
    seen_urls = set()
    overrides = load_pdf_overrides()
    current_data = load_complete_json(slug)

    override_url = overrides.get(slug, "")
    if override_url:
        add_pdf_candidate(candidates, seen_urls, override_url, "override", slug, 100, trusted_url=override_url)

    current_pdf = (current_data.get("pdf_link") or "").strip()
    if current_pdf:
        add_pdf_candidate(candidates, seen_urls, current_pdf, "current_json", slug, 95, trusted_url=override_url)

    variants = build_slug_variants(slug)[:2]
    for variant in variants:
        for template in REGION_PRODUCT_PAGES:
            page_url = template.format(slug=variant)
            html_text = fetch_text(page_url)
            if not html_text:
                continue

            download_link = first_group(r'download-link="([^"]+)"', html_text)
            if download_link:
                add_pdf_candidate(candidates, seen_urls, html.unescape(download_link), page_url, slug, 85 if variant == slug else 75, trusted_url=override_url)

            absolute_pdfs = re.findall(r'https?://[^"\'>\s]+(?:\.pdf|/\.rest/downloads/[^"\'>\s]+)', html_text, re.I)
            relative_downloads = re.findall(r'(/\.rest/downloads/[^"\'>\s]+)', html_text, re.I)

            for found_url in absolute_pdfs:
                add_pdf_candidate(candidates, seen_urls, html.unescape(found_url), page_url, slug, 80 if variant == slug else 70, trusted_url=override_url)

            for found_path in relative_downloads:
                add_pdf_candidate(candidates, seen_urls, urljoin(page_url, html.unescape(found_path)), page_url, slug, 75 if variant == slug else 65, trusted_url=override_url)

    candidates.sort(key=lambda item: (-item["score"], item["url"]))
    return candidates


def build_youtube_queries(slug):
    keywords = slug_keywords(slug)
    full_slug_query = slug.replace("-", " ")
    compact_query = " ".join(keywords)

    queries = [
        full_slug_query,
        compact_query,
        keywords[0] if keywords else ""
    ]

    deduped = []
    for query in queries:
        query = re.sub(r"\s+", " ", query).strip()
        if query and query not in deduped:
            deduped.append(query)
    return deduped


def fetch_youtube_meta(video_id):
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    oembed_url = f"https://www.youtube.com/oembed?format=json&url={quote(watch_url, safe='')}"
    status_code, body, _ = http_get(oembed_url, timeout=REQUEST_TIMEOUT)
    if status_code != 200 or not body:
        return None
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return None
    return {
        "watch_url": watch_url,
        "title": (data.get("title") or "").strip(),
        "author_name": (data.get("author_name") or "").strip(),
        "author_url": (data.get("author_url") or "").strip(),
        "thumbnail_url": (data.get("thumbnail_url") or "").strip(),
        "is_official_channel": is_official_peri_youtube(
            author_name=data.get("author_name", ""),
            author_url=data.get("author_url", "")
        )
    }


def extract_youtube_candidates(slug):
    candidates = []
    seen_ids = set()
    keywords = slug_keywords(slug)

    for query in build_youtube_queries(slug):
        search_url = f"https://www.youtube.com/@perigroup/search?query={quote(query)}"
        search_html = fetch_text(search_url)
        video_ids = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', search_html)

        for video_id in video_ids:
            if video_id in seen_ids:
                continue
            seen_ids.add(video_id)

            meta = fetch_youtube_meta(video_id)
            if not meta:
                continue

            title_lower = meta["title"].lower()
            score = slug_match_count(meta["title"], slug)
            if meta["is_official_channel"]:
                score += 4
            if "(en)" in title_lower or "training" in title_lower:
                score += 1

            candidates.append({
                "video_id": video_id,
                "query": query,
                "search_url": search_url,
                "watch_url": meta["watch_url"],
                "title": meta["title"],
                "author_name": meta["author_name"],
                "author_url": meta["author_url"],
                "thumbnail_url": meta["thumbnail_url"],
                "is_official_channel": meta["is_official_channel"],
                "is_english": is_english_youtube_title(meta["title"]),
                "matches_product": is_suitable_product_youtube(
                    title=meta["title"],
                    slug=slug,
                    author_name=meta["author_name"],
                    author_url=meta["author_url"]
                ),
                "score": score
            })

            if len(candidates) >= YOUTUBE_MAX_REVIEW_COUNT:
                break
        if len(candidates) >= YOUTUBE_MAX_REVIEW_COUNT:
            break

    candidates.sort(key=lambda item: (-item["score"], item["video_id"]))
    return candidates


def choose_youtube_video(candidates, slug):
    reviewed = candidates[:YOUTUBE_MAX_REVIEW_COUNT]
    for candidate in reviewed:
        if is_suitable_product_youtube(
            title=candidate["title"],
            slug=slug,
            author_name=candidate["author_name"],
            author_url=candidate["author_url"]
        ):
            return {
                "attempted_candidates": len(reviewed),
                "selected_video_id": candidate["video_id"],
                "selected_watch_url": candidate["watch_url"],
                "reason": "Found a suitable official PERI English product video."
            }

    minimum_target = min(YOUTUBE_MIN_REVIEW_COUNT, YOUTUBE_MAX_REVIEW_COUNT)
    if len(reviewed) >= minimum_target:
        reason = f"No suitable official PERI English product video found in the first {len(reviewed)} candidates."
    else:
        reason = f"Only {len(reviewed)} official candidates were available, and none was a suitable English product video."

    return {
        "attempted_candidates": len(reviewed),
        "selected_video_id": "",
        "selected_watch_url": "",
        "reason": reason
    }


def build_report(slug):
    products = load_products()
    if slug not in products:
        raise SystemExit(f"未知 slug: {slug}")

    product = products[slug]
    cn_url = CN_URL_OVERRIDES.get(slug, f"https://cn.peri.com/products/{slug}.html")
    product_html = fetch_text(cn_url)
    product_title = first_group(r"<title>(.*?)</title>", product_html)
    product_desc = first_group(r'<meta name="description" content="([^"]+)"', product_html)
    product_image = first_group(r'<meta property="og:image" content="([^"]+)"', product_html)
    if not product_image:
        product_image = first_group(r'<meta name="thumbnail" content="([^"]+)"', product_html)

    youtube_candidates = extract_youtube_candidates(slug)

    return {
        "slug": slug,
        "name_zh": product["name_zh"],
        "category": product["category"],
        "subcategory": product["subcategory"],
        "cn_url": cn_url,
        "page_title": product_title,
        "page_description": product_desc,
        "page_image": product_image,
        "projects": extract_projects_from_product_page(product_html),
        "pdf_candidates": extract_pdf_candidates(slug),
        "youtube_candidates": youtube_candidates,
        "youtube_decision": choose_youtube_video(youtube_candidates, slug)
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="产品 slug")
    parser.add_argument("--save", action="store_true", help="将报告保存到 source_reports/")
    args = parser.parse_args()

    report = build_report(args.slug)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.save:
        REPORTS_DIR.mkdir(exist_ok=True)
        report_path = REPORTS_DIR / f"{args.slug}_sources.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✅ 已保存: {report_path}")


if __name__ == "__main__":
    main()
