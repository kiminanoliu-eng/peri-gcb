# Formspree 留言板配置指南

## 📧 如何配置邮箱接收留言

网站已经集成了留言板功能，使用 Formspree 服务。您需要完成以下步骤来激活邮件通知：

---

## 步骤 1：注册 Formspree 账号

1. 访问 [https://formspree.io/](https://formspree.io/)
2. 点击 "Get Started" 或 "Sign Up"
3. 使用您的邮箱注册账号（建议使用您想接收留言的邮箱）
4. 验证邮箱

**免费版限制：** 每月 50 次提交（对于大多数网站足够使用）

---

## 步骤 2：创建新表单

1. 登录 Formspree 后，点击 "+ New Form"
2. 填写表单信息：
   - **Form Name**: `PERI GCB 产品留言板`
   - **Email**: 输入您想接收留言通知的邮箱地址
3. 点击 "Create Form"
4. 创建成功后，您会看到一个 **Form ID**，格式类似：`xyzabc123`

---

## 步骤 3：更新网站配置

找到您的 Form ID 后，需要更新生成脚本：

### 方法 1：手动替换（推荐）

打开 `rebuild_site_v2.py` 文件，找到第 160 行左右：

```python
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST" id="comment-form">
```

将 `YOUR_FORM_ID` 替换为您的实际 Form ID，例如：

```python
<form action="https://formspree.io/f/xyzabc123" method="POST" id="comment-form">
```

### 方法 2：使用脚本自动替换

在终端运行以下命令（将 `xyzabc123` 替换为您的实际 Form ID）：

```bash
cd "/Users/fufu/Documents/Claude/Projects/自动化/创建产品网站"
sed -i '' 's/YOUR_FORM_ID/xyzabc123/g' rebuild_site_v2.py
```

---

## 步骤 4：重新生成网站

更新 Form ID 后，重新生成网站：

```bash
cd "/Users/fufu/Documents/Claude/Projects/自动化/创建产品网站"
python3 rebuild_site_v2.py
```

---

## 步骤 5：部署到 GitHub Pages

```bash
bash deploy.sh
```

或双击 `deploy-peri-gcb.command` 文件

---

## 📬 留言通知邮件格式

当用户提交留言时，您会收到如下格式的邮件：

**主题：** New submission from PERI GCB 产品留言板

**内容：**
```
product: HANDSET Alpha 模块化模板系统
product_url: https://cn.peri.com/products/handset-alpha.html
name: 张三
company: ABC建筑公司
project: 上海某大厦项目
email: zhangsan@example.com
message: 这个产品很适合我们的项目，想了解更多技术细节...
```

---

## 🎨 留言板功能说明

### 用户填写的字段：
- **姓名** (必填)
- **公司** (必填)
- **项目名称** (可选)
- **邮箱** (可选)
- **留言内容** (必填)

### 自动包含的信息：
- 产品名称
- 产品链接

---

## 🔧 高级配置（可选）

### 自定义邮件通知

在 Formspree 控制面板中，您可以：

1. **自定义邮件主题**
   - Settings → Email Notifications → Subject Line
   - 例如：`[PERI产品留言] {{product}}`

2. **添加自动回复**
   - Settings → Autoresponder
   - 开启后，用户提交留言会收到确认邮件

3. **设置多个接收邮箱**
   - Settings → Email Notifications → Additional Recipients
   - 可以添加团队成员的邮箱

4. **查看提交历史**
   - Submissions 标签页可以查看所有历史留言

---

## ⚠️ 注意事项

1. **Form ID 必须正确**：如果 Form ID 错误，留言将无法发送
2. **首次提交需要确认**：第一次有人提交留言时，Formspree 会发送确认邮件，点击确认后才能正常接收
3. **垃圾邮件过滤**：Formspree 自带垃圾邮件过滤功能
4. **免费版限制**：每月 50 次提交，超出后需要升级付费计划

---

## 🆘 故障排查

### 问题 1：提交后没有收到邮件
- 检查 Form ID 是否正确
- 检查垃圾邮件文件夹
- 确认 Formspree 账号邮箱已验证

### 问题 2：提交失败
- 检查网络连接
- 确认 Formspree 服务状态：[https://status.formspree.io/](https://status.formspree.io/)

### 问题 3：超出免费版限制
- 升级到付费计划（$10/月，1000次提交）
- 或使用其他邮件服务（Web3Forms、EmailJS）

---

## 📞 需要帮助？

如果遇到问题，可以：
1. 查看 Formspree 官方文档：[https://help.formspree.io/](https://help.formspree.io/)
2. 联系 Formspree 支持：support@formspree.io

---

**配置完成后，您的网站留言板就可以正常工作了！** 🎉
