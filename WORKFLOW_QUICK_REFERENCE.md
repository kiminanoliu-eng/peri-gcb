# 产品页面生成 - 快速参考

## 流程（6步）

1. **确认产品slug** - 从products_v2.json获取准确的slug
2. **提取数据** - curl获取HTML，grep提取信息
3. **验证数据** - PDF内容、项目案例、视频
4. **创建JSON** - {slug}_complete.json
5. **生成页面** - python3 rebuild_site_v2.py
6. **部署验证** - bash deploy-peri-gcb.command

## 关键检查点

- [ ] 文件名 = `{slug}_complete.json`（完全匹配slug）
- [ ] PDF: 下载并打开确认内容是该产品的手册
- [ ] 项目: 从产品页面HTML提取（不用WebFetch）
- [ ] 视频: 在PERI频道内搜索（英语，≤10分钟）
- [ ] 部署后访问在线页面验证（等待2分钟）

## 常见错误速查

| 错误 | 症状 | 解决方法 |
|------|------|---------|
| 文件名不匹配 | 代码找不到文件 | 从products_v2.json确认slug |
| PDF内容错误 | 用户下载到错误手册 | 打开PDF人工确认内容 |
| 项目不匹配 | 项目不在产品页面上 | 用curl提取产品页面HTML |
| 忘记部署 | 在线页面404 | bash deploy-peri-gcb.command |
| slug使用URL编码 | GitHub Pages返回404 | 使用英文slug，不用中文 |

## 命令速查

```bash
# 1. 确认slug
grep -i "产品名称" products_v2.json | grep "slug"

# 2. 提取产品页面
curl -s "https://cn.peri.com/products/{slug}.html" > temp.html

# 3. 提取项目链接
grep -o 'href="/projects/[^"]*"' temp.html

# 4. 提取项目详情
curl -s "https://cn.peri.com/projects/{project-slug}.html" > project.html
grep -o '<h1[^>]*>[^<]*</h1>' project.html

# 5. 验证PDF
curl -I {pdf_url}  # 检查200
curl -o temp.pdf {pdf_url} && open temp.pdf  # 人工确认内容

# 6. 生成和部署
python3 rebuild_site_v2.py
bash deploy-peri-gcb.command

# 7. 验证在线页面
sleep 120
curl -I "https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html"
```

## PDF验证三步法

1. **验证链接有效**: `curl -I {pdf_url}` 返回200
2. **验证文件类型**: Content-Type是application/pdf
3. **验证内容正确**: 下载并打开PDF，人工确认是该产品的手册

## 核心原则

- ✅ 一次只做1个产品
- ✅ 每个产品完成后让用户验证
- ✅ 验证正确性，不只是有效性
- ✅ 文件名必须与slug完全匹配
- ✅ 宁可没有PDF/视频，也不用错误的

## 详细文档

详细的历史记录、错误分析、经验教训见 `archive/` 目录：
- `archive/workflow/` - 完整工作流程文档
- `archive/errors/` - 错误记录和分析
- `archive/checklists/` - 详细检查清单
- `archive/analysis/` - 问题分析文档
- `archive/reports/` - 状态报告
- `archive/fixes/` - 修复记录
- `archive/setup/` - 配置文档
