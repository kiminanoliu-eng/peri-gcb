#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量验证产品 - 分批检查所有产品
"""

import json
import sys

# 读取产品列表
with open('product_list.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# 获取批次参数
if len(sys.argv) > 1:
    batch_num = int(sys.argv[1])
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 10
else:
    batch_num = 0
    batch_size = 10

start = batch_num * batch_size
end = min(start + batch_size, len(products))

print(f"批次 {batch_num + 1}: 检查产品 {start + 1} 到 {end}")
print(f"总共 {len(products)} 个产品，每批 {batch_size} 个")
print()

batch_products = products[start:end]

for i, p in enumerate(batch_products, start + 1):
    print(f"{i}. {p['slug']}")
    print(f"   名称: {p['name']}")
    print(f"   URL: https://cn.peri.com/products/{p['slug']}.html")
    print()

# 保存当前批次
with open(f'batch_{batch_num}.json', 'w', encoding='utf-8') as f:
    json.dump(batch_products, f, ensure_ascii=False, indent=2)

print(f"批次数据已保存到 batch_{batch_num}.json")
print(f"剩余批次: {(len(products) - end + batch_size - 1) // batch_size}")
