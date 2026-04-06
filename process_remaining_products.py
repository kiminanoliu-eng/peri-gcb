#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理剩余153个产品
为每个产品添加项目案例和YouTube视频ID
"""

import json
import subprocess
import re
import os

def get_projects_from_cn_peri(slug):
    """从cn.peri.com提取项目案例"""
    url = f"https://cn.peri.com/products/{slug}.html"

    try:
        result = subprocess.run(['curl', '-s', url], capture_output=True, text=True, timeout=10)
        html = result.stdout

        # 提取项目链接
        project_links = re.findall(r'href="(/projects/[^"]+\.html)"', html)

        if not project_links:
            return []

        projects = []
        for link in project_links[:4]:  # 最多4个项目
            project_url = f"https://cn.peri.com{link}"
            proj_result = subprocess.run(['curl', '-s', project_url], capture_output=True, text=True, timeout=10)
            proj_html = proj_result.stdout

            # 提取项目信息
            name_match = re.search(r'<h1[^>]*>([^<]+)</h1>', proj_html)
            location_match = re.search(r'<span[^>]*class="[^"]*location[^"]*"[^>]*>([^<]+)</span>', proj_html)
            desc_match = re.search(r'<meta name="description" content="([^"]+)"', proj_html)
            img_match = re.search(r'<meta property="og:image" content="(https://cdn\.peri\.cloud/[^"]+)"', proj_html)

            if name_match:
                project = {
                    'name': name_match.group(1).strip(),
                    'location': location_match.group(1).strip() if location_match else '',
                    'description': desc_match.group(1).strip() if desc_match else '',
                    'image': img_match.group(1) if img_match else '',
                    'link': project_url
                }
                projects.append(project)

        return projects

    except Exception as e:
        print(f"      错误: {str(e)}")
        return []

def main():
    # 加载products_v2.json
    with open('products_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 已完成的7个产品
    completed = {
        'handset-alpha',
        'vario-gt-24-girder-wall-formwork',
        'maximo-panel-formwork',
        'skydeck-slab-formwork',
        'multiflex-girder-slab-formwork',
        'gridflex-deckenschalung',
        'domino-panel-formwork'
    }

    # 统计
    total = 0
    processed = 0
    has_projects = 0
    no_projects = 0

    # 存储结果
    results = {}

    print("开始处理剩余153个产品...\n")
    print("提取项目案例（YouTube视频需要手动添加）\n")

    for cat_key, cat in data.items():
        print(f"\n{'='*60}")
        print(f"分类: {cat_key}")
        print(f"{'='*60}")

        if 'subcategories' in cat:
            for sc_key, sc in cat['subcategories'].items():
                print(f"\n  子分类: {sc_key}")
                for p in sc['products']:
                    slug, name = p[0], p[1]

                    if slug in completed:
                        print(f"    ⏭️  {name} - 已完成")
                        continue

                    total += 1
                    print(f"    🔍 {name} - 提取项目案例...", end='', flush=True)

                    projects = get_projects_from_cn_peri(slug)

                    if projects:
                        has_projects += 1
                        print(f" ✅ 找到{len(projects)}个项目")
                    else:
                        no_projects += 1
                        print(f" ⚠️  无项目")

                    results[slug] = {
                        'name_zh': name,
                        'category': cat_key,
                        'subcategory': sc_key,
                        'projects': projects,
                        'youtube_video_id': '',  # 需要手动添加
                    }

                    processed += 1
        else:
            for p in cat.get('products', []):
                slug, name = p[0], p[1]

                if slug in completed:
                    print(f"  ⏭️  {name} - 已完成")
                    continue

                total += 1
                print(f"  🔍 {name} - 提取项目案例...", end='', flush=True)

                projects = get_projects_from_cn_peri(slug)

                if projects:
                    has_projects += 1
                    print(f" ✅ 找到{len(projects)}个项目")
                else:
                    no_projects += 1
                    print(f" ⚠️  无项目")

                results[slug] = {
                    'name_zh': name,
                    'category': cat_key,
                    'subcategory': None,
                    'projects': projects,
                    'youtube_video_id': '',  # 需要手动添加
                }

                processed += 1

    # 保存结果
    with open('remaining_products_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"处理完成！")
    print(f"{'='*60}")
    print(f"总计: {total}个产品")
    print(f"已处理: {processed}个")
    print(f"有项目案例: {has_projects}个 ({has_projects*100//total if total > 0 else 0}%)")
    print(f"无项目案例: {no_projects}个 ({no_projects*100//total if total > 0 else 0}%)")
    print(f"\n结果已保存到: remaining_products_data.json")
    print(f"\n下一步: 手动添加YouTube视频ID到 remaining_products_data.json")

if __name__ == '__main__':
    main()
