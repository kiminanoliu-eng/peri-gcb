# 错误追踪和预防系统 - 使用指南

## 系统概述

本系统包含4个核心文档和2个自动化脚本，用于追踪历史错误、预防未来错误，确保剩余148个产品的处理质量。

---

## 文档结构

### 1. ERROR_TRACKING.md - 错误追踪记录
**用途**: 记录所有历史错误，按类别组织

**内容**:
- 9个已记录的错误（文件命名、数据验证、工作流程等）
- 每个错误包含：发生时间、产品名称、影响范围、根本原因
- 错误趋势分析和改进重点
- 成功案例（LIWA、SB）

**何时查看**:
- 开始处理新产品前，回顾常见错误
- 遇到问题时，查找类似的历史错误
- 每周回顾，了解错误趋势

---

### 2. PREVENTION_CHECKLIST.md - 预防检查清单
**用途**: 详细的检查清单，每个产品处理时使用

**内容**:
- 8个阶段的检查清单（从确认slug到在线验证）
- 每个检查点包含：目的、操作步骤、验证标准、验证命令
- 常见错误快速检查命令
- 完整工作流程图

**何时使用**:
- **必须**: 处理每个产品时，逐项执行检查清单
- 特别关注：阶段2（项目案例）、阶段4（PDF验证）、阶段5（文件命名）

**关键检查点**:
- ✅ 检查点 0.1: 确认产品slug（避免文件命名错误）
- ✅ 检查点 2.1: 提取项目链接（避免使用错误项目）
- ✅ 检查点 4.2: 验证PDF内容（三步验证法）
- ✅ 检查点 5.1: 文件命名（严格匹配slug）

---

### 3. LESSONS_LEARNED.md - 经验教训总结
**用途**: 从错误中学到的教训和最佳实践

**内容**:
- 7个核心教训（质量优先、验证正确性、不依赖工具等）
- 4个改进的工作方法（分阶段验证、三步验证法等）
- 3个成功案例的最佳实践
- 工作流程的演进（第1版→第2版→第3版）
- 关键指标（错误率从60%降到0%）

**何时阅读**:
- 开始新一批产品前，回顾核心教训
- 遇到困难时，查找相关教训
- 定期回顾，强化记忆

**核心原则**:
1. 质量优先（慢即是快）
2. 验证充分（正确性 > 有效性）
3. 来源准确（数据可追溯）
4. 命名严格（文件名 = slug）
5. 范围明确（只做用户要求的）
6. 工具辅助（不100%信任）
7. 流程标准（使用检查清单）

---

### 4. README_ERROR_SYSTEM.md - 本文档
**用途**: 系统使用指南

---

## 自动化脚本

### 1. pre_flight_check.py - 预检脚本
**用途**: 在创建JSON前和生成HTML前自动检查常见错误

**功能**:
- 检查slug格式（是否包含下划线、空格、大写字母）
- 检查slug是否在products_v2.json中存在
- 检查文件名是否与slug匹配
- 检查JSON结构完整性（必需字段、语言翻译、数据类型）
- 检查HTML文件是否生成

**使用方法**:
```bash
cd /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站

# 检查所有（默认）
python3 pre_flight_check.py {slug}

# 只检查slug
python3 pre_flight_check.py {slug} slug

# 只检查JSON
python3 pre_flight_check.py {slug} json

# 只检查HTML
python3 pre_flight_check.py {slug} html
```

**示例**:
```bash
# 在创建JSON文件前
python3 pre_flight_check.py gridflex-deckenschalung slug

# 在创建JSON文件后
python3 pre_flight_check.py gridflex-deckenschalung json

# 在生成HTML后
python3 pre_flight_check.py gridflex-deckenschalung html

# 部署前全面检查
python3 pre_flight_check.py gridflex-deckenschalung all
```

**输出示例**:
```
============================================================
预检: sb-brace-frame
============================================================

🔍 检查slug格式...
✅ slug格式正确

🔍 检查slug是否在products_v2.json中...
✅ slug存在于products_v2.json

🔍 检查文件名是否与slug匹配...
✅ 文件名正确: sb-brace-frame_complete.json

🔍 检查JSON文件结构...
✅ JSON结构完整

🔍 检查HTML文件...
✅ HTML文件已生成: products/sb-brace-frame.html

============================================================
预检结果
============================================================

✅ 所有检查通过！
```

---

### 2. verify_product.py - 产品验证脚本
**用途**: 全面验证产品数据的完整性和正确性

**功能**:
- 验证文件名
- 验证JSON格式和结构
- 验证所有URL有效性（图片、项目图片、PDF）
- 验证YouTube视频ID格式
- 验证生成的HTML内容
- 提供人工确认提醒（PDF内容、视频内容）

**使用方法**:
```bash
cd /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站

# 验证产品
python3 verify_product.py {slug}
```

**何时使用**:
- JSON文件创建后
- HTML生成后
- 部署前

---

## 标准工作流程（集成错误预防系统）

### 阶段0: 开始前
```bash
# 1. 询问用户要处理的产品
# 2. 从products_v2.json确认slug
grep -i "产品名称" products_v2.json

# 3. 运行预检（检查slug）
python3 pre_flight_check.py {slug} slug
```

### 阶段1-4: 数据收集
```bash
# 按照 PREVENTION_CHECKLIST.md 执行
# - 提取产品信息
# - 提取项目案例（用curl，不用WebFetch）
# - 搜索YouTube视频（在PERI频道内）
# - 查找PDF链接（三步验证法）
```

### 阶段5: 创建JSON文件
```bash
# 1. 创建文件（严格命名：{slug}_complete.json）

# 2. 运行预检（检查JSON）
python3 pre_flight_check.py {slug} json

# 3. 运行验证脚本
python3 verify_product.py {slug}

# 4. 如果有错误，修正后重新验证
```

### 阶段6: 生成HTML
```bash
# 1. 重建网站
python3 rebuild_site_v2.py

# 2. 运行预检（检查HTML）
python3 pre_flight_check.py {slug} html

# 3. 再次运行验证脚本
python3 verify_product.py {slug}
```

### 阶段7: 部署前最终检查
```bash
# 1. 全面预检
python3 pre_flight_check.py {slug} all

# 2. 人工最终确认
# - PDF内容正确（已打开确认）
# - YouTube视频正确（已观看确认）
# - 项目案例属于该产品
```

### 阶段8: 部署和验证
```bash
# 1. 部署
bash deploy-peri-gcb.command

# 2. 在线验证
# 访问 https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html

# 3. 用户最终验证
```

---

## 快速参考

### 最常见的3个错误

#### 1. 文件名与slug不匹配
**预防**: 
```bash
# 创建文件前运行
python3 pre_flight_check.py {slug} slug
```

#### 2. PDF内容不正确
**预防**: 
```bash
# 下载PDF并打开确认
curl -o temp.pdf {PDF_URL}
open temp.pdf  # macOS
# 人工确认内容是该产品的手册
```

#### 3. 项目案例不属于该产品
**预防**: 
```bash
# 从产品页面HTML提取项目
curl -s "https://cn.peri.com/products/{slug}.html" | grep -o 'href="/projects/[^"]*"'
# 不从china_projects.json随机选择
```

---

## 关键命令速查

### 确认slug
```bash
grep -i "产品名称" products_v2.json | grep "slug"
```

### 检查文件名
```bash
ls -la {slug}_complete.json
```

### 验证PDF内容
```bash
curl -o temp.pdf {PDF_URL}
open temp.pdf
```

### 提取项目链接
```bash
curl -s "https://cn.peri.com/products/{slug}.html" | grep -o 'href="/projects/[^"]*"'
```

### 运行所有验证
```bash
python3 pre_flight_check.py {slug} all
python3 verify_product.py {slug}
```

---

## 成功指标

### 目标（剩余148个产品）
- 错误率 < 5%
- 返工率 < 10%
- 首次通过率 > 90%

### 当前表现（最近2个产品）
- 错误率: 0%
- 返工率: 0%
- 首次通过率: 100%

---

## 文档维护

### 何时更新ERROR_TRACKING.md
- 发现新错误时
- 每周回顾时

### 何时更新PREVENTION_CHECKLIST.md
- 发现新的检查点时
- 改进验证方法时

### 何时更新LESSONS_LEARNED.md
- 从错误中学到新教训时
- 发现新的最佳实践时

---

## 总结

### 核心理念
1. **质量优先于速度**: 慢即是快，做对一次比返工多次更快
2. **验证正确性**: 不只是有效性，更要验证内容正确
3. **使用检查清单**: 每个产品执行相同的标准流程
4. **自动化辅助**: 使用脚本减少人工错误

### 关键工具
- **PREVENTION_CHECKLIST.md**: 每个产品必须使用
- **pre_flight_check.py**: 每个阶段运行
- **verify_product.py**: 部署前运行

### 最重要的原则
**宁可慢一点，也要确保每个产品的数据100%正确。**

---

**系统创建日期**: 2026-04-06  
**适用范围**: 剩余148个PERI产品  
**预期效果**: 错误率 < 5%，返工率 < 10%
