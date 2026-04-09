#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
产品数据验证脚本
用于验证产品JSON文件和生成的HTML的完整性和正确性
"""

import json
import os
import sys
import re
from pathlib import Path
from urllib.parse import quote
from source_rules import (
    header_value,
    is_official_peri_youtube,
    is_verified_pdf_url,
    slug_keywords,
    slug_match_count,
    text_matches_slug,
)

from http_helpers import http_get, http_head

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "source_reports"


def load_trusted_pdf_links():
    trusted = {}
    for filename in ("product_pdf_links.json", "pdf_overrides.json"):
        path = BASE_DIR / filename
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as f:
            trusted.update(json.load(f))
    return trusted


TRUSTED_PDF_LINKS = load_trusted_pdf_links()


def load_source_report(slug):
    path = REPORTS_DIR / f"{slug}_sources.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def same_url(left, right):
    return (left or "").replace("&amp;", "&").strip() == (right or "").replace("&amp;", "&").strip()

def verify_product(slug):
    """验证产品数据的完整性和正确性"""

    print(f"\n{'='*60}")
    print(f"开始验证产品: {slug}")
    print(f"{'='*60}\n")

    errors = []
    warnings = []

    # 1. 验证文件名
    expected_filename = f"{slug}_complete.json"
    if not os.path.exists(expected_filename):
        errors.append(f"文件不存在: {expected_filename}")
        print(f"❌ 文件不存在: {expected_filename}")
        return errors, warnings

    print(f"✅ 文件名正确: {expected_filename}")

    # 2. 读取JSON
    try:
        with open(expected_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        errors.append(f"JSON解析失败: {e}")
        print(f"❌ JSON解析失败: {e}")
        return errors, warnings

    print(f"✅ JSON格式正确")
    source_report = load_source_report(slug)

    # 3. 验证必需字段
    required_fields = [
        'slug', 'name_zh', 'category', 'description', 'projects',
        'pdf_link', 'youtube_video_id'
    ]

    for field in required_fields:
        if field not in data:
            errors.append(f"缺少必需字段: {field}")
            print(f"❌ 缺少字段: {field}")
        else:
            print(f"✅ 字段存在: {field}")

    # 4. 验证slug匹配
    if data.get('slug') != slug:
        errors.append(f"slug不匹配 - 期望: {slug}, 实际: {data.get('slug')}")
        print(f"❌ slug不匹配 - 期望: {slug}, 实际: {data.get('slug')}")
    else:
        print(f"✅ slug匹配: {slug}")

    # 5. 验证7种语言翻译
    description = data.get('description', {})
    required_languages = ['zh', 'en', 'es', 'de', 'pt', 'sr', 'hu']

    print(f"\n验证7种语言翻译...")
    for lang in required_languages:
        if lang not in description or not description[lang]:
            errors.append(f"缺少{lang}语言翻译")
            print(f"❌ 缺少{lang}语言翻译")
        else:
            print(f"✅ {lang}语言翻译存在")

    # 6. 验证图片URL
    image_url = data.get('image', data.get('thumbnail', ''))
    if image_url:
        print(f"\n验证产品图片URL...")
        try:
            status_code, _ = http_head(image_url, timeout=10)
            if status_code == 200:
                print(f"✅ 图片URL有效: {image_url[:60]}...")
            else:
                errors.append(f"图片URL无效 (状态码: {status_code}): {image_url}")
                print(f"❌ 图片URL无效 (状态码: {status_code})")
        except Exception as e:
            errors.append(f"图片URL验证失败: {e}")
            print(f"❌ 图片URL验证失败: {e}")

    # 7. 验证项目案例
    projects = data.get('projects', [])
    print(f"\n项目案例数量: {len(projects)}")

    cn_url = data.get('cn_url', f"https://cn.peri.com/products/{slug}.html")
    product_page_html = ''
    try:
        status_code, body, _ = http_get(cn_url, timeout=15)
        if status_code == 200:
            product_page_html = body
            print("✅ 已获取原始产品页用于项目来源验证")
        else:
            warnings.append(f"无法获取原始产品页验证项目来源: {cn_url} (状态码: {status_code})")
            print(f"⚠️  无法获取原始产品页验证项目来源")
    except Exception as e:
        warnings.append(f"无法获取原始产品页验证项目来源: {e}")
        print(f"⚠️  无法获取原始产品页验证项目来源: {e}")

    if len(projects) == 0:
        report_projects = source_report.get("projects")
        if isinstance(report_projects, list) and len(report_projects) == 0:
            print(f"ℹ️  源报告确认该产品没有项目案例")
        else:
            warnings.append("没有项目案例，请确认该产品确实没有项目案例")
            print(f"⚠️  没有项目案例")

    for i, project in enumerate(projects, 1):
        print(f"\n验证项目 {i}/{len(projects)}: {project.get('name', 'N/A')}")

        required_project_fields = ['name', 'location', 'description', 'image', 'link']
        for field in required_project_fields:
            if field not in project:
                errors.append(f"项目{i}缺少字段: {field}")
                print(f"  ❌ 缺少字段: {field}")
            else:
                value = str(project[field])
                print(f"  ✅ {field}: {value[:50]}{'...' if len(value) > 50 else ''}")

        # 验证项目图片
        project_image = project.get('image', '')
        if project_image:
            try:
                status_code, _ = http_head(project_image, timeout=10)
                if status_code == 200:
                    print(f"  ✅ 项目图片有效")
                else:
                    errors.append(f"项目{i}图片无效 (状态码: {status_code})")
                    print(f"  ❌ 项目图片无效 (状态码: {status_code})")
            except Exception as e:
                errors.append(f"项目{i}图片验证失败: {e}")
                print(f"  ❌ 项目图片验证失败: {e}")

        project_link = project.get('link', '')
        if product_page_html and project_link:
            if project_link not in product_page_html:
                errors.append(f"项目{i}链接不在原始产品页中: {project_link}")
                print(f"  ❌ 项目链接不在原始产品页中")
            else:
                print(f"  ✅ 项目链接确实来自原始产品页")

    # 8. 验证PDF链接
    pdf_link = data.get('pdf_link', '')
    if pdf_link:
        print(f"\n验证PDF链接...")
        try:
            status_code, headers = http_head(pdf_link, timeout=10)
            if status_code == 200:
                content_type = header_value(headers, "content-type")
                trusted_pdf = TRUSTED_PDF_LINKS.get(slug, "")
                report_pdf_candidates = source_report.get("pdf_candidates") or []
                report_expected_pdf = report_pdf_candidates[0]["url"] if report_pdf_candidates else ""
                pdf_is_audited = same_url(pdf_link, trusted_pdf) or same_url(pdf_link, report_expected_pdf)
                if not is_verified_pdf_url(pdf_link, slug, headers=headers, trusted_url=trusted_pdf):
                    errors.append(f"PDF链接与产品slug或已验证映射不匹配: {pdf_link}")
                    print(f"❌ PDF链接与产品slug或可信映射不匹配")
                elif 'pdf' in content_type.lower() or '/.rest/downloads/' in pdf_link:
                    print(f"✅ PDF链接有效: {pdf_link[:60]}...")
                    if pdf_is_audited:
                        print(f"✅ PDF已由可信映射/源报告确认")
                    else:
                        warnings.append(f"⚠️  请人工确认PDF内容是该产品的手册: {pdf_link}")
                        print(f"⚠️  请人工确认PDF内容是该产品的手册")
                else:
                    errors.append(f"PDF链接的Content-Type不是application/pdf: {content_type}")
                    print(f"❌ Content-Type不是application/pdf: {content_type}")
            else:
                errors.append(f"PDF链接无效 (状态码: {status_code}): {pdf_link}")
                print(f"❌ PDF链接无效 (状态码: {status_code})")
        except Exception as e:
            errors.append(f"PDF链接验证失败: {e}")
            print(f"❌ PDF链接验证失败: {e}")
    else:
        print(f"\nℹ️  无PDF链接")

    # 9. 验证YouTube视频
    video_id = data.get('youtube_video_id', '')
    if video_id:
        print(f"\n验证YouTube视频...")
        if len(video_id) == 11:
            print(f"✅ 视频ID格式正确: {video_id}")
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            try:
                oembed_url = f"https://www.youtube.com/oembed?format=json&url={quote(watch_url, safe='')}"
                status_code, body, _ = http_get(oembed_url, timeout=15)
                if status_code != 200 or not body:
                    errors.append(f"YouTube视频无法访问或oEmbed失败 (状态码: {status_code}): {watch_url}")
                    print(f"❌ YouTube视频无法访问")
                else:
                    meta = json.loads(body)
                    title = (meta.get("title") or "").strip()
                    author_name = (meta.get("author_name") or "").strip()
                    author_url = (meta.get("author_url") or "").strip()
                    if not is_official_peri_youtube(author_name=author_name, author_url=author_url):
                        warnings.append(f"YouTube视频未明确识别为PERI官方频道，请人工确认: {watch_url}")
                        print(f"⚠️  未明确识别为PERI官方频道")
                    else:
                        print(f"✅ 视频作者识别为PERI官方频道: {author_name}")

                    keywords = slug_keywords(slug)
                    required_match_count = 1 if len(keywords) <= 1 else min(2, len(keywords))
                    if title and slug_match_count(title, slug) < required_match_count:
                        warnings.append(f"YouTube标题与产品slug关键词不够匹配，请人工确认: {title}")
                        print(f"⚠️  视频标题与产品关键词不够匹配: {title}")
                    elif title:
                        print(f"✅ 视频标题: {title}")

                    report_decision = source_report.get("youtube_decision") or {}
                    report_selected_video_id = report_decision.get("selected_video_id", "")
                    if (
                        report_selected_video_id == video_id
                        and is_official_peri_youtube(author_name=author_name, author_url=author_url)
                        and title
                        and slug_match_count(title, slug) >= required_match_count
                    ):
                        print(f"✅ YouTube已由源报告确认")
                    else:
                        warnings.append(f"⚠️  请人工确认视频是该产品的英语介绍: {watch_url}")
                        print(f"⚠️  请人工确认视频是该产品的英语介绍")
            except Exception as e:
                errors.append(f"YouTube视频验证失败: {e}")
                print(f"❌ YouTube视频验证失败: {e}")
        else:
            errors.append(f"视频ID格式不正确 (应为11个字符): {video_id}")
            print(f"❌ 视频ID格式不正确 (应为11个字符): {video_id}")
    else:
        print(f"\nℹ️  无YouTube视频")

    # 10. 验证生成的HTML
    html_path = f"products/{slug}.html"
    if os.path.exists(html_path):
        print(f"\n✅ HTML文件存在: {html_path}")

        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 验证PDF链接在HTML中
        if pdf_link and pdf_link not in html_content:
            errors.append(f"PDF链接未在HTML中找到")
            print(f"❌ PDF链接未在HTML中找到")
        elif pdf_link:
            print(f"✅ PDF链接在HTML中")

        # 验证YouTube视频在HTML中
        embed_present = (
            f"youtube.com/embed/{video_id}" in html_content or
            f"youtube-nocookie.com/embed/{video_id}" in html_content
        )
        if video_id and not embed_present:
            errors.append(f"YouTube视频未在HTML中找到")
            print(f"❌ YouTube视频未在HTML中找到")
        elif video_id:
            print(f"✅ YouTube视频在HTML中")

        # 验证项目数量
        project_count = html_content.count("window.open('https://cn.peri.com/projects/")
        if project_count != len(projects):
            errors.append(f"HTML中的项目数量不匹配 - 期望: {len(projects)}, 实际: {project_count}")
            print(f"❌ HTML中的项目数量不匹配 - 期望: {len(projects)}, 实际: {project_count}")
        else:
            print(f"✅ HTML中的项目数量匹配: {project_count}")
    else:
        warnings.append(f"HTML文件不存在: {html_path} (可能还未生成)")
        print(f"⚠️  HTML文件不存在: {html_path}")

    # 11. 输出结果
    print(f"\n{'='*60}")
    print(f"验证完成")
    print(f"{'='*60}\n")

    if errors:
        print(f"❌ 发现 {len(errors)} 个错误:\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")

    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个警告:\n")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")

    if not errors and not warnings:
        print(f"✅ 所有验证通过！")
    elif not errors:
        print(f"\n✅ 自动验证通过，请完成人工验证")

    return errors, warnings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 verify_product.py <product-slug>")
        print("示例: python3 verify_product.py gridflex-deckenschalung")
        sys.exit(1)

    slug = sys.argv[1]
    errors, warnings = verify_product(slug)

    if errors:
        print(f"\n❌ 验证失败！请修正错误后重新验证。")
        sys.exit(1)  # 有错误，退出码1
    else:
        print(f"\n✅ 验证成功！")
        sys.exit(0)  # 无错误，退出码0
