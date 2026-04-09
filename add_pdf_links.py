#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建已验证PDF链接索引。

只收录 *_complete.json 中已经人工确认过的官方直链PDF。
不再为所有产品生成 `#downloads` 这类占位链接，避免页面错误展示“PDF按钮”。
"""

import json
import os
from pathlib import Path
from http_helpers import http_head
from source_rules import is_verified_pdf_url


def load_pdf_overrides(base_dir):
    path = Path(base_dir) / "pdf_overrides.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_links = {}
    complete_files = sorted(Path(base_dir).glob('*_complete.json'))
    overrides = load_pdf_overrides(base_dir)

    for slug, pdf_url in overrides.items():
        status_code, headers = http_head(pdf_url, timeout=15)
        if status_code == 200 and is_verified_pdf_url(pdf_url, slug, headers=headers, trusted_url=pdf_url):
            pdf_links[slug] = pdf_url

    for complete_file in complete_files:
        with open(complete_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        slug = data.get('slug')
        pdf_url = data.get('pdf_link', '')
        if not slug or slug in pdf_links:
            continue

        status_code, headers = http_head(pdf_url, timeout=15)
        if status_code == 200 and is_verified_pdf_url(pdf_url, slug, headers=headers, trusted_url=overrides.get(slug, '')):
            pdf_links[slug] = pdf_url

    output_file = os.path.join(base_dir, 'product_pdf_links.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pdf_links, f, ensure_ascii=False, indent=2)

    print(f"✅ 已收录 {len(pdf_links)} 个已验证PDF链接")
    print(f"📄 链接已保存到: {output_file}")
    print(f"\n示例链接:")
    for i, (slug, url) in enumerate(list(pdf_links.items())[:5]):
        print(f"  {slug}: {url}")

if __name__ == '__main__':
    main()
