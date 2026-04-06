# PDF搜索方法总结

**日期**: 2026-04-06
**状态**: 已验证有效

---

## ✅ 方法1：PERI UK网站直接提取（推荐）

### 步骤
1. 访问 `https://www.peri.ltd.uk/products/{product-slug}.html`
2. 提取 `/.rest/downloads/{ID}` 链接
3. 使用完整URL：`https://www.peri.ltd.uk/.rest/downloads/{ID}`

### ⚠️ 重要：Slug变体尝试策略

**问题：** 中国网站和UK网站的产品slug可能不一致

**解决方案：** 必须尝试多个slug变体，按以下顺序：

1. **原始slug** - 直接使用中国网站的slug
2. **移除后缀** - 去掉产品类型后缀
   - `prokit-ep-110-fall-protection` → `prokit`
   - `peri-up-easy-frame-scaffolding` → `peri-up-easy-scaffolding`
3. **简化版本** - 只保留核心产品名
   - `domino-panel-formwork` → `domino`
4. **添加常见后缀** - 尝试添加UK网站常用后缀
   - 添加 `-scaffolding`
   - 添加 `-formwork`

### 示例
- PROKIT EP 110:
  - ❌ `prokit-ep-110-fall-protection` (中国slug)
  - ✅ `prokit` (简化版本)
  
- PERI UP Easy:
  - ❌ `peri-up-easy-frame-scaffolding` (中国slug)
  - ✅ `peri-up-easy-scaffolding` (移除"frame")

- DOMINO:
  - ✅ `domino-panel-formwork` (原始slug有效)
  - ✅ `domino` (简化版本也有效)

### 实施代码
```bash
# 尝试多个slug变体
slugs=(
  "$original_slug"
  "${original_slug%-*}"  # 移除最后一个词
  "${original_slug%%-*}" # 只保留第一个词
)

for slug in "${slugs[@]}"; do
  result=$(curl -s "https://www.peri.ltd.uk/products/$slug.html" | grep -o '/.rest/downloads/[0-9]*' | head -1)
  if [ -n "$result" ]; then
    echo "Found: $result"
    break
  fi
done
```

### 优点
- 直接、可靠
- PDF质量高（官方文档）
- 链接稳定

### 缺点
- 需要尝试多个slug变体
- 不是所有产品在UK网站都有

---

## ✅ 方法2：Google搜索（备选）

### 搜索公式
```
peri {产品英文名} pdf
```

### 示例
- LIWA: `peri liwa pdf`
  - 结果: https://www.peri.co.th/dam/jcr:bf8b3cd6-eeb5-4529-bf7e-c1d5148f8a36/liwa.pdf
  - 状态: ✅ 有效 (HTTP 200, 4.8MB)

### 为什么这个方法有效
1. **覆盖全球**: Google索引了PERI所有区域网站的PDF
2. **准确性高**: 搜索结果直接指向产品手册

### 局限性
⚠️ **WebSearch工具效果不佳**: 经常返回Scribd、ilovepdf等第三方网站，而不是PERI官方PDF。这是工具限制，不是方法问题。

---

## 📋 标准流程

### 每个产品的PDF搜索步骤

1. **优先尝试PERI UK网站**
   ```bash
   curl -s "https://www.peri.ltd.uk/products/{slug}.html" | grep -o '/.rest/downloads/[0-9]*' | head -1
   ```

2. **如果UK网站没有，尝试其他区域**
   - .com (美国)
   - .ca (加拿大)
   - .de (德国)
   - .co.th (泰国)

3. **验证PDF链接**
   ```bash
   curl -I {pdf_url}
   # 必须返回 HTTP 200
   # Content-Type 必须是 application/pdf
   ```

4. **如果找不到或不确定**
   - 使用空字符串 `""`
   - 不要使用错误的PDF

---

## 🎯 关键原则

1. **Google搜索是首选方法** - 不是最后的手段
2. **简单优于复杂** - 一次搜索胜过多次手动查找
3. **验证内容是强制的** - HTTP 200不等于内容正确
4. **宁缺毋滥** - 没有PDF好过错误的PDF

---

## 📊 效果对比

| 方法 | 时间 | 成功率 | 复杂度 |
|------|------|--------|--------|
| Google搜索 | 1分钟 | 高 | 低 |
| 手动遍历 | 10-15分钟 | 中 | 高 |

---

**最后更新**: 2026-04-06
**适用于**: 所有后续产品的PDF搜索
