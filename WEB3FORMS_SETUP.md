# Web3Forms 配置指南（推荐）

## 🎯 为什么选择 Web3Forms？

✅ **完全免费** - 无限制提交次数  
✅ **无需注册** - 只需要一个 Access Key  
✅ **简单快速** - 2分钟完成配置  
✅ **自动过滤** - 内置垃圾邮件防护  
✅ **即时通知** - 留言立即发送到邮箱  

---

## 📋 配置步骤（3步完成）

### 步骤 1：获取 Access Key

1. 打开浏览器，访问：**https://web3forms.com**

2. 点击页面上的 **"Get Started Free"** 或 **"Create Access Key"** 按钮

3. 输入你想接收留言通知的邮箱地址

4. 点击 **"Create Access Key"**

5. 复制显示的 **Access Key**（格式类似：`a1b2c3d4-e5f6-7890-abcd-ef1234567890`）

6. 检查邮箱，点击验证链接（重要！）

---

### 步骤 2：配置网站

打开终端，运行以下命令：

```bash
cd "/Users/fufu/Documents/Claude/Projects/自动化/创建产品网站"
bash configure_web3forms.sh YOUR_ACCESS_KEY
```

**将 `YOUR_ACCESS_KEY` 替换为你刚才复制的 Access Key**

示例：
```bash
bash configure_web3forms.sh a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

脚本会自动：
- ✅ 更新 rebuild_site_v2.py
- ✅ 重新生成所有网页
- ✅ 配置留言板功能

---

### 步骤 3：部署网站

```bash
bash deploy.sh
```

或双击 `deploy-peri-gcb.command` 文件

---

## 🎉 完成！测试留言板

1. 等待 1-2 分钟让 GitHub Pages 部署完成

2. 访问你的网站：https://kiminanoliu-eng.github.io/peri-gcb/

3. 点击任意产品页面

4. 滚动到"产品留言板"部分

5. 填写表单并提交

6. 检查你的邮箱 - 应该会收到留言通知！

---

## 📧 邮件通知格式

你会收到如下格式的邮件：

**主题：** PERI产品留言: [产品名称]

**内容：**
```
姓名: 张三
公司: ABC建筑公司
项目名称: 上海某大厦项目
邮箱: zhangsan@example.com
留言内容: 这个产品很适合我们的项目...

产品: HANDSET Alpha 模块化模板系统
产品链接: https://cn.peri.com/products/handset-alpha.html
```

---

## 🔧 高级配置（可选）

### 自定义邮件模板

访问 https://web3forms.com/dashboard 登录后可以：
- 自定义邮件主题
- 添加自动回复
- 设置多个接收邮箱
- 查看提交历史
- 下载提交数据

### 更换邮箱地址

如果想更换接收邮箱：
1. 访问 https://web3forms.com
2. 用新邮箱创建新的 Access Key
3. 重新运行配置脚本：
   ```bash
   bash configure_web3forms.sh NEW_ACCESS_KEY
   bash deploy.sh
   ```

---

## ⚡ 一键完成（复制粘贴）

获取 Access Key 后，复制以下命令并替换 `YOUR_ACCESS_KEY`：

```bash
cd "/Users/fufu/Documents/Claude/Projects/自动化/创建产品网站"
bash configure_web3forms.sh YOUR_ACCESS_KEY
bash deploy.sh
```

---

## 🆘 故障排查

### 问题 1：没有收到邮件
- ✅ 检查垃圾邮件文件夹
- ✅ 确认已点击 Web3Forms 发送的验证邮件
- ✅ 检查 Access Key 是否正确配置

### 问题 2：提交失败
- ✅ 检查网络连接
- ✅ 确认 Access Key 格式正确
- ✅ 查看浏览器控制台错误信息

### 问题 3：想要更多功能
- 访问 https://web3forms.com/docs 查看完整文档
- 支持自定义字段、文件上传、Webhook 等

---

## 📊 Web3Forms vs Formspree

| 特性 | Web3Forms | Formspree |
|------|-----------|-----------|
| 价格 | 完全免费 | 免费版 50次/月 |
| 注册 | 不需要 | 需要账号 |
| 提交限制 | 无限制 | 50次/月（免费版） |
| 配置难度 | ⭐ 简单 | ⭐⭐ 中等 |
| 垃圾邮件过滤 | ✅ | ✅ |
| 自定义 | ✅ | ✅ |

---

## 📞 需要帮助？

- Web3Forms 文档：https://web3forms.com/docs
- Web3Forms 支持：support@web3forms.com
- 常见问题：https://web3forms.com/faq

---

**准备好了吗？访问 https://web3forms.com 获取你的 Access Key！** 🚀
