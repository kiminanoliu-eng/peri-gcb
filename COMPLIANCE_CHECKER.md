# 产品合规性检查规则

## 检查Agent职责

每完成一个产品后，检查Agent必须验证以下所有规则，确保产品数据的正确性和完整性。

---

## 检查清单

### 1. 文件命名检查
- [ ] JSON文件名格式：`{slug}_complete.json`
- [ ] 文件名与products_v2.json中的slug完全匹配
- [ ] 使用连字符`-`，不是下划线`_`
- [ ] 不包含URL编码字符（如`%E9%92%A2`）

### 2. PDF链接检查
- [ ] 如果`pdf_link`不为空：
  - [ ] PDF链接返回HTTP 200
  - [ ] Content-Type是`application/pdf`
  - [ ] **PDF内容与产品匹配**（最重要！）
  - [ ] PDF来自PERI官方网站
- [ ] 如果`pdf_link`为空字符串`""`：
  - [ ] 生成的HTML页面**已隐藏**PDF按钮
  - [ ] 页面中不显示PDF相关组件

### 3. YouTube视频检查
- [ ] 如果`youtube_video_id`不为空：
  - [ ] 视频ID长度为11个字符
  - [ ] 视频来自PERI官方频道 @perigroup
  - [ ] 视频语言是英语（不是德语）
  - [ ] 视频时长 ≤ 10分钟
  - [ ] **视频内容是该产品的介绍**（不是项目案例）
- [ ] 如果`youtube_video_id`为空字符串`""`：
  - [ ] 生成的HTML页面**已隐藏**YouTube视频组件
  - [ ] 页面中不显示视频相关组件

### 4. 项目案例检查
- [ ] 如果`projects`数组不为空：
  - [ ] 每个项目都有：name, location, description, image, link
  - [ ] 项目链接格式：`https://cn.peri.com/projects/{slug}.html`
  - [ ] **项目确实在该产品的cn.peri.com页面上**（最重要！）
  - [ ] 项目图片URL有效（返回200）
  - [ ] 项目描述提到了该产品或相关技术
- [ ] 如果`projects`数组为空`[]`：
  - [ ] 生成的HTML页面**已隐藏**项目案例区域
  - [ ] 页面中不显示项目相关组件

### 5. 描述翻译检查
- [ ] `description`对象包含7种语言：zh, en, es, de, fr, pt, ar
- [ ] 中文描述与product_list.json中的描述一致
- [ ] 其他语言描述是合理的翻译（不是机械翻译）

### 6. 基本信息检查
- [ ] `slug`与文件名匹配
- [ ] `name_zh`正确
- [ ] `category`和`subcategory`正确
- [ ] `thumbnail`图片URL有效（返回200）

### 7. 页面生成检查
- [ ] 运行`python3 rebuild_site_v2.py`成功
- [ ] 生成的HTML文件存在：`products/{slug}.html`
- [ ] 页面正确隐藏了空组件（PDF/YouTube/项目）

### 8. 部署验证检查
- [ ] 运行`bash deploy-peri-gcb.command`成功
- [ ] 等待2分钟后，在线页面返回HTTP 200
- [ ] 在线页面URL：`https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html`

---

## 检查流程

### 步骤1: 读取JSON文件
```bash
cat {slug}_complete.json
```

### 步骤2: 验证PDF（如果存在）
```bash
# 验证HTTP状态
curl -I {pdf_url}

# 下载并检查内容
curl -o temp_check.pdf {pdf_url}
open temp_check.pdf  # 人工确认内容
```

### 步骤3: 验证YouTube视频（如果存在）
- 访问：`https://www.youtube.com/watch?v={video_id}`
- 确认视频语言、时长、内容

### 步骤4: 验证项目案例（如果存在）
```bash
# 验证项目在产品页面上
curl -s "https://cn.peri.com/products/{slug}.html" | grep "{project_link}"
```

### 步骤5: 检查生成的HTML
```bash
# 检查PDF按钮是否正确隐藏
grep "btn-yellow" products/{slug}.html

# 检查YouTube组件是否正确隐藏
grep "yt-section" products/{slug}.html

# 检查项目组件是否正确隐藏
grep "project-teasers" products/{slug}.html
```

### 步骤6: 验证在线页面
```bash
curl -I "https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html"
```

---

## 不合规处理

如果检查Agent发现任何不合规项：

1. **立即停止**继续处理下一个产品
2. **报告问题**：明确指出哪个检查项失败
3. **要求修正**：等待修正完成
4. **重新检查**：修正后再次运行完整检查
5. **确认通过**：所有检查项通过后才能继续

---

## 检查Agent使用方法

每完成一个产品后，调用检查Agent：

```
Agent(
  description="检查产品合规性",
  prompt=f"""
  检查产品 {slug} 的合规性。
  
  按照 COMPLIANCE_CHECKER.md 中的所有检查清单逐项验证：
  1. 文件命名
  2. PDF链接和内容
  3. YouTube视频
  4. 项目案例
  5. 描述翻译
  6. 基本信息
  7. 页面生成
  8. 部署验证
  
  对于每个检查项，返回：
  - ✅ 通过
  - ❌ 失败（说明原因）
  
  如果有任何失败项，要求立即修正。
  """
)
```

---

## 常见不合规问题

### 问题1: PDF内容不匹配
- **症状**: PDF是其他产品的手册
- **原因**: 只验证了HTTP 200，没有打开PDF确认
- **修正**: 重新搜索正确的PDF

### 问题2: 项目不在产品页面上
- **症状**: 项目链接有效，但不在产品页面上
- **原因**: 从china_projects.json随机选择
- **修正**: 从产品页面HTML提取项目链接

### 问题3: YouTube视频是德语
- **症状**: 视频是德语培训视频
- **原因**: 在YouTube主页搜索，不是频道内搜索
- **修正**: 使用空字符串，隐藏视频组件

### 问题4: 组件未隐藏
- **症状**: 内容为空但页面仍显示组件
- **原因**: rebuild_site_v2.py逻辑错误
- **修正**: 检查脚本的条件判断逻辑

---

**重要**: 检查Agent是质量保证的最后一道防线，必须严格执行所有检查项。
