# UNO产品问题分析报告

## 问题描述
用户报告："pdf 链接不对"，具体指UNO产品的PDF链接"不是uno的pdf"

## 当前状态

### UNO产品的PDF链接
- **当前链接**: `https://www.peri.it/dam/jcr:6ace1692-e75a-4192-8a98-4080f40e98dd/uno-cassaforma-per-pareti-brochure-en.pdf`
- **来源**: `uno-formwork-system_complete.json` 文件中的 `pdf_link` 字段
- **链接状态**: HTTP 200，有效的PDF文件
- **问题**: PDF内容不是UNO产品的手册（用户确认）

## 问题根源分析

### 1. PDF链接来源检查

#### cn.peri.com（中文官网）
```bash
curl -s "https://cn.peri.com/products/uno-formwork-system.html"
```
**结果**: 页面上没有直接的PDF下载链接

#### www.peri.com/en（英文官网）
```bash
curl -s "https://www.peri.com/en/products/uno-formwork-system.html"
```
**结果**: 页面上没有直接的PDF下载链接

#### 当前错误链接分析
- 链接域名: `www.peri.it` (意大利PERI网站)
- 文件名: `uno-cassaforma-per-pareti-brochure-en.pdf`
- 问题: 这个PDF可能是意大利网站上的某个产品手册，但不是UNO产品的

### 2. 对比其他已完成产品的PDF来源

```bash
grep '"pdf_link"' *_complete.json
```

| 产品 | PDF链接域名 | 状态 |
|------|------------|------|
| gridflex | www.peri.com.au | ✅ 用户已验证 |
| skydeck | www.peri.id | ✅ 用户已验证 |
| multiflex | www.peri.id | ✅ 用户已验证 |
| maximo | www.peri.id | ✅ 用户已验证 |
| handset-alpha | www.peri.co.za | ✅ 用户已验证 |
| vario-gt-24 | www.peri.id | ✅ 用户已验证 |
| domino | "" (空) | ✅ 用户已验证 |
| **uno** | **www.peri.it** | ❌ **错误** |

**发现**: 
- 其他产品的PDF主要来自 peri.id (印尼) 或 peri.com.au (澳大利亚)
- UNO的PDF来自 peri.it (意大利)，这是唯一一个来自意大利网站的
- 这个链接很可能是错误的

### 3. 正确的工作流程（根据CONTEXT_SUMMARY.md）

#### 标准PDF获取流程：
1. 首先检查 cn.peri.com 产品页面
2. 如果没有，检查 www.peri.com/en 产品页面
3. 如果没有，检查其他区域网站（peri.id, peri.com.au等）
4. **关键**: 必须验证PDF内容确实是该产品的手册

#### UNO制作时的问题：
- ❌ 没有在cn.peri.com找到PDF（正常，因为确实没有）
- ❌ 没有在www.peri.com/en找到PDF（正常，因为确实没有）
- ❌ **错误**: 从peri.it找到了一个PDF，但没有验证内容是否正确
- ❌ **错误**: 直接使用了这个错误的PDF链接

## 代码问题分析

### rebuild_site_v2.py 的PDF加载逻辑

```python
# 当前逻辑（第579-594行）
pdf_url = None
complete_json_path = os.path.join(BASE, f'{slug}_complete.json')
if os.path.exists(complete_json_path):
    try:
        with open(complete_json_path, 'r', encoding='utf-8') as f:
            product_data = json.load(f)
            pdf_url = product_data.get('pdf_link')  # 获取PDF链接
    except:
        pass

# Fallback到product_pdf_links.json，然后cn_url
if not pdf_url:
    pdf_url = PDF_LINKS.get(slug, cn_url)
```

**代码本身没有问题**，问题在于：
- `uno-formwork-system_complete.json` 中存储的 `pdf_link` 值是错误的
- 代码正确读取并使用了这个错误的值

### product_pdf_links.json 中的UNO

```json
"uno-formwork-system": "https://www.peri.com/en/products/uno-formwork-system.html#downloads"
```

这是一个fallback链接，指向产品页面的下载区域，不是直接PDF链接。

## 根本原因总结

1. **数据收集错误**: 在创建 `uno-formwork-system_complete.json` 时，填入了错误的PDF链接
2. **验证缺失**: 没有验证PDF内容是否真的是UNO产品的手册
3. **来源异常**: UNO的PDF来自peri.it（意大利），而其他产品都来自peri.id或peri.com.au

## 解决方案

### 立即行动：
1. 确认UNO产品是否有正确的PDF手册
2. 如果有，获取正确的PDF链接并更新 `uno-formwork-system_complete.json`
3. 如果没有，将 `pdf_link` 设为空字符串 `""`，让页面使用fallback链接或隐藏PDF按钮

### 未来预防措施：

#### 必须环节（每个产品都要做）：
1. ✅ 从cn.peri.com提取产品信息
2. ✅ 提取并验证图片URL（必须返回200）
3. ✅ 提取项目案例链接
4. ✅ 逐个提取项目信息
5. ✅ 搜索YouTube视频
6. ✅ **验证PDF链接内容**（新增：必须打开PDF确认内容正确）
7. ✅ 创建完整JSON文件
8. ✅ 生成产品页面
9. ✅ 最终验证

#### PDF链接验证清单：
- [ ] PDF链接返回HTTP 200
- [ ] PDF文件可以打开
- [ ] **PDF内容确实是该产品的手册**（关键！）
- [ ] PDF语言合适（优先英语或中文）
- [ ] 如果找不到正确的PDF，使用空字符串 `""`

## 需要用户确认

**问题**: UNO产品的正确PDF链接是什么？

**选项**:
1. 用户提供正确的UNO PDF链接
2. UNO产品没有PDF手册，应该使用空字符串 `""`
3. 需要我帮助搜索正确的UNO PDF链接

---

**重要原则**（已理解）：
- ✅ 已经用户检查过的产品 = 都是对的
- ✅ 未经用户允许，不能修改任何已完成的产品
- ✅ 只修改用户明确指出有问题的产品
