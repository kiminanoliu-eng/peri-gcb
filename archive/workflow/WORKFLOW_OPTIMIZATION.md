# 工作流程优化方案

## 当前问题总结

### 1. 缩略图显示问题（全站范围）
- **问题**: 不仅楼板模板分类页面，所有分类页面都可能存在缩略图显示为扳手图标的问题
- **影响范围**: 
  - 建筑模板系统（墙模、柱模、楼板模板、配件）
  - 脚手架/支撑系统
  - 土木工程
  - 工程服务
  - 软件/应用
  - 模板面板/胶合板

### 2. 部署流程问题
- **根本原因**: 
  1. `rebuild_site_v2.py` 生成文件到 `mnt/创建产品网站/`
  2. Git追踪根目录的 `categories/`, `products/`, `index.html`, `search.html`
  3. 部署前需要手动复制文件
  
- **当前工作流程**:
  ```bash
  # 步骤1: 重建网站
  python3 rebuild_site_v2.py
  
  # 步骤2: 复制文件到Git追踪目录
  cp -r mnt/创建产品网站/categories/* categories/
  cp -r mnt/创建产品网站/products/* products/
  cp mnt/创建产品网站/index.html .
  cp mnt/创建产品网站/search.html .
  
  # 步骤3: 部署
  bash deploy-peri-gcb.command
  ```

### 3. YouTube视频搜索流程问题
- **旧流程**: 在YouTube主页搜索产品名称
- **新要求**: 在PERI YouTube频道内搜索产品名称
- **频道URL**: https://www.youtube.com/@perigroup

## 优化方案

### 方案1: 修改rebuild_site_v2.py输出路径（推荐）

**优点**:
- 一次性解决问题
- 无需手动复制文件
- 减少出错可能

**实施**:
```python
# 修改 rebuild_site_v2.py 第39-40行
BASE = os.path.dirname(os.path.abspath(__file__))
SITE = BASE  # 直接输出到根目录，而不是 os.path.join(BASE, 'mnt', '创建产品网站')
CATS_DIR = os.path.join(SITE, 'categories')
PRODS_DIR = os.path.join(SITE, 'products')
```

**新工作流程**:
```bash
# 一步完成：重建并部署
python3 rebuild_site_v2.py && bash deploy-peri-gcb.command
```

### 方案2: 创建自动化脚本

创建 `rebuild_and_deploy.sh`:
```bash
#!/bin/bash
echo "🔨 重建网站..."
python3 rebuild_site_v2.py

echo "📋 复制文件到Git目录..."
cp -r mnt/创建产品网站/categories/* categories/
cp -r mnt/创建产品网站/products/* products/
cp mnt/创建产品网站/index.html .
cp mnt/创建产品网站/search.html .

echo "🚀 部署到GitHub..."
bash deploy-peri-gcb.command
```

## 批量修复缩略图问题的策略

### Token优化策略

**不推荐的方式**（浪费Token）:
- ❌ 逐个分类页面检查
- ❌ 重复读取相同的数据文件
- ❌ 多次运行rebuild脚本

**推荐的方式**（节省Token）:
1. ✅ 一次性重建整个网站（已包含所有分类页面）
2. ✅ 验证products_v2.json中的图片URL是否正确
3. ✅ 批量复制和部署

### 具体执行步骤

```bash
# 步骤1: 验证数据源正确性
python3 -c "
import json
with open('products_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
# 检查所有分类的图片URL
for cat_key, cat in data.items():
    if 'subcategories' in cat:
        for sc_key, sc in cat['subcategories'].items():
            for p in sc['products']:
                if not p[3] or 'placeholder' in p[3].lower():
                    print(f'⚠️  {p[1]}: 缺少图片URL')
    else:
        for p in cat.get('products', []):
            if not p[3] or 'placeholder' in p[3].lower():
                print(f'⚠️  {p[1]}: 缺少图片URL')
"

# 步骤2: 一次性重建所有页面
python3 rebuild_site_v2.py

# 步骤3: 复制到Git目录
cp -r mnt/创建产品网站/categories/* categories/
cp -r mnt/创建产品网站/products/* products/
cp mnt/创建产品网站/index.html .
cp mnt/创建产品网站/search.html .

# 步骤4: 部署
bash deploy-peri-gcb.command
```

## YouTube视频搜索新流程

### 更新rebuild_site_v2.py中的YouTube ID查找逻辑

**当前问题**: 
- YT_IDS字典是硬编码的
- 需要手动在PERI频道搜索并更新

**新流程文档**:

1. **访问PERI频道**: https://www.youtube.com/@perigroup
2. **搜索产品名称**: 在频道内搜索框输入产品英文名 + "formwork"
3. **筛选条件**:
   - ✅ 视频语言：英语
   - ✅ 视频长度：10分钟以内
   - ✅ 视频内容：产品介绍/演示
4. **提取视频ID**: 从URL中提取（例如：`watch?v=CgOEI3YtG_E` → `CgOEI3YtG_E`）
5. **更新YT_IDS字典**: 在rebuild_site_v2.py第14-36行

**示例**:
```python
# 在PERI频道搜索 "SKYDECK formwork"
# 找到视频: https://www.youtube.com/watch?v=CgOEI3YtG_E
# 更新字典:
YT_IDS = {
    'skydeck-slab-formwork': 'CgOEI3YtG_E',
    # ...
}
```

## 质量保证检查清单

### 重建前检查
- [ ] products_v2.json中所有产品都有有效的图片URL
- [ ] 图片URL可以通过curl访问（HTTP 200）
- [ ] YouTube视频ID已在PERI频道验证

### 重建后检查
- [ ] 所有分类页面生成成功
- [ ] 所有产品页面生成成功
- [ ] 本地文件已复制到Git目录

### 部署后检查
- [ ] GitHub Pages构建成功
- [ ] 随机抽查3-5个分类页面的缩略图
- [ ] 随机抽查3-5个产品页面的YouTube视频

## 下一步行动

### 立即执行（高优先级）
1. ✅ 修改rebuild_site_v2.py输出路径到根目录
2. ✅ 一次性重建整个网站
3. ✅ 部署并验证所有分类页面

### 后续优化（中优先级）
1. 为剩余153个产品添加YouTube视频ID
2. 验证所有产品的PDF链接
3. 补充缺失的项目案例

### 长期改进（低优先级）
1. 创建自动化测试脚本验证图片URL
2. 建立YouTube视频ID数据库
3. 实现增量构建（只重建修改的页面）

---

**文档创建日期**: 2026-04-06
**最后更新**: 2026-04-06
**状态**: 待执行
