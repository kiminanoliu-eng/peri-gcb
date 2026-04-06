# 错误预防检查清单

## 文档说明

本文档提供详细的检查清单，用于在处理每个产品时预防错误。每个检查点都包含具体的验证命令和步骤。

**使用方法**: 
- 在开始处理新产品前，阅读"产品处理前检查清单"
- 在每个阶段完成后，执行对应的"阶段验证清单"
- 在部署前，完成"最终验证清单"

---

## 产品处理前检查清单

### ✅ 检查点 0.1: 确认产品slug

**目的**: 避免文件命名错误

**操作步骤**:
```bash
cd /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站

# 1. 询问用户要处理的产品名称
# 2. 在products_v2.json中搜索该产品
grep -i "产品名称" products_v2.json | grep "slug"

# 3. 记录准确的slug（包括所有连字符和完整名称）
```

**验证标准**:
- [ ] 已从products_v2.json确认slug
- [ ] slug包含所有连字符（不是下划线）
- [ ] slug是完整名称（不是简短版本）
- [ ] 已记录slug，准备用于文件命名

**常见错误**:
- ❌ 使用下划线替代连字符: `handset_alpha` vs `handset-alpha`
- ❌ 使用简短版本: `vario_gt24` vs `vario-gt-24-girder-wall-formwork`

---

### ✅ 检查点 0.2: 准备工作环境

**操作步骤**:
```bash
# 1. 进入工作目录
cd /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站

# 2. 确认必要文件存在
ls -la products_v2.json rebuild_site_v2.py deploy-peri-gcb.command

# 3. 清理临时文件
rm -f temp.html project.html temp.pdf 2>/dev/null
```

**验证标准**:
- [ ] 工作目录正确
- [ ] 必要文件存在
- [ ] 临时文件已清理

---

## 阶段1: 数据收集验证清单

### ✅ 检查点 1.1: 产品页面HTML

**操作步骤**:
```bash
# 获取产品页面HTML
curl -s "https://cn.peri.com/products/{slug}.html" > temp.html

# 验证文件大小
ls -lh temp.html

# 验证包含产品名称
grep -i "产品名称" temp.html | head -3
```

**验证标准**:
- [ ] temp.html文件大小 > 10KB
- [ ] 文件包含产品名称
- [ ] 文件不是404错误页面

**如果失败**: 检查slug是否正确，或产品页面是否存在

---

### ✅ 检查点 1.2: 产品缩略图

**操作步骤**:
```bash
# 提取og:image
grep 'og:image' temp.html | grep -o 'content="[^"]*"'

# 验证图片URL（替换{IMAGE_URL}为实际URL）
curl -I {IMAGE_URL} | head -5
```

**验证标准**:
- [ ] 找到og:image标签
- [ ] 图片URL返回HTTP 200
- [ ] Content-Type是image/*

**如果失败**: 尝试查找其他图片标签，或使用占位图片

---

## 阶段2: 项目案例验证清单

### ✅ 检查点 2.1: 提取项目链接

**目的**: 避免使用错误的项目案例

**操作步骤**:
```bash
# 方法1: 提取所有项目链接
grep -o 'href="/projects/[^"]*"' temp.html

# 方法2: 检查项目卡片数量
grep -c "project-teasers__item" temp.html

# 方法3: 提取项目详细信息
grep -A 20 "project-teasers__item-regular-list-headline" temp.html
```

**验证标准**:
- [ ] 项目链接确实在temp.html中（不是从其他来源）
- [ ] 项目数量与页面显示一致
- [ ] 每个项目链接格式正确: `/projects/xxx.html`

**关键原则**:
- ✅ 必须从temp.html（产品页面HTML）提取
- ❌ 不使用WebFetch（可能返回不完整结果）
- ❌ 不从china_projects.json随机选择
- ❌ 不使用其他产品的项目

**如果没有项目**:
```bash
# 确认HTML中确实没有项目
grep -i "项目" temp.html
grep -i "project" temp.html

# 如果确认没有项目，使用空数组 []
```

---

### ✅ 检查点 2.2: 验证每个项目

**操作步骤**（对每个项目链接）:
```bash
# 获取项目页面
curl -s "https://cn.peri.com{PROJECT_URL}" > project.html

# 提取项目名称
grep -o '<h1[^>]*>[^<]*</h1>' project.html

# 提取位置
grep -o 'location[^>]*>[^<]*</span>' project.html

# 提取图片
grep -o 'og:image.*content="[^"]*"' project.html

# 验证项目图片
curl -I {PROJECT_IMAGE_URL} | head -5
```

**验证标准**（每个项目）:
- [ ] 项目名称提取成功
- [ ] 项目位置提取成功
- [ ] 项目描述提到了该产品
- [ ] 项目图片URL返回HTTP 200
- [ ] 项目链接可访问

**如果失败**: 跳过该项目，继续下一个

---

## 阶段3: YouTube视频验证清单

### ✅ 检查点 3.1: 搜索YouTube视频

**目的**: 找到正确的英语产品介绍视频

**操作步骤**（人工操作）:
```
1. 访问 https://www.youtube.com/@perigroup
2. 在频道内搜索框输入: {产品名称} formwork
3. 不要在YouTube主页搜索！
```

**验证标准**:
- [ ] 在PERI官方频道内搜索（不是YouTube主页）
- [ ] 尝试了多个关键词组合
- [ ] 筛选了搜索结果

**关键原则**:
- ✅ 必须在PERI频道内搜索
- ❌ 不在YouTube主页搜索
- ❌ 不使用德语培训视频

---

### ✅ 检查点 3.2: 验证视频质量

**筛选条件**:
- [ ] 语言: 英语（不是德语、西班牙语等）
- [ ] 时长: ≤ 10分钟
- [ ] 内容: 产品介绍/演示（不是项目案例视频）
- [ ] 来源: PERI官方频道
- [ ] 发布时间: 优先最新的

**提取视频ID**:
```
从URL提取11位视频ID:
https://www.youtube.com/watch?v=CgOEI3YtG_E → CgOEI3YtG_E
```

**验证标准**:
- [ ] 视频ID长度为11个字符
- [ ] 视频时长 ≤ 10分钟
- [ ] 视频语言是英语
- [ ] 视频内容是该产品的介绍

**如果找不到合适的视频**: 使用空字符串 `""`

---

## 阶段4: PDF链接验证清单（最关键）

### ✅ 检查点 4.1: 搜索PDF链接

**目的**: 找到正确的产品手册PDF

**操作步骤**（按优先级）:
```bash
# 优先级1: cn.peri.com
curl -s "https://cn.peri.com/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 优先级2: www.peri.com/en
curl -s "https://www.peri.com/en/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 优先级3: peri.id (印尼)
curl -s "https://www.peri.id/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 优先级4: peri.com.au (澳大利亚)
curl -s "https://www.peri.com.au/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 优先级5: peri.co.za (南非)
curl -s "https://www.peri.co.za/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'
```

**验证标准**:
- [ ] 找到至少一个PDF链接
- [ ] PDF链接来自PERI官方网站
- [ ] 优先使用cn.peri.com或peri.com/en的PDF

---

### ✅ 检查点 4.2: 验证PDF链接（三步验证法）

**目的**: 避免使用错误的PDF（UNO的教训）

**步骤1: 验证链接有效**
```bash
curl -I {PDF_URL} | head -10
```
- [ ] 返回HTTP 200
- [ ] 不是404或其他错误

**步骤2: 验证是PDF文件**
```bash
curl -I {PDF_URL} | grep "Content-Type"
```
- [ ] Content-Type是application/pdf
- [ ] 不是text/html或其他类型

**步骤3: 验证内容正确（最重要！）**
```bash
# 下载PDF
curl -o temp.pdf {PDF_URL}

# 人工检查（必须手动完成）:
# 1. 打开temp.pdf文件
# 2. 确认PDF内容确实是该产品的手册
# 3. 不是其他产品的手册
# 4. 不是意大利语或其他不相关的PDF
```

**验证标准**:
- [ ] PDF可以打开
- [ ] **PDF内容确实是该产品的手册**（人工确认）
- [ ] PDF语言合适（优先英语或中文）
- [ ] PDF不是其他产品的手册
- [ ] PDF来自PERI官方网站

**关键原则**:
- ✅ 宁可没有PDF（使用空字符串 `""`），也不要使用错误的PDF
- ❌ 不要只检查HTTP 200就使用
- ❌ 不要使用来自不确定来源的PDF
- ⚠️ 如果PDF来自peri.it等不常见的区域网站，必须特别仔细验证内容

**如果找不到正确的PDF**: 使用空字符串 `""`

---

## 阶段5: 创建JSON文件验证清单

### ✅ 检查点 5.1: 文件命名

**目的**: 避免文件名与slug不匹配

**操作步骤**:
```bash
# 1. 确认slug（从products_v2.json）
SLUG="{从products_v2.json确认的slug}"

# 2. 构建文件名
FILENAME="${SLUG}_complete.json"

# 3. 验证文件名格式
echo "文件名: $FILENAME"
echo "格式正确: ${SLUG}_complete.json"
```

**验证标准**:
- [ ] 文件名格式: `{slug}_complete.json`
- [ ] slug与products_v2.json完全匹配
- [ ] 保留所有连字符 `-`（不是下划线 `_`）
- [ ] 使用完整slug（不是简短版本）

**示例**:
```
✅ 正确: gridflex-deckenschalung_complete.json
❌ 错误: gridflex_complete.json (缺少完整slug)
❌ 错误: gridflex-deckenschalung.json (缺少_complete)
```

---

### ✅ 检查点 5.2: JSON结构完整性

**验证标准**:
- [ ] 包含所有必需字段: slug, name_zh, category, subcategory, cn_url, image, description, projects, pdf_link, youtube_video_id
- [ ] slug字段与文件名匹配
- [ ] description包含7种语言: zh, en, es, de, pt, sr, hu
- [ ] projects是数组（可以为空 `[]`）
- [ ] pdf_link是字符串（可以为空 `""`）
- [ ] youtube_video_id是字符串（可以为空 `""`）

**验证命令**:
```bash
# 验证JSON格式
python3 -c "import json; json.load(open('${FILENAME}'))" && echo "✅ JSON格式正确" || echo "❌ JSON格式错误"

# 验证必需字段
python3 -c "
import json
data = json.load(open('${FILENAME}'))
required = ['slug', 'name_zh', 'category', 'cn_url', 'image', 'description', 'projects', 'pdf_link', 'youtube_video_id']
missing = [f for f in required if f not in data]
if missing:
    print(f'❌ 缺少字段: {missing}')
else:
    print('✅ 所有必需字段存在')
"
```

---

## 阶段6: 生成和验证清单

### ✅ 检查点 6.1: 重建网站

**操作步骤**:
```bash
cd /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站
python3 rebuild_site_v2.py
```

**验证标准**:
- [ ] 显示"✅ Done!"
- [ ] 没有错误信息
- [ ] 没有Python异常

**如果失败**: 检查JSON文件格式和内容

---

### ✅ 检查点 6.2: 验证生成的HTML

**操作步骤**:
```bash
# 检查产品页面是否生成
ls -lh products/{slug}.html

# 检查PDF链接（如果有）
if [ -n "$PDF_LINK" ]; then
    grep 'btn btn-yellow' products/{slug}.html | grep -o 'href="[^"]*"'
fi

# 检查YouTube视频（如果有）
if [ -n "$VIDEO_ID" ]; then
    grep 'youtube.com/embed' products/{slug}.html
fi

# 检查项目案例数量
PROJECT_COUNT=$(grep -c 'class="card-title"' products/{slug}.html)
echo "HTML中的项目数量: $PROJECT_COUNT"
```

**验证标准**:
- [ ] products/{slug}.html文件存在
- [ ] 文件大小 > 10KB
- [ ] PDF链接正确（如果有）
- [ ] YouTube视频嵌入正确（如果有）
- [ ] 项目案例数量与JSON匹配

---

### ✅ 检查点 6.3: 运行自动验证脚本

**操作步骤**:
```bash
# 运行验证脚本
python3 verify_product.py {slug}
```

**验证标准**:
- [ ] 所有自动验证通过
- [ ] 没有错误信息
- [ ] 警告信息已人工确认

**如果失败**: 根据错误信息修正问题，重新验证

---

## 阶段7: 部署前最终验证清单

### ✅ 检查点 7.1: 最终数据检查

**操作步骤**:
```bash
# 1. 确认文件名正确
ls -la {slug}_complete.json

# 2. 确认HTML生成正确
ls -la products/{slug}.html

# 3. 确认所有URL有效
python3 verify_product.py {slug}
```

**验证标准**:
- [ ] JSON文件名与slug匹配
- [ ] HTML文件存在
- [ ] 所有验证通过

---

### ✅ 检查点 7.2: 人工最终确认

**验证清单**:
- [ ] 产品缩略图正确
- [ ] 7种语言翻译完整
- [ ] 项目案例确实属于该产品
- [ ] 项目案例数量正确
- [ ] PDF链接内容正确（已打开PDF确认）
- [ ] YouTube视频内容正确（已观看视频确认）
- [ ] 所有链接都有效

**如果有任何疑问**: 立即询问用户，不要假设

---

## 阶段8: 部署和在线验证清单

### ✅ 检查点 8.1: 部署

**操作步骤**:
```bash
bash deploy-peri-gcb.command
```

**验证标准**:
- [ ] Git提交成功
- [ ] Git推送成功
- [ ] 没有错误信息

---

### ✅ 检查点 8.2: 等待构建完成

**操作步骤**:
- 等待1-2分钟
- GitHub Pages构建完成

---

### ✅ 检查点 8.3: 在线验证

**操作步骤**:
访问 `https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html`

**验证标准**:
- [ ] 产品页面在线可访问
- [ ] 图片加载正常
- [ ] PDF链接可点击（如果有）
- [ ] YouTube视频可播放（如果有）
- [ ] 项目案例链接可访问
- [ ] 留言表单显示正常

---

## 常见错误快速检查命令

### 文件命名检查
```bash
# 检查文件名是否与slug匹配
SLUG="产品slug"
EXPECTED="${SLUG}_complete.json"
if [ -f "$EXPECTED" ]; then
    echo "✅ 文件名正确: $EXPECTED"
else
    echo "❌ 文件不存在: $EXPECTED"
    echo "当前目录中的complete文件:"
    ls *_complete.json | grep -i "${SLUG:0:10}"
fi
```

### 项目案例来源检查
```bash
# 确认项目确实在产品页面上
curl -s "https://cn.peri.com/products/{slug}.html" | grep -o 'href="/projects/[^"]*"'
```

### PDF内容检查
```bash
# 下载并打开PDF
curl -o temp.pdf {PDF_URL}
open temp.pdf  # macOS
# 人工确认内容是该产品的手册
```

### YouTube视频检查
```bash
# 验证视频ID格式
VIDEO_ID="视频ID"
if [ ${#VIDEO_ID} -eq 11 ]; then
    echo "✅ 视频ID格式正确"
    echo "视频链接: https://www.youtube.com/watch?v=$VIDEO_ID"
else
    echo "❌ 视频ID格式错误（应为11个字符）"
fi
```

---

## 工作流程总结

```
开始
  ↓
[检查点 0.1] 确认产品slug
  ↓
[检查点 0.2] 准备工作环境
  ↓
[检查点 1.1] 获取产品页面HTML
  ↓
[检查点 1.2] 提取产品缩略图
  ↓
[检查点 2.1] 提取项目链接
  ↓
[检查点 2.2] 验证每个项目
  ↓
[检查点 3.1] 搜索YouTube视频
  ↓
[检查点 3.2] 验证视频质量
  ↓
[检查点 4.1] 搜索PDF链接
  ↓
[检查点 4.2] 验证PDF内容（三步验证法）
  ↓
[检查点 5.1] 创建JSON文件（正确命名）
  ↓
[检查点 5.2] 验证JSON结构
  ↓
[检查点 6.1] 重建网站
  ↓
[检查点 6.2] 验证生成的HTML
  ↓
[检查点 6.3] 运行自动验证脚本
  ↓
[检查点 7.1] 最终数据检查
  ↓
[检查点 7.2] 人工最终确认
  ↓
[检查点 8.1] 部署
  ↓
[检查点 8.2] 等待构建完成
  ↓
[检查点 8.3] 在线验证
  ↓
用户最终验证
  ↓
完成
```

---

**记住**: 每个检查点都很重要，不要跳过任何一个！
