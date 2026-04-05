#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品验证脚本 - 检查所有产品的有效性
"""

import json
import os

# 读取产品数据
with open('products_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取所有产品
all_products = []
for cat_key, cat in data.items():
    if 'subcategories' in cat:
        for sc_key, sc in cat['subcategories'].items():
            for p in sc['products']:
                all_products.append({
                    'slug': p[0],
                    'name': p[1],
                    'desc': p[2],
                    'img': p[3],
                    'category': cat_key,
                    'subcategory': sc_key
                })
    else:
        for p in cat.get('products', []):
            all_products.append({
                'slug': p[0],
                'name': p[1],
                'desc': p[2],
                'img': p[3],
                'category': cat_key,
                'subcategory': None
            })

print(f"总共找到 {len(all_products)} 个产品")
print("\n产品列表：")
for i, p in enumerate(all_products, 1):
    print(f"{i}. {p['slug']} - {p['name']}")

# 保存产品列表供后续使用
with open('product_list.json', 'w', encoding='utf-8') as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print(f"\n产品列表已保存到 product_list.json")
