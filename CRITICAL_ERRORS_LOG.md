# 严重错误日志

## 2026-04-06 - LIWA和SB产品处理

### 错误1: 忘记部署到GitHub Pages

**严重程度**: 🔴 高

**问题描述**:
- 完成LIWA和SB两个产品后，没有运行部署脚本
- 导致用户无法访问LIWA页面（404错误）
- 所有修改都在本地，没有推送到GitHub

**根本原因**:
- 工作流程中缺少"部署"这个强制步骤
- 没有在完成产品后立即部署
- 没有验证在线页面是否可访问

**影响范围**:
- LIWA产品页面无法访问
- SB产品页面无法访问
- 用户无法验证产品

**解决方案**:
- 立即运行 `bash deploy-peri-gcb.command`
- 等待1-2分钟后验证在线页面

**预防措施**:
1. **强制部署步骤**: 每个产品完成后必须部署
2. **在线验证**: 部署后必须访问在线页面验证
3. **检查清单**: 添加"部署并验证在线页面"到检查清单

**检查命令**:
```bash
# 部署
bash deploy-peri-gcb.command

# 等待2分钟后验证
curl -I "https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html"
# 必须返回 HTTP/2 200
```

---

### 错误2: PDF内容验证不充分

**严重程度**: 🔴 高

**问题描述**:
- SB产品的PDF链接有效（HTTP 200）
- PDF文件可以下载（5.8MB）
- 但PDF内容不是SB产品的手册

**根本原因**:
- 只验证了PDF链接的有效性（HTTP 200）
- 只验证了文件类型（application/pdf）
- **没有打开PDF确认内容是该产品的手册**

**影响范围**:
- 用户下载到错误的PDF
- 产品信息不准确
- 需要返工修复

**当前状态**:
- PDF链接: `https://www.peri.id/dam/jcr:9f85565f-4040-3033-a38d-1932648984cc/sb-brace-frame.pdf`
- 文件已下载: `/tmp/sb_brace_frame.pdf`
- **等待用户提供正确的PDF链接**

**教训**:
根据MASTER_WORKFLOW.md第4.2节"PDF验证（三步验证法）"：
1. ✅ 步骤1: 验证链接有效（HTTP 200）
2. ✅ 步骤2: 验证是PDF文件（Content-Type）
3. ❌ **步骤3: 验证内容正确（打开PDF确认）** ← 这一步被跳过了！

**预防措施**:
1. **强制人工验证**: 找到PDF后，必须下载并打开确认内容
2. **验证清单**: 
   - [ ] PDF链接返回HTTP 200
   - [ ] Content-Type是application/pdf
   - [ ] **打开PDF，确认是该产品的手册**
   - [ ] PDF语言合适（英语或中文）
   - [ ] PDF不是其他产品的手册
3. **宁可没有PDF**: 如果不确定PDF内容，使用空字符串`""`

**正确流程**:
```bash
# 1. 下载PDF
curl -o temp.pdf {pdf_url}

# 2. 打开PDF（macOS）
open temp.pdf

# 3. 人工检查：
#    - PDF标题是否包含产品名称？
#    - PDF内容是否是该产品的技术规格？
#    - PDF是否是PERI官方文档？

# 4. 只有确认正确后才使用该PDF链接
```

---

### 错误3: 验证Agent也会犯错

**严重程度**: 🟡 中

**问题描述**:
- 用户报告"SB的项目示例不对"
- 但实际验证发现：SB的4个项目与cn.peri.com产品页面完全一致
- 验证Agent的报告可能有误导性

**根本原因**:
- Agent没有直接对比cn.peri.com产品页面的项目列表
- Agent可能依赖了不完整的数据
- 没有用curl获取实际的产品页面HTML进行对比

**实际情况**:
```
cn.peri.com/products/sb-brace-frame.html 上的项目：
1. dubai-frame-united-arab-emirates.html ✅
2. potsdamer-platz.html ✅
3. research-and-development-centre-of-ferring-pharmaceuticals-a-s-copenhagen-denmark.html ✅
4. vtb-arena-moscow-russia.html ✅

sb-brace-frame_complete.json 中的项目：
1. dubai-frame-united-arab-emirates.html ✅
2. potsdamer-platz.html ✅
3. research-and-development-centre-of-ferring-pharmaceuticals-a-s-copenhagen-denmark.html ✅
4. vtb-arena-moscow-russia.html ✅

结论：完全一致！
```

**教训**:
- **不要完全信任Agent的验证结果**
- **必须用curl获取实际页面进行对比**
- **验证方法要准确**

**正确的验证方法**:
```bash
# 1. 获取产品页面
curl -s "https://cn.peri.com/products/{slug}.html" > temp.html

# 2. 提取实际的项目链接
grep -o 'https://cn.peri.com/projects/[^"]*\.html' temp.html | \
  grep -v "projects-overview\|projects\.html" | \
  sort -u

# 3. 对比JSON中的项目链接
python3 -c "
import json
with open('{slug}_complete.json', 'r') as f:
    data = json.load(f)
    for p in data['projects']:
        print(p['link'])
" | sort

# 4. 人工对比两个列表是否一致
```

---

### 错误4: YouTube环节的弯路

**严重程度**: 🟡 中

**问题描述**:
- 文件名不匹配：创建了`liwa-钢框模板_complete.json`，但slug是`liwa-%E9%92%A2%E6%A1%86%E6%A8%A1%E6%9D%BF`
- 代码功能不完整：rebuild_site_v2.py不读取`youtube_video_id`
- 多次验证失败

**根本原因**:
1. 没有检查products_v2.json中的实际slug格式（URL编码）
2. 代码逻辑不一致（PDF有读取逻辑，YouTube没有）
3. 验证方法不准确

**解决方案**:
1. 修改了rebuild_site_v2.py，添加读取`youtube_video_id`的逻辑
2. 重命名文件为`liwa-%E9%92%A2%E6%A1%86%E6%A8%A1%E6%9D%BF_complete.json`
3. 重新生成网站

**预防措施**:
1. **创建文件前检查slug**:
```bash
python3 -c "
import json
with open('products_v2.json', 'r') as f:
    data = json.load(f)
    # 搜索产品，打印实际的slug
"
```

2. **使用预检脚本**:
```bash
python3 pre_flight_check.py {slug} slug
```

---

## 核心教训

### 1. 部署是强制步骤
- ❌ 不能完成产品后忘记部署
- ✅ 每个产品完成后立即部署
- ✅ 部署后验证在线页面可访问

### 2. PDF内容必须人工确认
- ❌ 不能只检查HTTP 200就使用
- ✅ 必须下载并打开PDF确认内容
- ✅ 宁可没有PDF也不用错误的PDF

### 3. 验证方法要准确
- ❌ 不能依赖Agent的不完整验证
- ✅ 必须用curl获取实际页面对比
- ✅ 人工验证关键数据

### 4. 文件命名要精确
- ❌ 不能假设slug格式
- ✅ 从products_v2.json获取实际slug
- ✅ 使用预检脚本验证

---

## 改进的工作流程

### 每个产品的完整流程（12步）

1. **确认产品**: 询问用户要做哪个产品
2. **检查slug**: 从products_v2.json获取准确的slug
3. **提取数据**: 从cn.peri.com提取产品信息和项目
4. **搜索YouTube**: 在PERI频道搜索视频
5. **查找PDF**: 搜索多个区域网站
6. **验证PDF内容**: ⚠️ **下载并打开PDF确认内容**
7. **创建JSON**: 使用准确的slug命名
8. **生成HTML**: 运行rebuild_site_v2.py
9. **本地验证**: 检查HTML内容正确
10. **部署**: ⚠️ **运行deploy-peri-gcb.command**
11. **在线验证**: ⚠️ **访问在线页面确认可访问**
12. **用户确认**: 让用户验证产品

### 强制检查点

**完成产品后必须执行**:
```bash
# 1. 部署
bash deploy-peri-gcb.command

# 2. 等待2分钟
sleep 120

# 3. 验证在线页面
curl -I "https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html"

# 4. 如果返回200，告诉用户可以验证
# 5. 如果返回404，检查问题并重新部署
```

---

## 下一个产品的检查清单

### 开始前
- [ ] 询问用户要做哪个产品
- [ ] 从products_v2.json获取准确的slug
- [ ] 运行预检脚本验证slug

### 数据收集
- [ ] 从cn.peri.com提取产品信息
- [ ] 提取项目案例（用curl，不用WebFetch）
- [ ] 验证项目在产品页面上
- [ ] 搜索YouTube视频（人工）
- [ ] 查找PDF链接

### PDF验证（三步）
- [ ] 步骤1: 验证链接有效（HTTP 200）
- [ ] 步骤2: 验证是PDF文件
- [ ] 步骤3: **下载并打开PDF确认内容**

### 文件创建
- [ ] 使用准确的slug命名JSON文件
- [ ] 验证JSON结构完整
- [ ] 7种语言翻译完整

### 生成和部署
- [ ] 运行rebuild_site_v2.py
- [ ] 验证本地HTML正确
- [ ] **运行deploy-peri-gcb.command**
- [ ] **等待2分钟**
- [ ] **验证在线页面可访问**

### 最终确认
- [ ] 让用户验证产品
- [ ] 记录任何问题
- [ ] 更新错误日志

---

**最后更新**: 2026-04-06 18:00
**状态**: LIWA和SB已部署，等待用户提供SB的正确PDF链接
