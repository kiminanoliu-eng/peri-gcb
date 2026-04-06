# PERI GCB 产品网站

自动生成的 PERI 产品展示网站，包含 160+ 产品页面和完整的分类导航系统。

## 当前状态

- **已完成产品**: 10+ 个（已验证）
- **待处理产品**: 150 个
- **网站地址**: https://kiminanoliu-eng.github.io/peri-gcb/

## 快速开始

### 添加新产品页面

- **快速参考**: [WORKFLOW_QUICK_REFERENCE.md](WORKFLOW_QUICK_REFERENCE.md) - 简洁版流程（2.6KB）
- **完整文档**: [WORKFLOW_COMPLETE.md](WORKFLOW_COMPLETE.md) - 详细步骤和经验教训（包含所有细节）

**简要步骤**:
1. 确认产品slug（从products_v2.json）
2. 提取数据（curl + grep）
3. 验证数据（PDF内容、项目案例、视频）
4. 创建JSON（{slug}_complete.json）
5. 生成页面（python3 rebuild_site_v2.py）
6. 部署验证（bash deploy-peri-gcb.command）

### 重新生成网站

```bash
python3 rebuild_site_v2.py
```

### 部署到GitHub Pages

```bash
bash deploy-peri-gcb.command
```

等待1-2分钟后访问在线页面验证。

## 项目结构

```
创建产品网站/
├── WORKFLOW_QUICK_REFERENCE.md  # 快速参考（必读）
├── PROJECT_RULES.md             # 核心规则
├── products_v2.json             # 产品数据源
├── rebuild_site_v2.py           # 网站生成脚本
├── deploy-peri-gcb.command      # 部署脚本
├── index.html                   # 首页
├── search.html                  # 搜索页面
├── categories/                  # 分类页面（19个）
├── products/                    # 产品页面（160+个）
└── archive/                     # 历史文档（详细记录）
    ├── workflow/                # 工作流程文档
    ├── errors/                  # 错误记录
    ├── checklists/              # 检查清单
    ├── analysis/                # 问题分析
    ├── reports/                 # 状态报告
    ├── fixes/                   # 修复记录
    └── setup/                   # 配置文档
```

## 核心文档

- **WORKFLOW_QUICK_REFERENCE.md** - 产品处理流程快速参考（必读）
- **PROJECT_RULES.md** - 项目核心规则
- **archive/** - 详细的历史记录、错误分析、经验教训

## 技术栈

- 纯静态 HTML/CSS/JavaScript
- Python 3（网站生成）
- GitHub Pages（托管）

---

**由 Claude Code 自动生成和维护** 🤖
