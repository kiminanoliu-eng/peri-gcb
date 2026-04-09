#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from urllib.parse import unquote, urlparse

PDF_GENERIC_TOKENS = {
    "peri", "up", "scaffold", "safety",
    "system", "systems", "formwork", "scaffolding", "wall", "column", "slab",
    "panel", "frame", "girder", "protection", "service", "services",
    "engineering", "construction", "kit", "kits", "platform", "platforms",
    "props", "accessories", "software", "planner", "tracker", "working",
    "table", "tables", "lifting", "fork", "digital", "solutions", "solution",
    "easy", "flex", "modular", "modularized", "and", "the"
}

PERI_YOUTUBE_CHANNEL_ID = "UCGYlSSGN81EdoPvY4QUzLDQ"
PERI_YOUTUBE_AUTHOR_NAME = "PERI Group"
PERI_YOUTUBE_AUTHOR_URL = "https://www.youtube.com/@perigroup"
YOUTUBE_MIN_REVIEW_COUNT = 5
YOUTUBE_MAX_REVIEW_COUNT = 14

TOKEN_SYNONYMS = {
    "anker": ["anchor"],
    "anchor": ["anker"]
}


def header_value(headers, name):
    if not headers:
        return ""
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return ""


def is_official_peri_host(hostname):
    return "peri." in (hostname or "").lower()


def slug_keywords(slug):
    tokens = []
    for token in re.split(r"[^a-z0-9]+", (slug or "").lower()):
        if not token or token in PDF_GENERIC_TOKENS:
            continue
        if len(token) < 2 and not token.isdigit():
            continue
        tokens.append(token)
    return tokens


def normalize_text(value):
    return unquote((value or "").lower())


def keyword_variants(keyword):
    variants = [keyword]
    for synonym in TOKEN_SYNONYMS.get(keyword, []):
        if synonym not in variants:
            variants.append(synonym)
    return variants


def slug_match_count(value, slug):
    normalized = normalize_text(value)
    keywords = slug_keywords(slug)
    count = 0
    for keyword in keywords:
        if any(variant in normalized for variant in keyword_variants(keyword)):
            count += 1
    return count


def text_matches_slug(value, slug):
    return slug_match_count(value, slug) > 0


def parse_content_disposition_filename(headers):
    content_disposition = header_value(headers, "content-disposition")
    if not content_disposition:
        return ""

    match = re.search(r"filename\*=UTF-8''([^;]+)", content_disposition, re.I)
    if match:
        return unquote(match.group(1).strip().strip('"'))

    match = re.search(r'filename="?([^";]+)"?', content_disposition, re.I)
    if match:
        return unquote(match.group(1).strip())

    return ""


def is_direct_pdf_like(url):
    path = normalize_text(urlparse(url).path or "")
    return path.endswith(".pdf") or "/.rest/downloads/" in path


def pdf_matches_slug(url, slug, headers=None):
    parsed = urlparse(url)
    normalized = normalize_text((parsed.path or "") + " " + (parsed.query or ""))
    if text_matches_slug(normalized, slug):
        return True

    filename = parse_content_disposition_filename(headers)
    if filename and text_matches_slug(filename, slug):
        return True

    return False


def is_verified_pdf_url(url, slug, headers=None, trusted_url=""):
    if not isinstance(url, str):
        return False

    url = url.strip()
    if not url:
        return False

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if not is_official_peri_host(parsed.netloc):
        return False
    if not is_direct_pdf_like(url):
        return False
    if trusted_url and url == trusted_url:
        return True
    return pdf_matches_slug(url, slug, headers=headers)


def is_official_peri_youtube(author_name="", author_url="", body=""):
    author_name = (author_name or "").strip().lower()
    author_url = (author_url or "").strip().lower()
    body = (body or "").lower()
    return (
        author_name == PERI_YOUTUBE_AUTHOR_NAME.lower() or
        author_url == PERI_YOUTUBE_AUTHOR_URL.lower() or
        author_url.endswith("/@perigroup") or
        PERI_YOUTUBE_CHANNEL_ID.lower() in body
    )


def is_english_youtube_title(title):
    title = (title or "").lower()
    return (
        "(en)" in title or
        "(english)" in title or
        re.search(r"\benglish\b", title) is not None
    )


def is_suitable_product_youtube(title, slug, author_name="", author_url="", body=""):
    keywords = slug_keywords(slug)
    required_match_count = 1 if len(keywords) <= 1 else min(2, len(keywords))
    return (
        is_official_peri_youtube(author_name=author_name, author_url=author_url, body=body) and
        slug_match_count(title, slug) >= required_match_count and
        is_english_youtube_title(title)
    )
