# 下一个产品完整处理指南（结合UNO教训）

## 背景文档总结

### 从CONTEXT_SUMMARY.md学到的
1. ❌ 不能依赖WebFetch的不完整输出
2. ❌ 批量处理导致质量下降
3. ✅ 必须用curl验证HTML源代码
4. ✅ 质量优先于速度

### 从PROJECT_RULES.md学到的
1. ✅ 一次处理1个产品，完成后让用户验证
2. ✅ 必须验证项目确实属于该产品
3. ✅ 不能依赖WebFetch的部分输出
4. ✅ 区分"无项目"和"未检查"
5. ✅ PDF链接必须验证内容正确性

### 从UNO问题学到的
1. ❌ 不能擅自修改其他已完成的产品
2. ❌ 不能擅自修改代码
3. ✅ PDF链接必须打开确认内容是该产品的手册
4. ✅ 文件名必须与slug完全匹配
5. ✅ 只做用户明确要求的产品

---

## 完整工作流程（每个产品必须严格遵守）

### 阶段0: 开始前确认

**必须询问用户**：
1. 下一个要做的产品是什么？
2. 产品的slug是什么？

**不要假设，不要自己选择产品！**

---

### 阶段1: 数据收集（从cn.peri.com）

#### 1.1 获取产品页面HTML
```bash
curl -s "https://cn.peri.com/products/{slug}.html" > temp.html
```

**验证**：
- [ ] 文件大小 > 0
- [ ] 包含产品名称

#### 1.2 提取图片URL
```bash
grep 'og:image' temp.html
```

**验证**：
```bash
curl -I {image_url}  # 必须返回200
```

#### 1.3 提取项目案例链接（关键步骤！）

**错误做法**：
- ❌ 使用WebFetch（可能返回不完整结果）
- ❌ 使用缓存的结果
- ❌ 使用其他产品的项目

**正确做法**：
```bash
# 方法1: 提取所有项目链接
grep -o 'href="/projects/[^"]*"' temp.html

# 方法2: 检查项目卡片数量
grep -c "project-teasers__item" temp.html

# 方法3: 提取项目详细信息
grep -A 20 "project-teasers__item-regular-list-headline" temp.html
```

**验证清单**：
- [ ] 项目链接确实在temp.html中
- [ ] 项目数量与页面显示一致
- [ ] 不是港珠澳大桥等不相关项目
- [ ] 不是从china_projects.json随机选择的

#### 1.4 逐个提取项目信息

对每个项目链接：
```bash
curl -s "https://cn.peri.com{project_url}" > project.html

# 提取项目名称
grep -o '<h1[^>]*>[^<]*</h1>' project.html

# 提取位置
grep -o 'location[^>]*>[^<]*</span>' project.html

# 提取描述
grep -A 5 'description' project.html

# 提取图片
grep -o 'og:image.*content="[^"]*"' project.html
```

**验证清单**：
- [ ] 项目名称正确
- [ ] 项目位置正确
- [ ] 项目描述提到了该产品
- [ ] 项目图片URL有效（HTTP 200）
- [ ] 项目链接可访问

---

### 阶段2: YouTube视频搜索

#### 2.1 在PERI频道内搜索
```
1. 访问 https://www.youtube.com/@perigroup
2. 在频道内搜索: {product_name} formwork
3. 不要在YouTube主页搜索！
```

#### 2.2 筛选条件
- 语言: 英语（不要德语培训视频）
- 时长: ≤ 10分钟
- 内容: 产品介绍（不是项目案例）
- 发布时间: 优先最新的

#### 2.3 验证视频
```bash
# 检查视频时长
curl -s "https://www.youtube.com/watch?v={VIDEO_ID}" | grep -o '"approxDurationMs":"[^"]*"'

# 检查视频标题（判断语言）
curl -s "https://www.youtube.com/watch?v={VIDEO_ID}" | grep -o '"title"'
```

**验证清单**：
- [ ] 视频时长 ≤ 10分钟
- [ ] 视频语言是英语
- [ ] 视频内容是该产品的介绍
- [ ] 视频来自PERI官方频道

---

### 阶段3: PDF链接查找（UNO的关键教训）

#### 3.1 搜索顺序
```bash
# 1. cn.peri.com
curl -s "https://cn.peri.com/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 2. www.peri.com/en
curl -s "https://www.peri.com/en/products/{slug}.html" | grep -o 'https://[^"]*\.pdf'

# 3. 其他区域网站
# peri.id (印尼)
# peri.com.au (澳大利亚)
# peri.co.za (南非)
# peri.ltd.uk (英国)
```

#### 3.2 PDF验证（最关键！UNO的教训）

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

# 人工检查:
# 1. 打开PDF文件
# 2. 确认PDF内容确实是该产品的手册
# 3. 不是其他产品的手册
# 4. 不是意大利语或其他不相关的PDF
```

**验证清单**：
- [ ] PDF链接返回HTTP 200
- [ ] Content-Type是application/pdf
- [ ] **PDF内容确实是该产品的手册**（打开PDF人工确认）
- [ ] PDF语言合适（优先英语或中文）
- [ ] PDF不是其他产品的手册
- [ ] PDF来自PERI官方网站（不是第三方）

**重要原则**：
- ✅ 宁可没有PDF（使用空字符串 `""`），也不要使用错误的PDF
- ❌ 不要只检查HTTP 200就使用
- ❌ 不要使用来自peri.it等不确定来源的PDF（除非确认内容正确）

---

### 阶段4: 创建完整JSON文件

#### 4.1 文件命名（UNO的教训）

**格式**: `{slug}_complete.json`

**关键规则**：
- 文件名必须与products_v2.json中的slug**完全匹配**
- 使用连字符 `-` 而不是下划线 `_`（如果slug中有连字符）
- 不要使用简短版本

**示例**：
```
slug: "gridflex-deckenschalung"
文件名: "gridflex-deckenschalung_complete.json"  ✅

文件名: "gridflex_complete.json"  ❌ 错误！
文件名: "gridflex-deckenschalung.json"  ❌ 缺少_complete
```

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

**验证清单**：
- [ ] slug与products_v2.json完全匹配
- [ ] 所有7种语言翻译完整
- [ ] projects数组包含所有提取的项目
- [ ] pdf_link是验证过内容的URL或空字符串
- [ ] youtube_video_id是验证过的视频ID或空字符串

---

### 阶段5: 生成和验证

#### 5.1 重建网站
```bash
cd /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站
python3 rebuild_site_v2.py
```

**检查输出**：
- [ ] 显示"✅ Done!"
- [ ] 没有错误信息

#### 5.2 验证生成的HTML
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

**验证清单**：
- [ ] 产品页面生成成功
- [ ] PDF链接正确（如果有）
- [ ] YouTube视频嵌入正确（如果有）
- [ ] 项目案例数量正确

#### 5.3 最终验证清单
- [ ] 图片显示正确
- [ ] PDF链接指向正确的PDF（不是#downloads）
- [ ] YouTube视频可播放
- [ ] 项目案例是该产品的项目
- [ ] 所有链接都有效

---

### 阶段6: 部署

```bash
bash deploy-peri-gcb.command
```

**等待1-2分钟后访问网站验证**：
- [ ] 产品页面在线可访问
- [ ] 图片加载正常
- [ ] PDF链接可点击
- [ ] YouTube视频可播放
- [ ] 项目案例链接可访问

---

## 关键检查点总结

### 项目案例（最容易出错）
1. ✅ 必须从产品页面的HTML源代码提取
2. ✅ 使用curl，不使用WebFetch
3. ✅ 验证项目确实在该产品页面上
4. ❌ 不要使用随机项目
5. ❌ 不要使用其他产品的项目
6. ❌ 不要使用缓存的结果

### PDF链接（UNO的教训）
1. ✅ 验证链接有效（HTTP 200）
2. ✅ **验证内容正确**（打开PDF确认是该产品的手册）
3. ❌ 不要只检查链接有效就使用
4. ❌ 不要使用其他产品的PDF
5. ✅ 找不到正确的PDF就用空字符串 `""`
6. ❌ 不要使用来自不确定来源的PDF

### 文件命名（UNO的教训）
1. ✅ 文件名必须与slug完全匹配
2. ✅ 格式：`{slug}_complete.json`
3. ❌ 不要使用简短版本
4. ❌ 不要使用下划线替代连字符

### 行为准则（UNO的教训）
1. ✅ 只做用户要求的产品
2. ❌ 不擅自修改其他产品
3. ❌ 不擅自修改代码
4. ✅ 有疑问立即询问用户
5. ✅ 一个产品完成后让用户验证

---

## 遇到问题时的处理

### 如果找不到项目案例
1. ❌ 不要说"无项目案例"
2. ✅ 说"WebFetch未找到项目，正在用curl验证"
3. ✅ 用curl检查HTML源代码
4. ✅ 如实报告："确认HTML中没有项目卡片"或"找到X个项目"

### 如果找不到PDF
1. ❌ 不要使用错误的PDF
2. ✅ 搜索多个区域网站
3. ✅ 如实报告："未找到该产品的PDF"
4. ✅ 使用空字符串 `""`

### 如果找不到YouTube视频
1. ✅ 在PERI频道内搜索
2. ✅ 尝试不同的关键词组合
3. ✅ 如实报告："未找到合适的英语产品介绍视频"
4. ✅ 使用空字符串 `""`

---

## 下一步行动

### 等待用户指示
1. 询问用户：下一个要做的产品是什么？
2. 确认产品的slug
3. 开始按照上述流程处理

### 不要做的事
- ❌ 不要自己选择产品
- ❌ 不要批量处理多个产品
- ❌ 不要修改其他已完成的产品
- ❌ 不要修改代码

---

**准备就绪，等待用户指示下一个产品。**
