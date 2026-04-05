#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为产品添加PDF下载链接
策略：使用Google搜索 "产品英文名 PERI PDF" 来查找PDF文档
"""

import json
import os

def generate_pdf_search_url(product_name_en, slug):
    """生成Google搜索PDF的URL"""
    import urllib.parse
    # 使用产品slug作为搜索关键词（通常是英文）
    search_query = f"{slug.replace('-', ' ')} PERI formwork PDF"
    encoded_query = urllib.parse.quote(search_query)
    return f"https://www.google.com/search?q={encoded_query}"

def generate_peri_pdf_url(slug):
    """生成PERI官网可能的PDF链接"""
    # PERI的PDF通常在这个路径下
    return f"https://www.peri.com/en/products/{slug}.html#downloads"

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    products_file = os.path.join(base_dir, 'products_v2.json')

    with open(products_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 为每个产品生成PDF链接
    pdf_links = {}

    for cat_key, cat in data.items():
        if 'subcategories' in cat:
            for sc_key, sc in cat['subcategories'].items():
                for p in sc['products']:
                    slug = p[0]
                    name_zh = p[1]
                    # 使用PERI官网的下载页面
                    pdf_links[slug] = generate_peri_pdf_url(slug)
        else:
            for p in cat.get('products', []):
                slug = p[0]
                name_zh = p[1]
                pdf_links[slug] = generate_peri_pdf_url(slug)

    # 保存PDF链接映射
    output_file = os.path.join(base_dir, 'product_pdf_links.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pdf_links, f, ensure_ascii=False, indent=2)

    print(f"✅ 已为 {len(pdf_links)} 个产品生成PDF链接")
    print(f"📄 链接已保存到: {output_file}")
    print(f"\n示例链接:")
    for i, (slug, url) in enumerate(list(pdf_links.items())[:5]):
        print(f"  {slug}: {url}")

if __name__ == '__main__':
    main()
