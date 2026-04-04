# PERI GCB 产品网站

这是一个自动生成的 PERI GCB 产品展示网站，包含 160+ 产品页面和完整的分类导航系统。

## 📁 项目结构

```
创建产品网站/
├── index.html              # 首页
├── search.html             # 搜索页面
├── categories/             # 分类页面（19个）
│   ├── wall-formwork.html
│   ├── column-formwork.html
│   ├── slab-formwork.html
│   └── ...
├── products/               # 产品页面（160+个）
│   ├── trio-rahmenschalung.html
│   ├── vario-gt-24.html
│   └── ...
├── products_v2.json        # 产品数据源
├── rebuild_site_v2.py      # 网站生成脚本
├── deploy.sh               # Mac/Linux 部署脚本
├── deploy.ps1              # Windows 部署脚本
├── deploy-peri-gcb.command # Mac 一键部署
└── DEPLOY_GUIDE.md         # 部署指南
```

## 🎯 产品分类

### 6 大主分类
1. **建筑模板系统** - 墙模、柱模、楼板模板、通用配件
2. **脚手架系统** - 各类脚手架产品
3. **支撑系统** - 支撑和支架产品
4. **爬架系统** - 爬升系统
5. **工程施工套件** - 工程配套产品
6. **数字化解决方案** - 软件和数字化服务

### 统计数据
- **160+ 产品页面**
- **19 个分类页面**
- **多语言支持**：中文、英文、西班牙语、德语

## 🔧 如何重新生成网站

如果你修改了 `products_v2.json` 数据文件，可以重新生成整个网站：

```bash
python3 rebuild_site_v2.py
```

脚本会自动生成：
- ✅ 首页 (index.html)
- ✅ 搜索页面 (search.html)
- ✅ 所有分类页面 (categories/)
- ✅ 所有产品页面 (products/)

## 🚀 如何部署

### 方式 1：一键部署（Mac）
双击 `deploy-peri-gcb.command` 文件

### 方式 2：命令行部署

**Mac/Linux:**
```bash
bash deploy.sh
```

**Windows:**
```powershell
.\deploy.ps1
```

部署脚本会自动：
1. 初始化 Git 仓库（如果需要）
2. 添加所有文件到暂存区
3. 创建提交
4. 推送到 GitHub

### 部署后访问
网站将在 1-2 分钟内发布到：
🌐 **https://kiminanoliu-eng.github.io/peri-gcb/**

## 📝 修改产品数据

所有产品数据存储在 `products_v2.json` 文件中。

### 数据结构示例
```json
{
  "建筑模板系统": {
    "slug": "building-formwork",
    "en": "Building Formwork Systems",
    "subcategories": {
      "墙模": {
        "slug": "wall-formwork",
        "products": [
          ["product-slug", "产品名称", "产品描述", "图片URL"]
        ]
      }
    }
  }
}
```

### 修改步骤
1. 编辑 `products_v2.json`
2. 运行 `python3 rebuild_site_v2.py`
3. 运行 `bash deploy.sh` 部署

## 🎨 样式特点

- **PERI 品牌色**：红色 (#e3000f) 和黄色 (#f5a800)
- **响应式设计**：支持桌面和移动设备
- **多语言切换**：页面内置语言切换功能
- **搜索功能**：支持产品名称和描述搜索
- **YouTube 集成**：部分产品页面包含视频演示

## 🛠️ 技术栈

- **纯静态 HTML/CSS/JavaScript** - 无需服务器
- **Python 3** - 用于生成网站
- **GitHub Pages** - 免费托管
- **Git** - 版本控制

## 📋 文件说明

| 文件 | 说明 |
|------|------|
| `index.html` | 网站首页，展示所有产品分类 |
| `search.html` | 搜索页面，支持全站产品搜索 |
| `products_v2.json` | 产品数据源（JSON 格式） |
| `rebuild_site_v2.py` | 网站生成脚本（Python 3） |
| `deploy.sh` | Mac/Linux 部署脚本 |
| `deploy.ps1` | Windows 部署脚本 |
| `DEPLOY_GUIDE.md` | 详细的部署指南 |

## ⚠️ 注意事项

1. **不要手动编辑 HTML 文件** - 所有修改应该在 `products_v2.json` 中进行，然后重新生成
2. **Git 凭证** - 部署时可能需要 GitHub Personal Access Token
3. **Python 版本** - 需要 Python 3.6 或更高版本

## 🔄 版本历史

- **2026-04-05** - 完全重新生成，清理旧文件，优化项目结构
- **2026-04-04** - 初始版本，包含 165 个产品页面

## 📞 支持

如有问题，请参考：
- [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) - 详细部署指南
- [PERI 中国官网](https://cn.peri.com) - 产品详细信息

---

**由 Claude Code 自动生成和维护** 🤖
