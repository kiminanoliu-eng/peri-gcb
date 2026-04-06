# PDF获取方法

## 问题
PERI产品的PDF链接在网页上是动态加载的，无法通过简单的curl或WebFetch直接提取。

## 解决方法

### 步骤1: 访问peri.ltd.uk产品页面
```bash
curl -s "https://www.peri.ltd.uk/products/{slug}.html" > page.html
```

### 步骤2: 提取REST API下载ID
PDF下载链接格式为: `/.rest/downloads/{ID}`

```bash
grep -o '/.rest/downloads/[0-9]*' page.html | sort -u
```

示例输出:
```
/.rest/downloads/78345
/.rest/downloads/80534
```

### 步骤3: 构建完整PDF URL
```
https://www.peri.ltd.uk/.rest/downloads/{ID}
```

### 步骤4: 验证PDF
```bash
# 检查HTTP状态码
curl -I "https://www.peri.ltd.uk/.rest/downloads/{ID}"

# 下载PDF
curl -s "https://www.peri.ltd.uk/.rest/downloads/{ID}" -o temp.pdf

# 验证文件类型
file temp.pdf

# 提取文本验证内容
strings temp.pdf | grep -i "{产品关键词}"
```

### 步骤5: 查看PDF标题（如果有多个PDF）
```bash
curl -s "https://www.peri.ltd.uk/products/{slug}.html" | grep -B5 "/.rest/downloads/{ID}"
```

这会显示PDF的标题，帮助选择正确的PDF。

## 注意事项

1. **产品名称可能不完全匹配**: 
   - 例如: `vario-quattro-column-formwork` 的PDF可能在 `quattro-column-formwork` 页面上
   - 如果在产品页面找不到PDF，尝试搜索相似的产品名称

2. **多个PDF的选择**:
   - 查看HTML中PDF的标题
   - 选择与产品名称最匹配的PDF
   - 下载并验证内容

3. **验证PDF内容**:
   - 使用 `strings` 命令提取文本
   - 检查是否包含产品名称或相关关键词
   - 确认不是其他产品的PDF

## 实际案例

### 案例1: vario-gt-24-girder-wall-formwork
```bash
# 访问页面
curl -s "https://www.peri.ltd.uk/products/vario-gt-24-girder-wall-formwork.html" > page.html

# 提取下载ID
grep -o '/.rest/downloads/[0-9]*' page.html
# 输出: /.rest/downloads/78345
#       /.rest/downloads/80534

# 查看标题
curl -s "https://www.peri.ltd.uk/products/vario-gt-24-girder-wall-formwork.html" | grep -B5 "/.rest/downloads/80534"
# 输出显示: "VARIO GT 24 | Girder Wall Formwork"

# 最终PDF链接
https://www.peri.ltd.uk/.rest/downloads/80534
```

### 案例2: vario-quattro-column-formwork
```bash
# 在原产品页面找不到PDF
curl -s "https://www.peri.ltd.uk/products/vario-quattro-column-formwork.html" | grep -o '/.rest/downloads/[0-9]*'
# 输出: (空)

# 尝试相似产品名称
curl -s "https://www.peri.ltd.uk/products/quattro-column-formwork.html" | grep -o '/.rest/downloads/[0-9]*'
# 输出: /.rest/downloads/76458
#       /.rest/downloads/80454

# 查看标题
curl -s "https://www.peri.ltd.uk/products/quattro-column-formwork.html" | grep -B5 "/.rest/downloads/80454"
# 输出显示: "QUATTRO | Column Formwork"

# 最终PDF链接
https://www.peri.ltd.uk/.rest/downloads/80454
```

## 总结

**核心方法**: 
1. 访问 `https://www.peri.ltd.uk/products/{slug}.html`
2. 提取 `/.rest/downloads/{ID}`
3. 构建完整URL: `https://www.peri.ltd.uk/.rest/downloads/{ID}`
4. 验证内容正确性

**如果找不到PDF**:
- 尝试简化产品名称（去掉vario-前缀等）
- 搜索相似产品页面
- 检查是否有多个PDF，选择标题最匹配的

---

**创建日期**: 2026-04-06  
**最后更新**: 2026-04-06
