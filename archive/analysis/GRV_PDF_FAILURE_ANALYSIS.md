# GRV PDF搜索失败分析

**日期**: 2026-04-06
**产品**: GRV 曲面模板 (grv-rundschalung)

---

## 问题

第一次搜索时错误地说"UK网站没有GRV的PDF"，但实际上UK网站有PDF。

---

## 失败原因

### 1. Slug语言不匹配

**中国网站slug**: `grv-rundschalung` (德语)
- `rundschalung` = 德语，意思是"circular formwork"（圆形模板/曲面模板）

**UK网站slug**: `grv-circular-formwork` (英文)
- 使用英文翻译，不是德语原词

### 2. 尝试的变体不够全面

我只尝试了：
1. ❌ `grv-rundschalung` (原始德语slug)
2. ❌ `grv-curved-formwork` (错误的英文翻译 - curved不是circular)
3. ❌ `grv` (简化版本)

**没有尝试**：
- ✅ `grv-circular-formwork` (正确的英文翻译)

### 3. 翻译错误

我将 `rundschalung` 翻译成了 `curved-formwork`，但正确的翻译应该是 `circular-formwork`。
- `curved` = 弯曲的
- `circular` = 圆形的、环形的

---

## 正确的PDF

**URL**: https://www.peri.ltd.uk/products/grv-circular-formwork.html
**PDF**: https://www.peri.ltd.uk/.rest/downloads/79925
**文件名**: GRV_Circular_Formwork-79925.pdf
**大小**: 10.6MB

---

## 改进措施

### 1. 必须尝试英文翻译变体

对于德语产品名，必须尝试英文翻译：
- `rundschalung` → `circular-formwork`
- `saeulenschalung` → `column-formwork`
- `wandschalung` → `wall-formwork`

### 2. 使用准确的翻译

不要猜测翻译，应该：
- 查询德语-英语词典
- 参考PERI官方英文网站的产品名称
- 尝试多个可能的英文翻译

### 3. 扩大搜索范围

对于每个产品，尝试顺序：
1. 原始slug
2. **英文翻译变体**（新增）
3. 移除后缀
4. 简化版本
5. 常见后缀变体

---

## 常见德语产品术语翻译

| 德语 | 英语 | 中文 |
|------|------|------|
| rundschalung | circular-formwork | 圆形模板/曲面模板 |
| saeulenschalung | column-formwork | 柱模 |
| wandschalung | wall-formwork | 墙模 |
| deckenschalung | slab-formwork | 楼板模板 |
| geruest | scaffolding | 脚手架 |

---

## 教训

1. **不要假设UK网站没有PDF** - 必须尝试所有合理的slug变体
2. **语言翻译很重要** - 德语产品名需要准确的英文翻译
3. **一次性做对** - 避免需要用户指出错误后再修正

---

**最后更新**: 2026-04-06
**状态**: 已修正，PDF已添加到grv-rundschalung_complete.json
