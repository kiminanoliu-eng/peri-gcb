# 下一个产品的正确处理流程

## 从UNO问题中学到的核心教训

### 绝对禁止的行为
1. ❌ **不能擅自修改其他产品** - 即使发现"问题"或"不一致"
2. ❌ **不能擅自修改代码** - 除非用户明确要求
3. ❌ **不能"优化"已校对的产品** - 用户校对过的 = 正确的
4. ❌ **不能假设问题范围** - 用户说哪个产品有问题，就只处理那个产品

### 必须遵守的原则
1. ✅ **只做用户明确要求的事情**
2. ✅ **一个产品一个产品地做**
3. ✅ **每个环节都要验证内容正确性，不只是链接有效性**
4. ✅ **有疑问立即询问用户，不要自作主张**

---

## 下一个产品的完整处理流程

### 阶段1: 数据收集（从cn.peri.com）

#### 1.1 提取产品基本信息
```bash
# 获取产品页面
curl -s "https://cn.peri.com/products/{slug}.html" > temp.html

# 提取图片URL
grep 'og:image' temp.html
# 验证图片有效性
curl -I {image_url}  # 必须返回200
```

#### 1.2 提取项目案例链接
```bash
# 从产品页面提取项目链接
grep -o 'href="/projects/[^"]*"' temp.html
```

**关键验证点**：
- ✅ 确认提取到的项目链接确实在产品页面上
- ✅ 不要使用随机项目或其他产品的项目
- ❌ 不要从china_projects.json随机选择
- ❌ 不要使用港珠澳大桥等不相关的项目

#### 1.3 逐个提取项目信息
```bash
for project_url in project_urls:
    curl -s "https://cn.peri.com{project_url}" > project.html
    # 提取: name, location, description, image, link
```

**验证清单**：
- [ ] 项目名称正确
- [ ] 项目位置正确
- [ ] 项目描述提到了该产品
- [ ] 项目图片URL有效（HTTP 200）
- [ ] 项目确实使用了该产品

---

### 阶段2: YouTube视频搜索

```
1. 访问 https://www.youtube.com/@perigroup
2. 在频道内搜索: {product_name} formwork
3. 筛选条件:
   - 语言: 英语
   - 时长: 10分钟内
   - 内容: 产品介绍（不是项目案例）
4. 提取视频ID
5. 验证视频确实是该产品的介绍
```

**验证清单**：
- [ ] 视频标题包含产品名称
- [ ] 视频内容是产品介绍
- [ ] 视频语言是英语
- [ ] 视频时长合适（不要太长）

---

### 阶段3: PDF链接查找

#### 3.1 查找顺序
```bash
# 1. 首先检查cn.peri.com
curl -s "https://cn.peri.com/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 2. 如果没有，检查www.peri.com/en
curl -s "https://www.peri.com/en/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 3. 如果没有，检查其他区域网站
# peri.id (印尼)
# peri.com.au (澳大利亚)
# peri.co.za (南非)
```

#### 3.2 PDF验证（最关键！）
```bash
# 验证1: 链接有效
curl -I {pdf_url}  # 必须返回200

# 验证2: 是PDF文件
curl -I {pdf_url} | grep "Content-Type: application/pdf"

# 验证3: 内容正确（最重要！）
# 下载PDF并打开查看
curl -o temp.pdf {pdf_url}
# 人工检查: PDF内容确实是该产品的手册
```

**PDF验证清单**：
- [ ] PDF链接返回HTTP 200
- [ ] Content-Type是application/pdf
- [ ] **PDF内容确实是该产品的手册**（打开PDF人工确认）
- [ ] PDF语言合适（优先英语或中文）
- [ ] PDF不是其他产品的手册
- [ ] 如果找不到正确的PDF，使用空字符串 `""`

**重要**：宁可没有PDF（使用空字符串），也不要使用错误的PDF！

---

### 阶段4: 创建完整JSON文件

#### 4.1 文件命名规则
```
文件名格式: {slug}_complete.json
```

**关键**：
- 文件名必须与products_v2.json中的slug**完全匹配**
- 使用连字符 `-` 而不是下划线 `_`（如果slug中有连字符）
- 例如：
  - slug是 `gridflex-deckenschalung` → 文件名是 `gridflex-deckenschalung_complete.json`
  - slug是 `uno-formwork-system` → 文件名是 `uno-formwork-system_complete.json`

#### 4.2 JSON结构
```json
{
  "slug": "product-slug",
  "name_zh": "产品中文名",
  "category": "分类",
  "subcategory": "子分类",
  "cn_url": "https://cn.peri.com/products/{slug}.html",
  "image": "验证过的图片URL",
  "description": {
    "zh": "...",
    "en": "...",
    "es": "...",
    "de": "...",
    "pt": "...",
    "sr": "...",
    "hu": "..."
  },
  "projects": [
    {
      "name": "项目名称",
      "location": "位置",
      "description": "描述",
      "image": "项目图片URL",
      "link": "项目链接"
    }
  ],
  "pdf_link": "PDF URL或空字符串",
  "youtube_video_id": "视频ID或空字符串"
}
```

---

### 阶段5: 生成和验证

#### 5.1 重建网站
```bash
cd /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站
python3 rebuild_site_v2.py
```

#### 5.2 验证生成的HTML
```bash
# 检查产品页面是否生成
ls products/{slug}.html

# 检查PDF链接
grep 'btn btn-yellow' products/{slug}.html | grep -o 'href="[^"]*"'

# 检查YouTube视频
grep 'youtube.com/embed' products/{slug}.html

# 检查项目案例
grep 'card-title' products/{slug}.html
```

#### 5.3 最终验证清单
- [ ] 产品页面生成成功
- [ ] 图片显示正确
- [ ] PDF链接正确（如果有）
- [ ] YouTube视频正确（如果有）
- [ ] 项目案例正确（数量和内容）
- [ ] 所有链接都有效

---

### 阶段6: 部署

```bash
bash deploy-peri-gcb.command
```

等待1-2分钟后访问网站验证。

---

## 关键检查点总结

### 项目案例（最容易出错）
1. ✅ 必须从产品页面提取项目链接
2. ✅ 验证项目确实使用了该产品
3. ❌ 不要使用随机项目
4. ❌ 不要使用其他产品的项目
5. ❌ 不要使用china_projects.json中的随机项目

### PDF链接（UNO的教训）
1. ✅ 验证链接有效（HTTP 200）
2. ✅ **验证内容正确**（打开PDF确认）
3. ❌ 不要只检查链接有效就使用
4. ❌ 不要使用其他产品的PDF
5. ✅ 找不到正确的PDF就用空字符串 `""`

### 文件命名
1. ✅ 文件名必须与slug完全匹配
2. ✅ 格式：`{slug}_complete.json`
3. ❌ 不要使用简短版本或下划线替代连字符

### 行为准则
1. ✅ 只做用户要求的产品
2. ❌ 不擅自修改其他产品
3. ❌ 不擅自修改代码
4. ✅ 有疑问立即询问用户

---

## 下一个产品开始前的确认

在开始下一个产品之前，我会：

1. **询问用户**：下一个要做的产品是什么？
2. **确认slug**：从products_v2.json中确认产品的准确slug
3. **按流程执行**：严格按照上述流程，不跳过任何验证步骤
4. **遇到问题立即询问**：不自作主张

---

## 当前待解决的问题

### UNO的PDF链接
- 当前链接：`https://www.peri.it/dam/.../uno-cassaforma-per-pareti-brochure-en.pdf`
- 问题：内容不是UNO产品的手册
- 需要：用户提供正确的PDF链接，或确认UNO没有PDF

**等待用户指示下一步行动。**
