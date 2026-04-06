#!/usr/bin/env python3
"""
产品数据预检脚本
在创建JSON文件前和生成HTML前运行，自动检查常见错误
"""

import json
import os
import sys
import re
from pathlib import Path

# 工作目录
BASE_DIR = "/Users/fufu/Documents/Claude/Projects/自动化/创建产品网站"

def check_slug_format(slug):
    """检查slug格式是否正确"""
    errors = []

    # 检查是否包含下划线（应该使用连字符）
    if '_' in slug:
        errors.append(f"❌ slug包含下划线'_'，应该使用连字符'-': {slug}")

    # 检查是否包含空格
    if ' ' in slug:
        errors.append(f"❌ slug包含空格，应该使用连字符'-': {slug}")

    # 检查是否包含大写字母（slug应该全小写）
    if slug != slug.lower() and not any(ord(c) > 127 for c in slug):  # 排除中文字符
        errors.append(f"❌ slug包含大写字母，应该全小写: {slug}")

    return errors

def check_slug_exists_in_products_v2(slug):
    """检查slug是否在products_v2.json中存在"""
    products_v2_path = os.path.join(BASE_DIR, "products_v2.json")

    if not os.path.exists(products_v2_path):
        return [f"❌ products_v2.json文件不存在: {products_v2_path}"]

    try:
        with open(products_v2_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # products_v2.json的结构是嵌套的分类结构
        slugs = []

        if isinstance(data, dict):
            # 遍历所有分类
            for category_name, category_data in data.items():
                if isinstance(category_data, dict) and 'subcategories' in category_data:
                    # 遍历所有子分类
                    for subcat_name, subcat_data in category_data['subcategories'].items():
                        if isinstance(subcat_data, dict) and 'products' in subcat_data:
                            # 遍历所有产品
                            for product in subcat_data['products']:
                                if isinstance(product, list) and len(product) > 0:
                                    slugs.append(product[0])  # 第一个元素是slug

        if slug not in slugs:
            return [f"❌ slug '{slug}' 不在products_v2.json中"]

        return []

    except Exception as e:
        return [f"❌ 读取products_v2.json失败: {e}"]

def check_filename_matches_slug(slug):
    """检查文件名是否与slug匹配"""
    expected_filename = f"{slug}_complete.json"
    file_path = os.path.join(BASE_DIR, expected_filename)

    errors = []

    if not os.path.exists(file_path):
        errors.append(f"❌ 文件不存在: {expected_filename}")

        # 查找可能的错误文件名
        similar_files = []
        for f in os.listdir(BASE_DIR):
            if f.endswith('_complete.json'):
                # 检查是否是slug的变体
                base = f.replace('_complete.json', '')
                if base.replace('-', '_') == slug.replace('-', '_'):
                    similar_files.append(f)

        if similar_files:
            errors.append(f"   可能的错误文件名: {', '.join(similar_files)}")

    return errors

def check_json_structure(slug):
    """检查JSON文件结构是否完整"""
    filename = f"{slug}_complete.json"
    file_path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(file_path):
        return [f"⚠️  跳过JSON结构检查（文件不存在）"]

    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"❌ JSON格式错误: {e}"]
    except Exception as e:
        return [f"❌ 读取JSON文件失败: {e}"]

    # 检查必需字段
    required_fields = [
        'slug', 'name_zh', 'category', 'subcategory', 'cn_url',
        'image', 'description', 'projects', 'pdf_link', 'youtube_video_id'
    ]

    for field in required_fields:
        if field not in data:
            errors.append(f"❌ 缺少必需字段: {field}")

    # 检查slug是否匹配
    if 'slug' in data and data['slug'] != slug:
        errors.append(f"❌ JSON中的slug不匹配")
        errors.append(f"   期望: {slug}")
        errors.append(f"   实际: {data['slug']}")

    # 检查description是否包含7种语言
    if 'description' in data:
        required_langs = ['zh', 'en', 'es', 'de', 'pt', 'sr', 'hu']
        desc = data['description']

        if not isinstance(desc, dict):
            errors.append(f"❌ description应该是对象，不是{type(desc).__name__}")
        else:
            for lang in required_langs:
                if lang not in desc:
                    errors.append(f"❌ description缺少语言: {lang}")
                elif not desc[lang] or not desc[lang].strip():
                    errors.append(f"⚠️  description的{lang}为空")

    # 检查projects是否是数组
    if 'projects' in data:
        if not isinstance(data['projects'], list):
            errors.append(f"❌ projects应该是数组，不是{type(data['projects']).__name__}")
        else:
            # 检查每个项目的结构
            for i, project in enumerate(data['projects']):
                required_project_fields = ['name', 'location', 'description', 'image', 'link']
                for field in required_project_fields:
                    if field not in project:
                        errors.append(f"❌ 项目{i+1}缺少字段: {field}")

    # 检查pdf_link和youtube_video_id是否是字符串
    if 'pdf_link' in data and not isinstance(data['pdf_link'], str):
        errors.append(f"❌ pdf_link应该是字符串，不是{type(data['pdf_link']).__name__}")

    if 'youtube_video_id' in data:
        if not isinstance(data['youtube_video_id'], str):
            errors.append(f"❌ youtube_video_id应该是字符串，不是{type(data['youtube_video_id']).__name__}")
        elif data['youtube_video_id'] and len(data['youtube_video_id']) != 11:
            errors.append(f"⚠️  youtube_video_id长度不是11个字符: {data['youtube_video_id']}")

    return errors

def check_html_generated(slug):
    """检查HTML文件是否生成"""
    html_path = os.path.join(BASE_DIR, "products", f"{slug}.html")

    if not os.path.exists(html_path):
        return [f"⚠️  HTML文件未生成: products/{slug}.html"]

    # 检查文件大小
    file_size = os.path.getsize(html_path)
    if file_size < 1024:  # 小于1KB
        return [f"⚠️  HTML文件太小（{file_size}字节），可能生成失败"]

    return []

def pre_flight_check(slug, check_type="all"):
    """
    执行预检

    check_type:
        - "slug": 只检查slug格式和存在性
        - "json": 检查JSON文件
        - "html": 检查HTML文件
        - "all": 检查所有
    """
    print(f"\n{'='*60}")
    print(f"预检: {slug}")
    print(f"{'='*60}\n")

    all_errors = []
    all_warnings = []

    # 检查slug格式
    if check_type in ["slug", "all"]:
        print("🔍 检查slug格式...")
        errors = check_slug_format(slug)
        if errors:
            all_errors.extend(errors)
        else:
            print("✅ slug格式正确")

        # 检查slug是否在products_v2.json中
        print("\n🔍 检查slug是否在products_v2.json中...")
        errors = check_slug_exists_in_products_v2(slug)
        if errors:
            all_errors.extend(errors)
        else:
            print("✅ slug存在于products_v2.json")

    # 检查文件名
    if check_type in ["json", "all"]:
        print("\n🔍 检查文件名是否与slug匹配...")
        errors = check_filename_matches_slug(slug)
        if errors:
            all_errors.extend(errors)
        else:
            print(f"✅ 文件名正确: {slug}_complete.json")

        # 检查JSON结构
        print("\n🔍 检查JSON文件结构...")
        errors = check_json_structure(slug)
        for error in errors:
            if error.startswith('❌'):
                all_errors.append(error)
            elif error.startswith('⚠️'):
                all_warnings.append(error)
            else:
                print(error)

        if not any(e.startswith('❌') for e in errors):
            print("✅ JSON结构完整")

    # 检查HTML
    if check_type in ["html", "all"]:
        print("\n🔍 检查HTML文件...")
        errors = check_html_generated(slug)
        if errors:
            all_warnings.extend(errors)
        else:
            print(f"✅ HTML文件已生成: products/{slug}.html")

    # 输出结果
    print(f"\n{'='*60}")
    print("预检结果")
    print(f"{'='*60}\n")

    if all_errors:
        print(f"❌ 发现 {len(all_errors)} 个错误:\n")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")

    if all_warnings:
        print(f"\n⚠️  发现 {len(all_warnings)} 个警告:\n")
        for i, warning in enumerate(all_warnings, 1):
            print(f"  {i}. {warning}")

    if not all_errors and not all_warnings:
        print("✅ 所有检查通过！")

    print()

    return len(all_errors) == 0

def main():
    if len(sys.argv) < 2:
        print("用法: python3 pre_flight_check.py <product-slug> [check-type]")
        print()
        print("check-type:")
        print("  slug  - 只检查slug格式和存在性")
        print("  json  - 检查JSON文件")
        print("  html  - 检查HTML文件")
        print("  all   - 检查所有（默认）")
        print()
        print("示例:")
        print("  python3 pre_flight_check.py gridflex-deckenschalung")
        print("  python3 pre_flight_check.py handset-alpha slug")
        print("  python3 pre_flight_check.py uno-formwork-system json")
        sys.exit(1)

    slug = sys.argv[1]
    check_type = sys.argv[2] if len(sys.argv) > 2 else "all"

    if check_type not in ["slug", "json", "html", "all"]:
        print(f"❌ 无效的check-type: {check_type}")
        print("   有效值: slug, json, html, all")
        sys.exit(1)

    success = pre_flight_check(slug, check_type)

    if success:
        sys.exit(0)  # 成功
    else:
        sys.exit(1)  # 有错误

if __name__ == "__main__":
    main()
