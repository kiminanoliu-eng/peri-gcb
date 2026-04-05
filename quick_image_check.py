#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证产品图片 - 简化版本
检查products_v2.json中的图片URL是否有效
"""

import json
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    products_file = os.path.join(base_dir, 'products_v2.json')

    with open(products_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    issues = []
    valid_count = 0
    total_count = 0

    for cat_key, cat in data.items():
        if 'subcategories' in cat:
            for sc_key, sc in cat['subcategories'].items():
                for p in sc['products']:
                    total_count += 1
                    slug, name_zh, desc_zh, img = p[0], p[1], p[2], p[3]

                    # 检查图片URL
                    if not img:
                        issues.append({
                            'slug': slug,
                            'name': name_zh,
                            'issue': '缺少图片URL',
                            'category': f'{cat_key} > {sc_key}'
                        })
                    elif 'placeholder' in img.lower() or 'vario-gt-24' in img and slug != 'vario-gt-24-girder-wall-formwork':
                        issues.append({
                            'slug': slug,
                            'name': name_zh,
                            'issue': '使用占位符图片',
                            'current_img': img,
                            'category': f'{cat_key} > {sc_key}'
                        })
                    else:
                        valid_count += 1
        else:
            for p in cat.get('products', []):
                total_count += 1
                slug, name_zh, desc_zh, img = p[0], p[1], p[2], p[3]

                if not img:
                    issues.append({
                        'slug': slug,
                        'name': name_zh,
                        'issue': '缺少图片URL',
                        'category': cat_key
                    })
                elif 'placeholder' in img.lower():
                    issues.append({
                        'slug': slug,
                        'name': name_zh,
                        'issue': '使用占位符图片',
                        'current_img': img,
                        'category': cat_key
                    })
                else:
                    valid_count += 1

    # 生成报告
    report = {
        'total_products': total_count,
        'valid_images': valid_count,
        'issues_count': len(issues),
        'issues': issues
    }

    output_file = os.path.join(base_dir, 'image_validation_report.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ 验证完成")
    print(f"总产品数: {total_count}")
    print(f"有效图片: {valid_count}")
    print(f"问题数量: {len(issues)}")
    print(f"\n报告已保存到: {output_file}")

    if issues:
        print(f"\n前10个问题:")
        for i, issue in enumerate(issues[:10], 1):
            print(f"{i}. {issue['name']} ({issue['slug']})")
            print(f"   分类: {issue['category']}")
            print(f"   问题: {issue['issue']}")
            if 'current_img' in issue:
                print(f"   当前图片: {issue['current_img'][:80]}...")
            print()

if __name__ == '__main__':
    main()
