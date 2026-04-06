# 🚀 快速配置指南

## 当前状态

✅ 网站已生成，包含以下更新：
- 产品图片已从 cn.peri.com 更新
- 留言板功能已集成（使用 Web3Forms）
- 示例项目链接已修复（15个项目）

⚠️ **待完成：** 配置 Web3Forms Access Key 以接收留言通知

---

## 📋 配置 Web3Forms（3 步完成）

### 步骤 1：获取 Access Key

1. 访问 https://web3forms.com
2. 点击 "Get Started Free"
3. 输入你想接收留言的邮箱地址
4. 点击 "Create Access Key"
5. 复制 **Access Key**（格式如：`a1b2c3d4-e5f6-7890-abcd-ef1234567890`）
6. 检查邮箱并点击验证链接

### 步骤 2：运行配置脚本

```bash
cd "/Users/fufu/Documents/Claude/Projects/自动化/创建产品网站"
bash configure_web3forms.sh YOUR_ACCESS_KEY
```

将 `YOUR_ACCESS_KEY` 替换为你的实际 Access Key

### 步骤 3：部署网站

```bash
bash deploy.sh
```

或双击 `deploy-peri-gcb.command`

---

## 🎯 一键完成（复制粘贴）

获取 Access Key 后，运行：

```bash
cd "/Users/fufu/Documents/Claude/Projects/自动化/创建产品网站"
bash configure_web3forms.sh YOUR_ACCESS_KEY  # 替换为你的 Access Key
bash deploy.sh
```

---

## 📁 项目文件说明

| 文件 | 说明 |
|------|------|
| `rebuild_site_v2.py` | 网站生成脚本 |
| `products_v2.json` | 产品数据（已更新图片） |
| `china_projects.json` | 项目数据（15个项目） |
| `configure_web3forms.sh` | Web3Forms 配置脚本 |
| `deploy.sh` | 部署脚本 |
| `WEB3FORMS_SETUP.md` | 详细配置指南（推荐阅读） |
| `UPDATE_SUMMARY.md` | 更新摘要 |

---

## ✨ 完成的更新

### 1. 产品图片 ✅
- 从 cn.peri.com 自动提取正确图片
- 更新了 products_v2.json

### 2. 留言板功能 ✅
- 替换了询价表单
- 使用 Web3Forms（完全免费，无限制）
- 字段：姓名、公司、项目、邮箱、留言
- 支持 7 种语言
- 自动邮件通知

### 3. 项目链接 ✅
- 修复了 404 错误
- 新增 15 个真实项目
- 所有链接指向 cn.peri.com

---

## 🧪 测试留言板

部署后：
1. 访问任意产品页面
2. 滚动到"产品留言板"部分
3. 填写表单并提交
4. 检查邮箱是否收到通知

---

## 📞 需要帮助？

- 详细配置：查看 `WEB3FORMS_SETUP.md`
- 更新说明：查看 `UPDATE_SUMMARY.md`
- Web3Forms 文档：https://web3forms.com/docs

---

## ⚡ 如果不想配置 Web3Forms

你也可以暂时跳过配置，直接部署：

```bash
bash deploy.sh
```

留言板会显示，但提交时会提示需要配置 Access Key。你可以随时回来配置。

---

**准备好了吗？访问 https://web3forms.com 获取你的 Access Key！** 🎉
