# 快速错误预防指南

## 一页纸速查表 - 处理每个产品时使用

---

## 开始前（5分钟）

### ✅ 步骤1: 确认slug
```bash
# 从products_v2.json确认准确的slug
grep -i "产品名称" products_v2.json

# 记录完整slug（包括所有连字符）
SLUG="从products_v2.json复制的slug"
```

### ✅ 步骤2: 预检slug
```bash
python3 pre_flight_check.py $SLUG slug
```

**必须通过才能继续！**

---

## 数据收集（15分钟）

### ✅ 步骤3: 提取产品信息
```bash
# 获取产品页面
curl -s "https://cn.peri.com/products/$SLUG.html" > temp.html

# 提取图片
grep 'og:image' temp.html

# 验证图片
curl -I {IMAGE_URL}  # 必须200
```

### ✅ 步骤4: 提取项目案例（关键！）
```bash
# 从temp.html提取项目链接
grep -o 'href="/projects/[^"]*"' temp.html

# 对每个项目
curl -s "https://cn.peri.com{PROJECT_URL}" > project.html
grep -o '<h1[^>]*>[^<]*</h1>' project.html
grep -o 'og:image.*content="[^"]*"' project.html

# 验证项目图片
curl -I {PROJECT_IMAGE_URL}  # 必须200
```

**关键原则**:
- ✅ 必须从temp.html提取
- ❌ 不用WebFetch
- ❌ 不从china_projects.json选择

### ✅ 步骤5: 搜索YouTube视频
```
1. 访问 https://www.youtube.com/@perigroup
2. 在频道内搜索: {产品名称} formwork
3. 筛选: 英语、≤10分钟、产品介绍
4. 提取11位视频ID
```

**如果找不到**: 使用空字符串 `""`

### ✅ 步骤6: 查找PDF（最关键！）
```bash
# 按优先级搜索
curl -s "https://cn.peri.com/products/$SLUG.html" | grep -o 'https://[^"]*\.pdf'
curl -s "https://www.peri.com/en/products/$SLUG.html" | grep -o 'https://[^"]*\.pdf'
curl -s "https://www.peri.id/products/$SLUG.html" | grep -o 'https://[^"]*\.pdf'

# 三步验证法
curl -I {PDF_URL}  # 步骤1: HTTP 200
curl -I {PDF_URL} | grep "application/pdf"  # 步骤2: 类型正确
curl -o temp.pdf {PDF_URL}  # 步骤3: 下载并打开确认内容
open temp.pdf  # 人工确认是该产品的手册
```

**关键原则**:
- ✅ 必须打开PDF确认内容
- ❌ 不只检查HTTP 200
- ✅ 找不到正确的PDF就用空字符串 `""`

---

## 创建JSON（5分钟）

### ✅ 步骤7: 创建JSON文件
```bash
# 文件名格式: {slug}_complete.json
FILENAME="${SLUG}_complete.json"

# 创建JSON文件（使用Write工具）
# 确保:
# - slug字段与文件名匹配
# - 7种语言翻译完整
# - projects数组包含所有项目
# - pdf_link和youtube_video_id正确或为空字符串
```

### ✅ 步骤8: 验证JSON
```bash
# 预检JSON
python3 pre_flight_check.py $SLUG json

# 全面验证
python3 verify_product.py $SLUG
```

**必须通过才能继续！**

---

## 生成和部署（5分钟）

### ✅ 步骤9: 生成HTML
```bash
# 重建网站
python3 rebuild_site_v2.py

# 验证HTML
python3 pre_flight_check.py $SLUG html
python3 verify_product.py $SLUG
```

### ✅ 步骤10: 部署前最终检查
```bash
# 全面预检
python3 pre_flight_check.py $SLUG all

# 人工确认
# - PDF内容正确（已打开确认）✓
# - YouTube视频正确（已观看确认）✓
# - 项目案例属于该产品 ✓
```

### ✅ 步骤11: 部署
```bash
bash deploy-peri-gcb.command

# 等待1-2分钟后访问
# https://kiminanoliu-eng.github.io/peri-gcb/products/$SLUG.html
```

### ✅ 步骤12: 用户验证
请用户检查产品页面，确认所有内容正确

---

## 最常见的3个错误及预防

### ❌ 错误1: 文件名与slug不匹配
**症状**: 代码找不到文件
**预防**: 
```bash
# 创建文件前运行
python3 pre_flight_check.py $SLUG slug
# 文件名必须是: {slug}_complete.json
```

### ❌ 错误2: PDF内容不正确
**症状**: 用户报告PDF不是该产品的
**预防**: 
```bash
# 下载并打开PDF确认
curl -o temp.pdf {PDF_URL}
open temp.pdf
# 人工确认内容是该产品的手册
```

### ❌ 错误3: 项目案例不属于该产品
**症状**: 项目不在产品页面上
**预防**: 
```bash
# 从产品页面HTML提取
curl -s "https://cn.peri.com/products/$SLUG.html" | grep -o 'href="/projects/[^"]*"'
# 不从china_projects.json随机选择
```

---

## 核心原则（必须记住）

1. **质量优先**: 慢即是快，做对一次比返工多次更快
2. **验证正确性**: 不只是有效性（HTTP 200），更要验证内容正确
3. **严格命名**: 文件名 = {slug}_complete.json
4. **数据来源**: 项目必须从产品页面HTML提取
5. **三步验证**: PDF/项目/视频都要验证有效性+类型+内容

---

## 检查清单（每个产品）

- [ ] 从products_v2.json确认slug
- [ ] 运行 `python3 pre_flight_check.py $SLUG slug`
- [ ] 从产品页面HTML提取项目（用curl）
- [ ] 验证所有项目图片URL（HTTP 200）
- [ ] 在PERI频道内搜索YouTube视频
- [ ] 下载并打开PDF确认内容正确
- [ ] 文件名格式: {slug}_complete.json
- [ ] 运行 `python3 pre_flight_check.py $SLUG json`
- [ ] 运行 `python3 verify_product.py $SLUG`
- [ ] 运行 `python3 rebuild_site_v2.py`
- [ ] 运行 `python3 pre_flight_check.py $SLUG all`
- [ ] 人工最终确认（PDF、视频、项目）
- [ ] 部署并在线验证
- [ ] 用户最终验证

---

## 遇到问题时

### 找不到项目案例
```bash
# 用curl验证HTML源代码
curl -s "https://cn.peri.com/products/$SLUG.html" > temp.html
grep -i "项目" temp.html
grep -i "project" temp.html
# 如果确实没有，使用空数组 []
```

### 找不到PDF
```bash
# 搜索多个区域网站
# cn.peri.com → peri.com/en → peri.id → peri.com.au → peri.co.za
# 如果都找不到，使用空字符串 ""
```

### 找不到YouTube视频
```bash
# 在PERI频道内尝试不同关键词
# 如果找不到合适的，使用空字符串 ""
```

---

## 时间分配（总计30分钟/产品）

- 确认slug和预检: 5分钟
- 数据收集: 15分钟
- 创建和验证JSON: 5分钟
- 生成、部署、验证: 5分钟

**目标**: 首次通过率 > 90%，无需返工

---

**打印本页，处理每个产品时对照使用！**
