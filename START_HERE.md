# 新对话快速启动指令

## 在新的Claude对话窗口中使用此项目

### 推荐方式（完整版 - 包含所有细节）

```
我需要继续处理PERI产品网站项目。

项目路径: /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站

请读取以下文件了解项目：
1. README.md - 项目概况
2. PRODUCT_STATUS.md - 产品完成状态（21个已完成，139个待处理）
3. WORKFLOW_COMPLETE.md - 完整工作流程（包含PDF提取、项目提取、YouTube提取的所有细节和实际方法）

然后告诉我当前状态和建议下一个处理的产品。
```

### 方法2: 简洁版（如果需要快速开始）

```
我需要继续处理PERI产品网站项目。

项目路径: /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站

请读取以下文件了解项目：
1. README.md - 项目概况
2. WORKFLOW_QUICK_REFERENCE.md - 快速参考

然后告诉我当前状态，我们可以继续处理下一个产品。
```

### 方法2: 简短版本

```
继续PERI产品网站项目
路径: /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站
读取: WORKFLOW_QUICK_REFERENCE.md
```

### 方法3: 直接说明

```
我要继续做PERI产品网站，路径是 /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站，
先读WORKFLOW_QUICK_REFERENCE.md了解流程，然后我们开始处理下一个产品。
```

## 重要提示

✅ **推荐使用完整版**（WORKFLOW_COMPLETE.md）:
- 包含PDF提取的详细步骤（搜索顺序、三步验证法）
- 包含项目提取的详细步骤（为什么不用WebFetch、如何验证）
- 包含YouTube提取的详细步骤（在哪搜索、筛选条件）
- 包含所有常见错误和解决方法
- 包含所有经验教训和纠错细节
- 文件大小：14.7KB，524行（仍然可以快速加载）

✅ **只读取这些文档**（避免token过多）:
- `WORKFLOW_COMPLETE.md` (14.7KB) - 完整工作流程和所有细节
- `README.md` (2.3KB) - 项目概况
- `PROJECT_RULES.md` (6.8KB) - 如需了解核心规则

❌ **不要读取**:
- `archive/` 目录中的文档（除非需要查看历史记录）
- 旧的MASTER_WORKFLOW.md等（已归档，内容已整合到WORKFLOW_COMPLETE.md）

## 典型对话开始

**你说**:
```
继续PERI产品，路径 /Users/fufu/Documents/Claude/Projects/自动化/创建产品网站
读 WORKFLOW_QUICK_REFERENCE.md
```

**Claude会**:
1. 读取WORKFLOW_QUICK_REFERENCE.md
2. 了解6步工作流程
3. 询问你要处理哪个产品
4. 按照流程开始工作

## 当前项目状态

- **已完成**: 10+ 个产品（已验证）
- **待处理**: 150 个产品
- **网站**: https://kiminanoliu-eng.github.io/peri-gcb/
- **工作流程**: 确认slug → 提取数据 → 验证 → 创建JSON → 生成 → 部署

## 如果需要详细信息

如果Claude需要查看历史错误记录或详细检查清单：
```
请查看 archive/errors/CRITICAL_ERRORS_LOG.md 了解之前的错误
```

或
```
请查看 archive/checklists/PREVENTION_CHECKLIST.md 了解详细检查清单
```

---

**提示**: 将此文件加入书签，每次新对话时快速参考！
