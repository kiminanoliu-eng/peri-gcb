# PERI GCB 网站部署指南 / Deployment Guide

## 中文说明 🇨🇳

### 快速部署（一条命令搞定）

你的网站已经完全生成好了！所有 177 个 HTML 文件都在这个文件夹里。现在只需要一条命令就能推送到 GitHub：

#### Mac/Linux 用户：
打开终端，进入这个文件夹，然后运行：
```bash
bash deploy.sh
```

#### Windows 用户：
打开 PowerShell，进入这个文件夹，然后运行：
```powershell
.\deploy.ps1
```

**就这样！** 脚本会自动：
- ✅ 初始化 Git 仓库（如果还没有的话）
- ✅ 暂存所有 177 个文件
- ✅ 创建一条提交
- ✅ 推送到 GitHub

### 几分钟内...
1. GitHub Actions 会自动构建你的网站
2. ~1-2 分钟后，你的网站就活跃了！
3. 访问：https://kiminanoliu-eng.github.io/peri-gcb/

### 需要 Git 凭证吗？
如果系统要求输入密码/凭证：
- **优先选项：** 使用 GitHub 的 Personal Access Token (PAT)
- **最简单的方法：** 使用 GitHub 登录 (如果你在 Mac 的钥匙链里保存过 GitHub 凭证)

---

## English Instructions 🇬🇧

### Quick Deploy (One Command)

Your website is completely generated! All 177 HTML files are ready in this folder. Deploy to GitHub with a single command:

#### Mac/Linux:
Open Terminal, navigate to this folder, and run:
```bash
bash deploy.sh
```

#### Windows:
Open PowerShell, navigate to this folder, and run:
```powershell
.\deploy.ps1
```

**That's it!** The script will automatically:
- ✅ Initialize Git repo (if needed)
- ✅ Stage all 177 files
- ✅ Create a commit
- ✅ Push to GitHub

### Within minutes:
1. GitHub Actions automatically builds your site
2. After ~1-2 minutes, your site is live!
3. Visit: https://kiminanoliu-eng.github.io/peri-gcb/

### Need Git Credentials?
If prompted for password/credentials:
- **Preferred:** Use GitHub Personal Access Token (PAT)
- **Easiest:** Use GitHub login (if you've saved credentials to your keychain on Mac)

---

## What's Included

```
创建产品网站/
├── index.html                    (Homepage)
├── categories/
│   ├── wall-formwork.html        (12 category pages)
│   ├── scaffolding.html
│   └── ... (10 more)
├── products/
│   ├── trio-rahmenschalung.html  (165 product pages)
│   ├── vario-gt-24.html
│   └── ... (163 more)
├── deploy.sh                     (Mac/Linux deployment)
├── deploy.ps1                    (Windows deployment)
└── DEPLOY_GUIDE.md              (This file)
```

## Troubleshooting

### "git: command not found"
Install Git: https://git-scm.com/download

### "fatal: 'origin' does not appear to be a 'git' repository"
The script will auto-fix this, but you can also run:
```bash
git remote add origin https://github.com/kiminanoliu-eng/peri-gcb.git
```

### "Permission denied" on deploy.sh (Mac/Linux)
Run:
```bash
chmod +x deploy.sh
bash deploy.sh
```

### "fatal: Authentication failed"
GitHub changed from password authentication to tokens. Use a Personal Access Token instead:
1. Go to https://github.com/settings/tokens
2. Create a new token with `repo` scope
3. Use the token as your password when prompted

---

## Next Steps

After deployment, the site will be live at:
🌐 **https://kiminanoliu-eng.github.io/peri-gcb/**

To add more content or make changes:
1. Edit the HTML files locally
2. Run `bash deploy.sh` (or `.\deploy.ps1`) again
3. Changes deploy automatically in ~1-2 minutes

---

**Questions?** All automation is built in — just run the deploy script! 🚀
