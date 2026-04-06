#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复所有产品的图片URL
从cn.peri.com提取真实的产品图片URL
"""

import json
import subprocess
import re
import time

def get_image_url_from_cn_peri(product_slug):
    """从cn.peri.com产品页面提取图片URL"""
    url = f"https://cn.peri.com/products/{product_slug}.html"

    try:
        # 使用curl获取页面内容
        result = subprocess.run(
            ['curl', '-s', url],
            capture_output=True,
            text=True,
            timeout=10
        )

        html = result.stdout

        # 查找产品图片URL的多种模式
        patterns = [
            r'<meta property="og:image" content="(https://cdn\.peri\.cloud/[^"]+)"',
            r'class="product-image"[^>]*src="(https://cdn\.peri\.cloud/[^"]+)"',
            r'<img[^>]*class="[^"]*product[^"]*"[^>]*src="(https://cdn\.peri\.cloud/[^"]+)"',
            r'data-src="(https://cdn\.peri\.cloud/[^"]+)"',
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                img_url = match.group(1)
                # 验证URL
                test_result = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', img_url],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if test_result.stdout.strip() == '200':
                    return img_url

        return None

    except Exception as e:
        print(f"  ⚠️  错误: {str(e)}")
        return None

def main():
    # 加载products_v2.json
    with open('products_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = 0
    fixed = 0
    failed = 0

    print("开始修复所有产品的图片URL...\n")

    for cat_key, cat in data.items():
        print(f"\n{'='*60}")
        print(f"分类: {cat_key}")
        print(f"{'='*60}")

        if 'subcategories' in cat:
            for sc_key, sc in cat['subcategories'].items():
                print(f"\n子分类: {sc_key}")
                for i, p in enumerate(sc['products']):
                    total += 1
                    slug, name = p[0], p[1]
                    current_url = p[3]

                    # 测试当前URL
                    try:
                        test_result = subprocess.run(
                            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', current_url],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if test_result.stdout.strip() == '200':
                            print(f"  ✅ {name} - URL有效")
                            continue
                    except:
                        pass

                    # URL无效，尝试从cn.peri.com提取
                    print(f"  🔧 {name} - 提取新URL...")
                    new_url = get_image_url_from_cn_peri(slug)

                    if new_url:
                        sc['products'][i][3] = new_url
                        fixed += 1
                        print(f"     ✅ 已修复")
                    else:
                        failed += 1
                        print(f"     ❌ 提取失败")

                    time.sleep(0.5)  # 避免请求过快
        else:
            for i, p in enumerate(cat.get('products', [])):
                total += 1
                slug, name = p[0], p[1]
                current_url = p[3]

                # 测试当前URL
                try:
                    test_result = subprocess.run(
                        ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', current_url],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if test_result.stdout.strip() == '200':
                        print(f"  ✅ {name} - URL有效")
                        continue
                except:
                    pass

                # URL无效，尝试从cn.peri.com提取
                print(f"  🔧 {name} - 提取新URL...")
                new_url = get_image_url_from_cn_peri(slug)

                if new_url:
                    cat['products'][i][3] = new_url
                    fixed += 1
                    print(f"     ✅ 已修复")
                else:
                    failed += 1
                    print(f"     ❌ 提取失败")

                time.sleep(0.5)

    # 保存修复后的数据
    with open('products_v2_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"修复完成！")
    print(f"{'='*60}")
    print(f"总计: {total}个产品")
    print(f"已修复: {fixed}个")
    print(f"修复失败: {failed}个")
    print(f"无需修复: {total - fixed - failed}个")
    print(f"\n修复后的数据已保存到: products_v2_fixed.json")

if __name__ == '__main__':
    main()
