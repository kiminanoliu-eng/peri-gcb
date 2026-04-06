# PERI产品网站生成 - 完整工作流程

## 项目概述

**目标**: 为160个PERI产品创建完整的中文介绍网站

**每个产品需要包含**:
1. 7种语言翻译（中、英、西、德、葡、塞、匈）
2. 产品缩略图（来自cn.peri.com的og:image）
3. YouTube视频（英语、≤10分钟、来自PERI官方频道）
4. 项目案例（从cn.peri.com产品页面提取）
5. PDF下载链接（直接PDF链接，优先级：cn.peri.com > peri.com/en > 其他区域网站）
6. Web3Forms留言板

**当前进度**: 10个产品已完成，150个待处理

---

## 核心原则（必须遵守）

### 1. 质量优先于速度
- ✅ 一次只做1个产品
- ✅ 每个产品完成后让用户验证
- ❌ 不批量处理多个产品

### 2. 只做用户明确要求的工作
- ✅ 用户指定哪个产品就做哪个
- ❌ 不擅自修改其他已完成的产品
- ❌ 不擅自修改代码

### 3. 验证数据的正确性，不只是有效性
- ✅ PDF链接：必须打开PDF确认内容是该产品的手册
- ✅ 项目案例：必须确认项目在该产品的cn.peri.com页面上
- ✅ YouTube视频：必须确认视频是该产品的英语介绍
- ❌ 不能只检查HTTP 200就使用

### 4. 文件命名规则
- 格式：`{slug}_complete.json`
- slug必须与products_v2.json中的slug**完全匹配**
- 保留连字符`-`，不要替换成下划线`_`

---

## 错误教训总结（从之前的工作中学到的）

### 错误1: 依赖WebFetch工具的不完整输出

**问题**: 使用WebFetch提取项目案例时，工具返回"未找到项目"，没有验证就相信了

**后果**: MAXIMO、SKYDECK、MULTIFLEX、GRIDFLEX、DOMINO最初都标记为"0个项目"，实际上都有项目案例

**教训**: 
- ❌ 不能依赖WebFetch的输出
- ✅ 必须用curl获取HTML源代码验证

### 错误2: 批量处理导致质量下降

**问题**: 为了速度，同时处理5-7个产品，没有逐个验证

**后果**: 产生大量错误数据，需要返工修复

**教训**:
- ❌ 不批量处理多个产品
- ✅ 一次只做1个产品，完成后让用户验证

### 错误3: 只验证链接有效性，不验证内容正确性

**问题**: UNO产品的PDF链接返回HTTP 200，但内容不是UNO产品的手册

**后果**: 用户发现PDF内容错误，需要重新查找

**教训**:
- ❌ 不能只检查HTTP 200就使用
- ✅ 必须打开PDF确认内容是该产品的手册

### 错误4: 使用错误的项目案例

**问题**: MAXIMO产品使用了港珠澳大桥项目，但该项目不在MAXIMO的cn.peri.com页面上

**后果**: 项目案例与产品不匹配

**教训**:
- ❌ 不从china_projects.json随机选择项目
- ❌ 不使用其他产品的项目
- ✅ 必须从该产品的cn.peri.com页面提取项目链接

### 错误5: 误解问题范围，擅自修改已完成的产品

**问题**: 用户说"pdf链接不对"，我理解成所有产品都有问题，擅自修改了HANDSET和VARIO的文件名

**后果**: 用户强烈反对，要求恢复

**教训**:
- ❌ 不要假设问题的范围
- ❌ 不擅自修改已完成的产品
- ✅ 先询问用户具体哪个产品有问题
- ✅ 只修改用户明确指出有问题的产品

### 错误6: 在YouTube主页搜索，而不是在PERI频道内搜索

**问题**: 在YouTube主页搜索产品名称，找到的大多是德语培训视频

**后果**: 视频不符合要求（需要英语产品介绍）

**教训**:
- ❌ 不在YouTube主页搜索
- ✅ 必须在PERI官方频道内搜索：https://www.youtube.com/@perigroup

### 错误7: 文件名与slug不匹配

**问题**: 创建了`handset_alpha_complete.json`，但slug是`handset-alpha`（使用下划线而不是连字符）

**后果**: 代码找不到文件，无法读取数据

**教训**:
- ❌ 不使用下划线替代连字符
- ❌ 不使用简短版本的文件名
- ✅ 文件名必须与slug完全匹配：`{slug}_complete.json`

---

## 完整工作流程

### 阶段0: 开始前确认

**操作**:
1. 询问用户：下一个要做的产品是什么？
2. 从products_v2.json确认产品的准确slug

**工具**: Read工具读取products_v2.json

---

### 阶段1: 提取产品基本信息

#### 1.1 获取产品页面HTML

**工具**: curl命令
```bash
curl -s "https://cn.peri.com/products/{slug}.html" > temp.html
```

**验证**:
- 文件大小 > 0
- 包含产品名称

#### 1.2 提取产品缩略图URL

**工具**: grep命令
```bash
grep 'og:image' temp.html
```

**提取内容**: `<meta property="og:image" content="图片URL">`

**验证图片有效性**:
```bash
curl -I {image_url}  # 必须返回200
```

#### 1.3 提取产品描述

**来源**: products_v2.json中已有7种语言的翻译

**工具**: Read工具读取products_v2.json，找到对应slug的description字段

---

### 阶段2: 提取项目案例（关键步骤）

#### 2.1 从产品页面提取项目链接

**工具**: grep命令（不使用WebFetch）
```bash
# 方法1: 提取所有项目链接
grep -o 'href="/projects/[^"]*"' temp.html

# 方法2: 检查项目卡片数量
grep -c "project-teasers__item" temp.html
```

**重要**: 
- ✅ 必须从temp.html（产品页面HTML）中提取
- ❌ 不使用WebFetch（可能返回不完整结果）
- ❌ 不使用缓存的结果
- ❌ 不使用其他产品的项目
- ❌ 不从china_projects.json随机选择

#### 2.2 逐个提取项目详细信息

对每个项目链接：

**工具**: curl + grep
```bash
# 获取项目页面
curl -s "https://cn.peri.com{project_url}" > project.html

# 提取项目名称
grep -o '<h1[^>]*>[^<]*</h1>' project.html

# 提取位置
grep -o 'location[^>]*>[^<]*</span>' project.html

# 提取描述
grep -A 5 'description' project.html

# 提取图片（og:image）
grep -o 'og:image.*content="[^"]*"' project.html
```

**验证清单**:
- [ ] 项目名称正确
- [ ] 项目位置正确
- [ ] 项目描述提到了该产品
- [ ] 项目图片URL有效（curl -I返回200）
- [ ] 项目确实在该产品的cn.peri.com页面上

---

### 阶段3: 搜索YouTube视频

#### 3.1 在PERI官方频道内搜索

**人工操作**（必须手动完成）:
1. 访问 https://www.youtube.com/@perigroup
2. 在频道内搜索框输入：`{product_name} formwork`
3. **不要在YouTube主页搜索**

#### 3.2 筛选视频

**筛选条件**:
- ✅ 语言：英语（不要德语培训视频）
- ✅ 时长：≤ 10分钟
- ✅ 内容：产品介绍/演示（不是项目案例视频）
- ✅ 来源：PERI官方频道
- ✅ 发布时间：优先最新的

#### 3.3 提取视频ID

**人工操作**:
从视频URL提取11位视频ID
- 例如：`https://www.youtube.com/watch?v=CgOEI3YtG_E` → `CgOEI3YtG_E`

**验证**:
- [ ] 视频ID长度为11个字符
- [ ] 视频时长 ≤ 10分钟
- [ ] 视频语言是英语
- [ ] 视频内容是该产品的介绍

**如果找不到合适的视频**: 使用空字符串 `""`

---

### 阶段4: 查找PDF链接（最关键）

#### 4.1 搜索顺序

**工具**: curl + grep

**优先级1**: cn.peri.com
```bash
curl -s "https://cn.peri.com/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'
```

**优先级2**: www.peri.com/en
```bash
curl -s "https://www.peri.com/en/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'
```

**优先级3**: 其他区域网站
- peri.id (印尼)
- peri.com.au (澳大利亚)
- peri.co.za (南非)
- peri.ltd.uk (英国)

#### 4.2 PDF验证（三步验证法）

**步骤1: 验证链接有效**
```bash
curl -I {pdf_url}  # 必须返回200
```

**步骤2: 验证是PDF文件**
```bash
curl -I {pdf_url} | grep "Content-Type: application/pdf"
```

**步骤3: 验证内容正确（最重要！）**
```bash
# 下载PDF
curl -o temp.pdf {pdf_url}

# 人工检查（必须手动完成）:
# 1. 打开temp.pdf文件
# 2. 确认PDF内容确实是该产品的手册
# 3. 不是其他产品的手册
# 4. 不是意大利语或其他不相关的PDF
```

**验证清单**:
- [ ] PDF链接返回HTTP 200
- [ ] Content-Type是application/pdf
- [ ] **PDF内容确实是该产品的手册**（人工确认）
- [ ] PDF语言合适（优先英语或中文）
- [ ] PDF不是其他产品的手册
- [ ] PDF来自PERI官方网站

**重要原则**:
- ✅ 宁可没有PDF（使用空字符串`""`），也不要使用错误的PDF
- ❌ 不要只检查HTTP 200就使用
- ❌ 不要使用来自不确定来源的PDF

---

### 阶段5: 创建完整JSON文件

#### 5.1 文件命名

**格式**: `{slug}_complete.json`

**示例**:
```
slug: "gridflex-deckenschalung"
文件名: "gridflex-deckenschalung_complete.json"  ✅

文件名: "gridflex_complete.json"  ❌ 错误
文件名: "gridflex-deckenschalung.json"  ❌ 缺少_complete
```

#### 5.2 JSON结构

**工具**: Write工具创建JSON文件

```json
{
  "slug": "product-slug",
  "name_zh": "产品中文名",
  "category": "分类",
  "subcategory": "子分类",
  "cn_url": "https://cn.peri.com/products/{slug}.html",
  "image": "验证过的图片URL",
  "description": {
    "zh": "中文描述",
    "en": "English description",
    "es": "Descripción en español",
    "de": "Deutsche Beschreibung",
    "pt": "Descrição em português",
    "sr": "Српски опис",
    "hu": "Magyar leírás"
  },
  "projects": [
    {
      "name": "项目名称",
      "location": "位置",
      "description": "描述",
      "image": "项目图片URL",
      "link": "https://cn.peri.com/projects/..."
    }
  ],
  "pdf_link": "PDF URL或空字符串",
  "youtube_video_id": "视频ID或空字符串"
}
```

**验证清单**:
- [ ] slug与products_v2.json完全匹配
- [ ] 所有7种语言翻译完整
- [ ] projects数组包含所有提取的项目
- [ ] pdf_link是验证过内容的URL或空字符串
- [ ] youtube_video_id是验证过的视频ID或空字符串

---

### 阶段6: 生成产品页面

#### 6.1 运行生成脚本

**工具**: Bash命令
```bash
cd /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站
python3 rebuild_site_v2.py
```

**检查输出**:
- [ ] 显示"✅ Done!"
- [ ] 没有错误信息

#### 6.2 验证生成的HTML

**工具**: Bash命令
```bash
# 检查产品页面是否生成
ls products/{slug}.html

# 检查PDF链接
grep 'btn btn-yellow' products/{slug}.html | grep -o 'href="[^"]*"'

# 检查YouTube视频
grep 'youtube.com/embed' products/{slug}.html

# 检查项目案例数量
grep -c 'card-title' products/{slug}.html
```

**验证清单**:
- [ ] products/{slug}.html文件存在
- [ ] PDF链接正确（如果有）
- [ ] YouTube视频嵌入正确（如果有）
- [ ] 项目案例数量正确

---

### 阶段7: 部署到GitHub Pages

#### 7.1 部署

**工具**: Bash命令
```bash
bash deploy-peri-gcb.command
```

#### 7.2 等待构建完成

**人工操作**: 等待1-2分钟，GitHub Pages构建完成

#### 7.3 在线验证

**人工操作**: 访问 https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html

**验证清单**:
- [ ] 产品页面在线可访问
- [ ] 图片加载正常
- [ ] PDF链接可点击（如果有）
- [ ] YouTube视频可播放（如果有）
- [ ] 项目案例链接可访问

---

### 阶段8: 用户最终验证

**操作**: 请用户检查产品页面，确认所有内容正确

**如果用户确认无误**: 继续下一个产品

**如果用户发现问题**: 修正问题，重新生成并部署

---

## 工具使用总结

### 必须使用的工具

| 工具 | 用途 | 使用场景 |
|------|------|---------|
| **curl** | 获取HTML源代码 | 提取产品信息、项目案例 |
| **grep** | 搜索和提取文本 | 提取图片URL、项目链接、PDF链接 |
| **Read** | 读取本地文件 | 读取products_v2.json |
| **Write** | 创建JSON文件 | 创建{slug}_complete.json |
| **Bash** | 执行脚本 | 运行rebuild_site_v2.py和部署脚本 |

### 必须人工完成的操作

| 操作 | 原因 |
|------|------|
| **YouTube视频搜索** | 需要在PERI频道内手动搜索和筛选 |
| **PDF内容验证** | 必须打开PDF确认内容是该产品的手册 |
| **最终在线验证** | 需要人工访问网站确认所有功能正常 |

### 禁止使用的工具

| 工具 | 原因 |
|------|------|
| **WebFetch** | 可能返回不完整的HTML内容 |

---

## 常见问题处理

### 问题1: 找不到项目案例

**处理方式**:
1. ✅ 用curl检查HTML源代码
2. ✅ 搜索`<h2>项目实例</h2>`或`project-teasers__items-list`
3. ✅ 如实报告："确认HTML中没有项目卡片"
4. ✅ projects数组使用空数组`[]`
5. ❌ 不要说"无项目案例"就跳过验证

### 问题2: 找不到PDF

**处理方式**:
1. ✅ 搜索多个区域网站
2. ✅ 如实报告："未找到该产品的PDF"
3. ✅ pdf_link使用空字符串`""`
4. ❌ 不要使用错误的PDF

### 问题3: 找不到YouTube视频

**处理方式**:
1. ✅ 在PERI频道内搜索
2. ✅ 尝试不同的关键词组合（产品名 + formwork）
3. ✅ 如实报告："未找到合适的英语产品介绍视频"
4. ✅ youtube_video_id使用空字符串`""`

---

## 质量检查清单（每个产品必须完成）

### 数据收集阶段
- [ ] 产品slug与products_v2.json完全匹配
- [ ] 图片URL有效（HTTP 200）
- [ ] 项目案例确实在该产品的cn.peri.com页面上
- [ ] 项目数量正确
- [ ] 所有项目图片URL有效
- [ ] YouTube视频ID正确（11个字符）
- [ ] YouTube视频是英语产品介绍
- [ ] YouTube视频时长 ≤ 10分钟
- [ ] PDF链接有效（HTTP 200）
- [ ] **PDF内容确实是该产品的手册**（人工确认）

### 文件创建阶段
- [ ] JSON文件名格式正确：{slug}_complete.json
- [ ] JSON文件名与slug完全匹配
- [ ] JSON结构完整（所有必需字段）
- [ ] 7种语言翻译完整

### 生成和部署阶段
- [ ] rebuild_site_v2.py运行成功
- [ ] products/{slug}.html生成成功
- [ ] HTML中包含PDF链接（如果有）
- [ ] HTML中包含YouTube视频（如果有）
- [ ] HTML中项目案例数量正确
- [ ] 部署成功
- [ ] 在线页面可访问
- [ ] 用户最终验证通过

---

## 文件结构

```
/Users/fufu/Documents/Claude/Projects/自动化/创建产品网站/
├── products_v2.json                    # 所有产品基础数据
├── rebuild_site_v2.py                  # 网站生成脚本
├── deploy-peri-gcb.command             # 部署脚本
├── {slug}_complete.json                # 单个产品完整数据
├── categories/                         # 分类页面（Git追踪）
├── products/                           # 产品页面（Git追踪）
├── index.html                          # 首页（Git追踪）
└── search.html                         # 搜索页面（Git追踪）
```

---

## 当前状态

**已完成产品**: 10个
1. HANDSET Alpha
2. VARIO GT 24
3. MAXIMO
4. MULTIFLEX
5. DOMINO
6. GRIDFLEX
7. SKYDECK
8. UNO
9. TRIO Rahmenschalung
10. TRIO Schalungssystem

**待完成产品**: 150个

**网站地址**: https://kiminanoliu-eng.github.io/peri-gcb/

---

**文档创建日期**: 2026-04-06
**最后更新**: 2026-04-06
**版本**: 1.0
