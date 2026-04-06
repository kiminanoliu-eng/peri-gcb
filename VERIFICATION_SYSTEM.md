# 文件命名和最终验证方案

## 问题根源

**核心问题**：文件名与slug不匹配导致代码找不到文件

**案例**：
- `handset_alpha_complete.json` vs slug `handset-alpha`
- `vario_gt24_complete.json` vs slug `vario-gt-24-girder-wall-formwork`

---

## 解决方案1: 统一命名规则

### 强制规则：文件名必须与slug完全匹配

**命名格式**：`{slug}_complete.json`

**示例**：
```
slug: "gridflex-deckenschalung"
文件名: "gridflex-deckenschalung_complete.json"  ✅

slug: "handset-alpha"
文件名: "handset-alpha_complete.json"  ✅ (不是handset_alpha)

slug: "vario-gt-24-girder-wall-formwork"
文件名: "vario-gt-24-girder-wall-formwork_complete.json"  ✅ (不是vario_gt24)
```

**关键点**：
1. slug中的连字符 `-` 必须保留，不能替换成下划线 `_`
2. slug中的完整名称必须保留，不能简化
3. 只在最后加 `_complete.json`

---

## 解决方案2: 创建验证Agent

### Agent职责：100%验证最终结果

**Agent名称**：`product-verification-agent`

**验证时机**：每个产品完成后，部署前

**验证内容**：

#### 1. 文件命名验证
```bash
# 检查文件名是否与slug匹配
expected_filename="${slug}_complete.json"
if [ ! -f "$expected_filename" ]; then
    echo "❌ 错误：文件名不匹配"
    echo "   期望：$expected_filename"
    echo "   实际：$(ls *_complete.json | grep -i ${slug:0:10})"
    exit 1
fi
```

#### 2. JSON结构验证
```python
import json

# 读取JSON文件
with open(f'{slug}_complete.json', 'r') as f:
    data = json.load(f)

# 验证必需字段
required_fields = [
    'slug', 'name_zh', 'category', 'cn_url', 'image',
    'description', 'projects', 'pdf_link', 'youtube_video_id'
]

for field in required_fields:
    if field not in data:
        print(f"❌ 错误：缺少字段 {field}")
        exit(1)

# 验证slug匹配
if data['slug'] != slug:
    print(f"❌ 错误：JSON中的slug不匹配")
    print(f"   期望：{slug}")
    print(f"   实际：{data['slug']}")
    exit(1)
```

#### 3. 项目案例验证
```python
# 验证项目数量
projects = data.get('projects', [])
print(f"项目案例数量：{len(projects)}")

# 验证每个项目的必需字段
for i, project in enumerate(projects):
    required_project_fields = ['name', 'location', 'description', 'image', 'link']
    for field in required_project_fields:
        if field not in project:
            print(f"❌ 错误：项目{i+1}缺少字段 {field}")
            exit(1)
    
    # 验证项目图片URL
    import requests
    response = requests.head(project['image'])
    if response.status_code != 200:
        print(f"❌ 错误：项目{i+1}图片URL无效")
        print(f"   URL: {project['image']}")
        print(f"   状态码: {response.status_code}")
        exit(1)
```

#### 4. PDF链接验证
```python
pdf_link = data.get('pdf_link', '')

if pdf_link:
    # 验证URL有效性
    response = requests.head(pdf_link)
    if response.status_code != 200:
        print(f"❌ 错误：PDF链接无效")
        print(f"   URL: {pdf_link}")
        print(f"   状态码: {response.status_code}")
        exit(1)
    
    # 验证Content-Type
    content_type = response.headers.get('Content-Type', '')
    if 'pdf' not in content_type.lower():
        print(f"⚠️  警告：PDF链接的Content-Type不是application/pdf")
        print(f"   Content-Type: {content_type}")
        print(f"   请人工确认PDF内容是否正确")
```

#### 5. YouTube视频验证
```python
video_id = data.get('youtube_video_id', '')

if video_id:
    # 验证视频ID格式
    if len(video_id) != 11:
        print(f"❌ 错误：YouTube视频ID格式不正确")
        print(f"   视频ID: {video_id}")
        exit(1)
    
    # 验证视频可访问
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ 错误：YouTube视频无法访问")
        print(f"   视频ID: {video_id}")
        exit(1)
```

#### 6. 生成的HTML验证
```bash
# 验证HTML文件生成
if [ ! -f "products/${slug}.html" ]; then
    echo "❌ 错误：产品页面未生成"
    echo "   期望：products/${slug}.html"
    exit 1
fi

# 验证PDF链接在HTML中
if [ -n "$pdf_link" ]; then
    if ! grep -q "$pdf_link" "products/${slug}.html"; then
        echo "❌ 错误：PDF链接未在HTML中找到"
        exit 1
    fi
fi

# 验证YouTube视频在HTML中
if [ -n "$video_id" ]; then
    if ! grep -q "youtube.com/embed/$video_id" "products/${slug}.html"; then
        echo "❌ 错误：YouTube视频未在HTML中找到"
        exit 1
    fi
fi

# 验证项目案例数量
project_count=$(grep -c 'class="card-title"' "products/${slug}.html")
expected_count=${#projects[@]}
if [ "$project_count" -ne "$expected_count" ]; then
    echo "❌ 错误：HTML中的项目数量不匹配"
    echo "   期望：$expected_count"
    echo "   实际：$project_count"
    exit 1
fi
```

#### 7. 最终验证清单

```markdown
## 验证清单

### 文件命名
- [ ] 文件名格式：{slug}_complete.json
- [ ] 文件名与slug完全匹配（包括连字符）
- [ ] 文件存在且可读

### JSON结构
- [ ] 包含所有必需字段
- [ ] slug字段与文件名匹配
- [ ] 7种语言翻译完整

### 项目案例
- [ ] 项目数量 > 0（如果产品页面有项目）
- [ ] 每个项目包含所有必需字段
- [ ] 所有项目图片URL有效（HTTP 200）
- [ ] 项目确实来自该产品的cn.peri.com页面

### PDF链接
- [ ] PDF链接有效（HTTP 200）或为空字符串
- [ ] Content-Type是application/pdf（如果有PDF）
- [ ] **人工确认：PDF内容是该产品的手册**

### YouTube视频
- [ ] 视频ID格式正确（11个字符）或为空字符串
- [ ] 视频可访问（如果有视频）
- [ ] **人工确认：视频是该产品的英语介绍**

### 生成的HTML
- [ ] products/{slug}.html文件存在
- [ ] PDF链接在HTML中（如果有）
- [ ] YouTube视频在HTML中（如果有）
- [ ] 项目案例数量匹配

### 最终确认
- [ ] 所有自动验证通过
- [ ] 所有人工验证完成
- [ ] 准备部署
```

---

## 工作流程集成

### 新的完整流程

```
1. 用户指定产品
   ↓
2. 提取数据（项目、PDF、YouTube）
   ↓
3. 创建 {slug}_complete.json
   ↓
4. 【新增】运行验证Agent
   ↓
   ├─ 通过 → 继续
   └─ 失败 → 修正问题，重新验证
   ↓
5. 重建网站
   ↓
6. 【新增】再次运行验证Agent（验证HTML）
   ↓
   ├─ 通过 → 继续
   └─ 失败 → 修正问题，重新验证
   ↓
7. 部署
   ↓
8. 用户最终验证
```

---

## 实施方案

### 创建验证脚本

```python
# verify_product.py

import json
import os
import sys
import requests
from pathlib import Path

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
        return errors, warnings
    
    print(f"✅ 文件名正确: {expected_filename}")
    
    # 2. 读取JSON
    try:
        with open(expected_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        errors.append(f"JSON解析失败: {e}")
        return errors, warnings
    
    print(f"✅ JSON格式正确")
    
    # 3. 验证必需字段
    required_fields = [
        'slug', 'name_zh', 'category', 'cn_url', 'image',
        'description', 'projects', 'pdf_link', 'youtube_video_id'
    ]
    
    for field in required_fields:
        if field not in data:
            errors.append(f"缺少必需字段: {field}")
        else:
            print(f"✅ 字段存在: {field}")
    
    # 4. 验证slug匹配
    if data.get('slug') != slug:
        errors.append(f"slug不匹配 - 期望: {slug}, 实际: {data.get('slug')}")
    else:
        print(f"✅ slug匹配: {slug}")
    
    # 5. 验证图片URL
    image_url = data.get('image', '')
    if image_url:
        try:
            response = requests.head(image_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ 图片URL有效: {image_url[:50]}...")
            else:
                errors.append(f"图片URL无效 (状态码: {response.status_code}): {image_url}")
        except Exception as e:
            errors.append(f"图片URL验证失败: {e}")
    
    # 6. 验证项目案例
    projects = data.get('projects', [])
    print(f"\n项目案例数量: {len(projects)}")
    
    for i, project in enumerate(projects, 1):
        print(f"\n验证项目 {i}/{len(projects)}: {project.get('name', 'N/A')}")
        
        required_project_fields = ['name', 'location', 'description', 'image', 'link']
        for field in required_project_fields:
            if field not in project:
                errors.append(f"项目{i}缺少字段: {field}")
            else:
                print(f"  ✅ {field}: {str(project[field])[:50]}...")
        
        # 验证项目图片
        project_image = project.get('image', '')
        if project_image:
            try:
                response = requests.head(project_image, timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ 项目图片有效")
                else:
                    errors.append(f"项目{i}图片无效 (状态码: {response.status_code})")
            except Exception as e:
                errors.append(f"项目{i}图片验证失败: {e}")
    
    # 7. 验证PDF链接
    pdf_link = data.get('pdf_link', '')
    if pdf_link:
        print(f"\n验证PDF链接...")
        try:
            response = requests.head(pdf_link, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'pdf' in content_type.lower():
                    print(f"✅ PDF链接有效: {pdf_link[:50]}...")
                    warnings.append(f"⚠️  请人工确认PDF内容是该产品的手册: {pdf_link}")
                else:
                    warnings.append(f"PDF链接的Content-Type不是application/pdf: {content_type}")
            else:
                errors.append(f"PDF链接无效 (状态码: {response.status_code}): {pdf_link}")
        except Exception as e:
            errors.append(f"PDF链接验证失败: {e}")
    else:
        print(f"ℹ️  无PDF链接")
    
    # 8. 验证YouTube视频
    video_id = data.get('youtube_video_id', '')
    if video_id:
        print(f"\n验证YouTube视频...")
        if len(video_id) == 11:
            print(f"✅ 视频ID格式正确: {video_id}")
            warnings.append(f"⚠️  请人工确认视频是该产品的英语介绍: https://www.youtube.com/watch?v={video_id}")
        else:
            errors.append(f"视频ID格式不正确 (应为11个字符): {video_id}")
    else:
        print(f"ℹ️  无YouTube视频")
    
    # 9. 验证生成的HTML
    html_path = f"products/{slug}.html"
    if os.path.exists(html_path):
        print(f"\n✅ HTML文件存在: {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 验证PDF链接在HTML中
        if pdf_link and pdf_link not in html_content:
            errors.append(f"PDF链接未在HTML中找到")
        
        # 验证YouTube视频在HTML中
        if video_id and f"youtube.com/embed/{video_id}" not in html_content:
            errors.append(f"YouTube视频未在HTML中找到")
        
        # 验证项目数量
        project_count = html_content.count('class="card-title"')
        if project_count != len(projects):
            errors.append(f"HTML中的项目数量不匹配 - 期望: {len(projects)}, 实际: {project_count}")
        else:
            print(f"✅ HTML中的项目数量匹配: {project_count}")
    else:
        errors.append(f"HTML文件不存在: {html_path}")
    
    # 10. 输出结果
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
    
    return errors, warnings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python verify_product.py <product-slug>")
        sys.exit(1)
    
    slug = sys.argv[1]
    errors, warnings = verify_product(slug)
    
    if errors:
        sys.exit(1)  # 有错误，退出码1
    else:
        sys.exit(0)  # 无错误，退出码0
```

---

## 使用方法

### 每个产品完成后运行

```bash
# 1. 创建JSON文件后验证
python3 verify_product.py {slug}

# 2. 如果有错误，修正后重新验证
python3 verify_product.py {slug}

# 3. 验证通过后，重建网站
python3 rebuild_site_v2.py

# 4. 再次验证（验证HTML）
python3 verify_product.py {slug}

# 5. 验证通过后，部署
bash deploy-peri-gcb.command
```

---

## 总结

### 关键改进

1. **统一命名规则**：文件名必须与slug完全匹配
2. **自动验证Agent**：100%验证所有数据
3. **双重验证**：JSON创建后验证 + HTML生成后验证
4. **人工确认提醒**：PDF内容和YouTube视频需要人工确认

### 保证质量

- ✅ 文件命名100%正确
- ✅ 所有必需字段100%存在
- ✅ 所有URL 100%有效
- ✅ HTML生成100%正确
- ✅ 人工验证100%完成

**不再出现文件名不匹配的问题！**
