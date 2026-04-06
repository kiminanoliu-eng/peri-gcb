# 产品页面生成 - 完整工作流程和经验教训

## 目录
1. [6步工作流程](#6步工作流程)
2. [PDF提取详细步骤](#pdf提取详细步骤)
3. [项目示例提取详细步骤](#项目示例提取详细步骤)
4. [YouTube视频提取详细步骤](#youtube视频提取详细步骤)
5. [文件命名和验证](#文件命名和验证)
6. [常见错误和解决方法](#常见错误和解决方法)
7. [核心原则和教训](#核心原则和教训)
8. [命令速查表](#命令速查表)

---

## 6步工作流程

### 阶段0: 开始前确认
1. 询问用户：下一个要做的产品是什么？
2. 从products_v2.json确认产品的准确slug
3. 记录完整slug（包括所有连字符）

### 阶段1: 提取产品基本信息
```bash
# 获取产品页面HTML
curl -s "https://cn.peri.com/products/{slug}.html" > temp.html

# 提取产品缩略图URL
grep 'og:image' temp.html

# 验证图片有效性
curl -I {image_url}  # 必须返回200
```

### 阶段2: 提取项目案例（见详细步骤）

### 阶段3: 搜索YouTube视频（见详细步骤）

### 阶段4: 查找PDF链接（见详细步骤）

### 阶段5: 创建JSON文件
- 文件名：`{slug}_complete.json`（完全匹配slug）
- 包含：slug、name_zh、category、description（7种语言）、projects、pdf_link、youtube_video_id

### 阶段6: 生成和部署
```bash
# 生成页面
python3 rebuild_site_v2.py

# 部署
bash deploy-peri-gcb.command

# 等待2分钟后验证
sleep 120
curl -I "https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html"
```

---

## PDF提取详细步骤

### 方法1: PERI UK网站直接提取（推荐，最有效）

**为什么推荐UK网站**:
- PDF链接格式统一：`/.rest/downloads/{ID}`
- 成功率高
- PDF质量好（官方文档）

**步骤**:
```bash
# 1. 访问UK网站产品页面
curl -s "https://www.peri.ltd.uk/products/{slug}.html" > uk_page.html

# 2. 提取下载链接ID
download_id=$(grep -o '/.rest/downloads/[0-9]*' uk_page.html | head -1)

# 3. 构建完整PDF URL
pdf_url="https://www.peri.ltd.uk${download_id}"

# 4. 验证
curl -I "$pdf_url"
```

**⚠️ 关键：Slug变体尝试策略**

**问题**: 中国网站和UK网站的产品slug可能不一致

**解决方案**: 必须尝试多个slug变体，按以下顺序：

1. **原始slug** - 直接使用中国网站的slug
2. **英文翻译变体** - 将德语/其他语言翻译成英文
   - `grv-rundschalung` → `grv-circular-formwork` (rundschalung=circular formwork)
   - `quattro-saeulenschalung` → `quattro-column-formwork`
3. **移除后缀** - 去掉产品类型后缀
   - `prokit-ep-110-fall-protection` → `prokit`
   - `peri-up-easy-frame-scaffolding` → `peri-up-easy-scaffolding`
4. **简化版本** - 只保留核心产品名
   - `domino-panel-formwork` → `domino`
5. **添加常见后缀** - 尝试添加UK网站常用后缀
   - 添加 `-scaffolding`
   - 添加 `-formwork`

**实际案例**:
- PROKIT EP 110:
  - ❌ `prokit-ep-110-fall-protection` (中国slug)
  - ✅ `prokit` (简化版本)
  
- PERI UP Easy:
  - ❌ `peri-up-easy-frame-scaffolding` (中国slug)
  - ✅ `peri-up-easy-scaffolding` (移除"frame")

- GRV:
  - ❌ `grv-rundschalung` (德语slug)
  - ❌ `grv` (简化版本)
  - ✅ `grv-circular-formwork` (英文翻译)

**自动尝试多个变体的脚本**:
```bash
# 定义slug变体数组
original_slug="your-product-slug"
slugs=(
  "$original_slug"                    # 原始slug
  "${original_slug%-*}"               # 移除最后一个词
  "${original_slug%%-*}"              # 只保留第一个词
  "${original_slug}-formwork"         # 添加formwork
  "${original_slug}-scaffolding"      # 添加scaffolding
)

# 尝试每个变体
for slug in "${slugs[@]}"; do
  echo "尝试: $slug"
  result=$(curl -s "https://www.peri.ltd.uk/products/$slug.html" | grep -o '/.rest/downloads/[0-9]*' | head -1)
  if [ -n "$result" ]; then
    echo "✅ 找到: https://www.peri.ltd.uk$result"
    pdf_url="https://www.peri.ltd.uk$result"
    break
  fi
done

if [ -z "$result" ]; then
  echo "❌ UK网站未找到，尝试方法2"
fi
```

### 方法2: Google搜索（备选，简单有效）

**搜索公式**:
```
peri {产品英文名} pdf
```

**为什么这个方法有效**:
1. Google索引了PERI所有区域网站的PDF
2. 搜索结果直接指向产品手册
3. 覆盖全球所有PERI网站

**示例**:
- LIWA: `peri liwa pdf`
  - 结果: https://www.peri.co.th/dam/jcr:bf8b3cd6-eeb5-4529-bf7e-c1d5148f8a36/liwa.pdf
  - 状态: ✅ 有效 (HTTP 200, 4.8MB)

**操作步骤**:
1. 在Google搜索：`peri {产品英文名} pdf`
2. 查找来自PERI官方网站的PDF链接（peri.com, peri.co.th, peri.id等）
3. 复制PDF直接链接
4. 验证链接（见下方三步验证法）

**⚠️ 注意**: 
- 避免使用Scribd、ilovepdf等第三方网站的PDF
- 只使用PERI官方网站的PDF

### 方法3: 其他区域网站（如果方法1和2都失败）

**搜索顺序**:
```bash
# 优先级1: cn.peri.com
curl -s "https://cn.peri.com/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 优先级2: www.peri.com/en
curl -s "https://www.peri.com/en/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 优先级3: peri.id (印尼)
curl -s "https://www.peri.id/en/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 优先级4: peri.com.au (澳大利亚)
curl -s "https://www.peri.com.au/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 优先级5: peri.co.za (南非)
curl -s "https://www.peri.co.za/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 优先级6: peri.de (德国)
curl -s "https://www.peri.de/produkte/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 优先级7: peri.co.th (泰国)
curl -s "https://www.peri.co.th/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'
```

### PDF验证三步法（最关键！）

**步骤1: 验证链接有效**
```bash
curl -I {pdf_url}
# 必须返回: HTTP/2 200
```

**步骤2: 验证文件类型**
```bash
curl -I {pdf_url} | grep "Content-Type: application/pdf"
# 必须包含: Content-Type: application/pdf
```

**步骤3: 验证内容正确（最重要！不能跳过！）**
```bash
# 下载PDF
curl -o temp.pdf {pdf_url}

# 打开PDF（macOS）
open temp.pdf

# 人工检查（必须手动完成）:
# 1. PDF标题是否包含产品名称？
# 2. PDF内容是否是该产品的技术规格/手册？
# 3. PDF是否是PERI官方文档？
# 4. PDF不是其他产品的手册？
# 5. PDF语言是否合适（优先英语或中文）？
```

### PDF验证清单
- [ ] PDF链接返回HTTP 200
- [ ] Content-Type是application/pdf
- [ ] **打开PDF，确认是该产品的手册**（人工确认）
- [ ] PDF语言合适（优先英语或中文）
- [ ] PDF不是其他产品的手册
- [ ] PDF来自PERI官方网站

### 重要原则
- ✅ **宁可没有PDF（使用空字符串`""`），也不要使用错误的PDF**
- ❌ 不要只检查HTTP 200就使用
- ❌ 不要使用来自不确定来源的PDF
- ❌ 不要跳过步骤3（内容验证）

### 常见错误案例
**错误案例1: UNO产品**
- PDF链接: peri.it网站（意大利）
- HTTP 200: ✓
- Content-Type: ✓
- 内容正确: ✗（PDF内容不是UNO产品的手册）
- **教训**: 必须打开PDF人工确认内容

---

## 项目示例提取详细步骤

### 为什么不用WebFetch？
- WebFetch可能返回不完整的HTML内容
- 曾导致5个产品（MAXIMO、SKYDECK、MULTIFLEX、GRIDFLEX、DOMINO）被错误标记为"0个项目"
- **必须用curl获取完整HTML源代码**

### 提取步骤

**步骤1: 从产品页面提取项目链接**
```bash
# 方法1: 提取所有项目链接
grep -o 'href="/projects/[^"]*"' temp.html

# 方法2: 检查项目卡片数量
grep -c "project-teasers__item" temp.html

# 方法3: 提取完整项目URL
grep -o 'https://cn.peri.com/projects/[^"]*\.html' temp.html | \
  grep -v "projects-overview\|projects\.html" | \
  sort -u
```

**步骤2: 逐个提取项目详细信息**

对每个项目链接：
```bash
# 获取项目页面
curl -s "https://cn.peri.com/projects/{project-slug}.html" > project.html

# 提取项目名称
grep -o '<h1[^>]*>[^<]*</h1>' project.html

# 提取位置
grep -o 'location[^>]*>[^<]*</span>' project.html

# 提取描述
grep -A 5 'description' project.html

# 提取图片（og:image）
grep -o 'og:image.*content="[^"]*"' project.html
```

### 项目验证清单
- [ ] 项目名称正确
- [ ] 项目位置正确
- [ ] 项目描述提到了该产品
- [ ] 项目图片URL有效（curl -I返回200）
- [ ] **项目确实在该产品的cn.peri.com页面上**（最重要！）

### 重要原则
- ✅ 必须从temp.html（产品页面HTML）中提取
- ❌ 不使用WebFetch（可能返回不完整结果）
- ❌ 不使用缓存的结果
- ❌ 不使用其他产品的项目
- ❌ 不从china_projects.json随机选择

### 验证方法
```bash
# 1. 获取产品页面的实际项目链接
curl -s "https://cn.peri.com/products/{slug}.html" > temp.html
grep -o 'https://cn.peri.com/projects/[^"]*\.html' temp.html | \
  grep -v "projects-overview\|projects\.html" | \
  sort -u > actual_projects.txt

# 2. 对比JSON中的项目链接
python3 -c "
import json
with open('{slug}_complete.json', 'r') as f:
    data = json.load(f)
    for p in data['projects']:
        print(p['link'])
" | sort > json_projects.txt

# 3. 对比两个列表
diff actual_projects.txt json_projects.txt
# 应该没有差异
```

### 常见错误案例
**错误案例1: MAXIMO产品**
- 使用了"港珠澳大桥"项目
- 但该项目不在MAXIMO的cn.peri.com页面上
- 项目是从china_projects.json随机选择的
- **教训**: 必须从产品页面HTML提取项目链接

---

## YouTube视频提取详细步骤

### ⚠️ 重要：YouTube搜索是人工操作

**YouTube视频搜索必须手动完成**，原因：
1. 需要在PERI官方频道内搜索（不是YouTube主页）
2. 需要人工判断视频语言（英语 vs 德语）
3. 需要人工判断视频内容（产品介绍 vs 项目案例 vs 培训视频）
4. 需要人工判断视频时长（≤10分钟）

### 步骤1: 在PERI官方频道内搜索

**✅ 正确方式**:
1. 访问 https://www.youtube.com/@perigroup
2. 点击频道页面的"搜索"图标（放大镜）
3. 在频道内搜索框输入：`{product_name} formwork`
4. 浏览搜索结果

**❌ 错误方式**:
- 不要在YouTube主页搜索
- 不要在Google搜索YouTube视频
- 原因：会找到大量德语培训视频和其他上传者的视频

### 步骤2: 筛选视频

**必须满足所有条件**:
- ✅ **语言**: 英语（不要德语培训视频）
  - 检查方法：看视频标题、描述、或播放几秒确认语言
- ✅ **时长**: ≤ 10分钟
  - 检查方法：视频缩略图右下角显示时长
- ✅ **内容**: 产品介绍/演示（不是项目案例视频）
  - 检查方法：看视频标题和描述
  - 产品介绍：标题包含产品名称，描述介绍产品特点
  - 项目案例：标题包含项目名称（如"Dubai Frame"），描述介绍项目
- ✅ **来源**: PERI官方频道（@perigroup）
  - 已经在频道内搜索，自动满足
- ✅ **发布时间**: 优先最新的
  - 如果有多个符合条件的视频，选择最新的

### 步骤3: 提取视频ID

**从视频URL提取11位视频ID**:

**URL格式**:
- 标准格式：`https://www.youtube.com/watch?v=CgOEI3YtG_E`
- 短链接：`https://youtu.be/CgOEI3YtG_E`
- 嵌入格式：`https://www.youtube.com/embed/CgOEI3YtG_E`

**提取方法**:
- 视频ID是URL中 `v=` 后面的11个字符
- 或者短链接中域名后的11个字符
- 例如：`CgOEI3YtG_E`

**验证**:
- [ ] 视频ID长度为11个字符
- [ ] 视频时长 ≤ 10分钟
- [ ] 视频语言是英语
- [ ] 视频内容是该产品的介绍/演示

### 搜索技巧

**关键词组合**:
```
基础搜索:
- {product_name} formwork
- {product_name} system
- {product_name} introduction
- {product_name} overview

示例:
- "TRIO formwork"
- "MAXIMO panel formwork"
- "PERI UP scaffolding"
- "SKYDECK slab formwork"
```

**如果找不到结果**:
1. 尝试简化产品名称
   - `vario-gt-24-girder-wall-formwork` → `VARIO GT 24`
   - `peri-up-easy-frame-scaffolding` → `PERI UP Easy`
2. 尝试不同的关键词
   - 添加 "product"
   - 添加 "system"
   - 移除 "formwork"
3. 检查产品是否有别名或简称

### 常见问题

**问题1: 只找到德语视频**
- 原因：在YouTube主页搜索，而不是在PERI频道内搜索
- 解决：必须在 https://www.youtube.com/@perigroup 频道内搜索

**问题2: 找到的视频超过10分钟**
- 解决：继续搜索，或者使用空字符串 `""`
- 不要使用超过10分钟的视频

**问题3: 找到的是项目案例视频**
- 特征：标题包含项目名称（如"Dubai Frame", "Burj Khalifa"）
- 解决：继续搜索产品介绍视频，或者使用空字符串 `""`

**问题4: 完全找不到视频**
- 解决：使用空字符串 `""`
- 不要使用不符合条件的视频
- 不要使用其他频道的视频

### 如果找不到合适的视频

**使用空字符串 `""`**:
```json
{
  "youtube_video_id": ""
}
```

**不要**:
- ❌ 使用德语视频
- ❌ 使用超过10分钟的视频
- ❌ 使用项目案例视频
- ❌ 使用其他频道的视频
- ❌ 使用培训视频

### 实际操作示例

**示例1: TRIO Formwork**
1. 访问 https://www.youtube.com/@perigroup
2. 在频道内搜索："TRIO formwork"
3. 找到视频："TRIO Panel Formwork System"
4. 检查：
   - 语言：英语 ✓
   - 时长：8:32 ✓
   - 内容：产品介绍 ✓
5. 提取视频ID：`ypBa9srkqy8`

**示例2: MAXIMO**
1. 访问 https://www.youtube.com/@perigroup
2. 在频道内搜索："MAXIMO formwork"
3. 找到视频："MAXIMO Panel Formwork"
4. 检查：
   - 语言：英语 ✓
   - 时长：6:45 ✓
   - 内容：产品介绍 ✓
5. 提取视频ID：`ROJJQ-tdidw`

**示例3: 找不到合适视频**
1. 访问 https://www.youtube.com/@perigroup
2. 在频道内搜索："SB brace frame"
3. 结果：没有找到符合条件的视频
4. 使用空字符串：`""`

---

## 文件命名和验证

### 文件命名规则

**格式**: `{slug}_complete.json`

**关键点**:
- slug必须与products_v2.json中的slug**完全匹配**
- 保留所有连字符`-`，不要替换成下划线`_`
- 使用完整slug，不要使用简短版本
- slug必须是英文，不能使用URL编码的中文

### 正确示例
```
slug: "gridflex-deckenschalung"
文件名: "gridflex-deckenschalung_complete.json"  ✅

slug: "vario-gt-24-girder-wall-formwork"
文件名: "vario-gt-24-girder-wall-formwork_complete.json"  ✅
```

### 错误示例
```
slug: "handset-alpha"
文件名: "handset_alpha_complete.json"  ❌ 使用了下划线

slug: "vario-gt-24-girder-wall-formwork"
文件名: "vario_gt24_complete.json"  ❌ 使用了简短版本

slug: "liwa"
文件名: "liwa-%E9%92%A2%E6%A1%86%E6%A8%A1%E6%9D%BF_complete.json"  ❌ 使用了URL编码
```

### 创建文件前的标准流程
```bash
# 1. 从products_v2.json确认slug
grep -i "产品名称" products_v2.json | grep "slug"

# 2. 记录完整slug（包括所有连字符）
# 例如: handset-alpha

# 3. 构建文件名
filename="${slug}_complete.json"

# 4. 验证文件名格式
echo $filename
# 应该输出: handset-alpha_complete.json

# 5. 创建文件
# 使用Write工具创建文件
```

### slug验证清单
- [ ] 已从products_v2.json确认slug
- [ ] slug包含所有连字符（不是下划线）
- [ ] slug是完整名称（不是简短版本）
- [ ] slug是英文（不是URL编码的中文）
- [ ] 文件名格式: {slug}_complete.json

---

## 常见错误和解决方法

### 错误1: 文件名与slug不匹配
**症状**: 代码找不到文件，无法读取数据
**原因**: 
- 使用下划线替代连字符: `handset_alpha` vs `handset-alpha`
- 使用简短版本: `vario_gt24` vs `vario-gt-24-girder-wall-formwork`
**解决**: 从products_v2.json确认准确的slug

### 错误2: PDF内容错误
**症状**: 用户下载到错误的产品手册
**原因**: 只验证了HTTP 200，没有打开PDF确认内容
**解决**: 下载PDF并人工确认内容是该产品的手册

### 错误3: 项目不匹配
**症状**: 项目不在产品页面上
**原因**: 
- 使用WebFetch（返回不完整结果）
- 从china_projects.json随机选择
- 使用其他产品的项目
**解决**: 用curl提取产品页面HTML，从中提取项目链接

### 错误4: 忘记部署
**症状**: 在线页面404
**原因**: 完成产品后没有运行部署脚本
**解决**: bash deploy-peri-gcb.command，等待2分钟后验证

### 错误5: slug使用URL编码
**症状**: GitHub Pages返回404
**原因**: slug使用了URL编码的中文（如`liwa-%E9%92%A2%E6%A1%86%E6%A8%A1%E6%9D%BF`）
**解决**: 使用英文slug（从www.peri.com/en获取）

### 错误6: YouTube视频不符合要求
**症状**: 找到的是德语培训视频
**原因**: 在YouTube主页搜索，而不是在PERI频道内搜索
**解决**: 在https://www.youtube.com/@perigroup频道内搜索

### 错误7: 批量处理导致质量下降
**症状**: 多个产品都有错误，需要返工
**原因**: 同时处理5-7个产品，没有逐个验证
**解决**: 一次只做1个产品，完成后让用户验证

---

## 核心原则和教训

### 原则1: 质量永远优先于速度
- ✅ 一次只做1个产品
- ✅ 每个产品完成后让用户验证
- ✅ 慢即是快：做对一次比返工多次更快
- ❌ 不批量处理多个产品

**数据支持**:
- 批量处理: 5个产品，3个有错误，返工率60%
- 逐个处理: 最近2个产品（LIWA, SB），0个错误，返工率0%

### 原则2: 验证正确性，不只是有效性
- ✅ HTTP 200 ≠ 内容正确
- ✅ 必须打开PDF确认内容
- ✅ 必须确认项目在产品页面上
- ✅ 必须确认视频是该产品的介绍

**三步验证法**（以PDF为例）:
1. 验证链接有效（HTTP 200）
2. 验证文件类型（Content-Type: application/pdf）
3. **验证内容正确**（打开PDF确认是该产品的手册）

### 原则3: 不要依赖工具的不完整输出
- ✅ WebFetch可能返回不完整的HTML
- ✅ 必须用curl获取完整HTML源代码
- ✅ 不要100%信任工具输出，要验证

### 原则4: 严格遵守命名规则
- ✅ 文件名必须与slug完全匹配
- ✅ 连字符`-`不能替换成下划线`_`
- ✅ 不能使用简短版本
- ✅ 创建文件前必须确认slug

### 原则5: 只做用户明确要求的工作
- ✅ 用户指定哪个产品就做哪个
- ❌ 不擅自修改其他已完成的产品
- ❌ 不假设问题的范围
- ✅ 先询问用户具体哪个产品有问题

### 原则6: 宁可没有，也不用错误的
- ✅ 找不到PDF → 使用空字符串`""`
- ✅ 找不到视频 → 使用空字符串`""`
- ❌ 不要使用错误的PDF/视频/项目

### 原则7: 部署是强制步骤
- ✅ 每个产品完成后必须部署
- ✅ 部署后必须验证在线页面（等待2分钟）
- ❌ 不能完成产品后忘记部署

---

## 命令速查表

### 确认slug
```bash
grep -i "产品名称" products_v2.json | grep "slug"
```

### 提取产品页面
```bash
curl -s "https://cn.peri.com/products/{slug}.html" > temp.html
```

### 提取项目链接
```bash
# 方法1: 提取项目链接
grep -o 'href="/projects/[^"]*"' temp.html

# 方法2: 提取完整URL
grep -o 'https://cn.peri.com/projects/[^"]*\.html' temp.html | \
  grep -v "projects-overview\|projects\.html" | \
  sort -u
```

### 提取项目详情
```bash
curl -s "https://cn.peri.com/projects/{project-slug}.html" > project.html
grep -o '<h1[^>]*>[^<]*</h1>' project.html
grep -o 'location[^>]*>[^<]*</span>' project.html
grep -o 'og:image.*content="[^"]*"' project.html
```

### 搜索PDF（按优先级）
```bash
# 方法1: PERI UK网站（推荐）
# 尝试多个slug变体
original_slug="your-product-slug"
slugs=(
  "$original_slug"
  "${original_slug%-*}"
  "${original_slug%%-*}"
)

for slug in "${slugs[@]}"; do
  result=$(curl -s "https://www.peri.ltd.uk/products/$slug.html" | grep -o '/.rest/downloads/[0-9]*' | head -1)
  if [ -n "$result" ]; then
    pdf_url="https://www.peri.ltd.uk$result"
    echo "找到: $pdf_url"
    break
  fi
done

# 方法2: Google搜索（如果方法1失败）
# 在Google搜索: peri {产品英文名} pdf
# 手动操作，复制找到的PDF链接

# 方法3: 其他区域网站
curl -s "https://cn.peri.com/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'
curl -s "https://www.peri.com/en/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'
curl -s "https://www.peri.id/en/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'
```

### 搜索YouTube视频（人工操作）
```
1. 访问 https://www.youtube.com/@perigroup
2. 在频道内搜索: {product_name} formwork
3. 筛选条件:
   - 语言: 英语
   - 时长: ≤10分钟
   - 内容: 产品介绍（不是项目案例）
4. 提取视频ID（11个字符）
5. 如果找不到: 使用空字符串 ""
```

### 验证PDF（三步法）
```bash
# 步骤1: 验证链接有效
curl -I {pdf_url}  # 必须返回200

# 步骤2: 验证文件类型
curl -I {pdf_url} | grep "Content-Type: application/pdf"

# 步骤3: 验证内容正确（人工）
curl -o temp.pdf {pdf_url}
open temp.pdf  # macOS
# 人工确认PDF内容是该产品的手册
```

### 生成和部署
```bash
# 生成页面
python3 rebuild_site_v2.py

# 部署
bash deploy-peri-gcb.command

# 等待2分钟后验证
sleep 120
curl -I "https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html"
# 必须返回: HTTP/2 200
```

---

## 详细历史文档

如需查看更详细的历史记录、错误分析、经验教训，见 `archive/` 目录：
- `archive/workflow/` - 完整工作流程文档（MASTER_WORKFLOW.md等）
- `archive/errors/` - 错误记录和分析（ERROR_TRACKING.md、CRITICAL_ERRORS_LOG.md等）
- `archive/checklists/` - 详细检查清单（PREVENTION_CHECKLIST.md等）
- `archive/analysis/` - 问题分析文档
- `archive/reports/` - 状态报告
- `archive/fixes/` - 修复记录
- `archive/setup/` - 配置文档
