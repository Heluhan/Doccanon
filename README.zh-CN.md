[English](README.md) | [简体中文](README.zh-CN.md)

# DocCanon

### 别再让每个 Coding Agent 从头理解你的代码库。

**DocCanon 是为 Coding Agent 提供的可验证上下文层。**

它把项目中稳定、重要的知识沉淀在代码库里，让不同 Coding Agent 可以复用同一份项目上下文，而不是每次接到新任务，都重新扫描仓库、重新理解架构、重新建立项目认知。

**复用上下文。保持最新。自由切换 Agent。**

---

## 快速开始

在当前项目中安装 DocCanon：

```bash
gh skill install Heluhan/Doccanon doccanon --agent universal
```

然后告诉你的 Coding Agent：

> **Set up DocCanon for this project.**

就这么简单。

完成初始化后，正常使用你的 Coding Agent 即可。DocCanon 会在工作流中负责上下文路由、状态验证和文档同步。

> `gh skill` 目前仍属于 GitHub CLI 的 preview 功能。特定 Agent 或手动安装方式见 [安装](#安装)。

---

## 为什么需要 DocCanon？

### 1. 不要反复重新理解同一个代码库

一个新的 Coding Agent 任务，经常从同一套流程开始：

```text
任务
 ↓
搜索代码库
 ↓
阅读入口文件
 ↓
追踪依赖
 ↓
重新理解架构
 ↓
找到相关代码
 ↓
开始真正工作
```

但其中很多理解其实是稳定的。

它们没有必要在每个新任务、每个新 session、每个新 Agent 中重新建立一遍。

DocCanon 会先给 Agent 一份精简的项目地图：

```text
任务
 ↓
加载相关项目上下文
 ↓
检查相关代码
 ↓
开始工作
```

Agent 在需要时依然会检查真实代码。

区别只是，它不再需要每次都把整个代码库当成一片完全陌生的区域重新探索。

DocCanon 的目标，就是减少重复的代码库探索，从而降低 Agent 在理解项目阶段消耗的 context、工具调用和时间。

实际能节省多少 token，会受到项目规模、任务类型、模型和 Agent 实现方式影响，因此 DocCanon 不承诺一个统一的百分比。

---

### 2. 换 Agent，不要丢上下文

项目知识应该属于**项目本身**，而不是某一个模型、IDE 或 session。

DocCanon 将 canonical knowledge 以普通 Markdown 的形式保存在仓库中：

```text
CONTEXT.md
docs/
```

不同 Coding Agent 可以基于同一套项目认知工作：

```text
Codex ──────────┐
Claude Code ────┤
Cursor ─────────┼──→ 项目上下文 ──→ Codebase
OpenCode ───────┤
Copilot ────────┤
Gemini CLI ─────┘
```

今天用 Codex，明天换 Claude Code，后天再换 OpenCode，不需要每次重新从零建立项目 mental model。

**换 Agent，不换上下文。**

---

### 3. 不要让共享上下文悄悄过期

一旦项目知识被长期保存，就会产生一个新的问题：

**如果代码变了，但文档没变怎么办？**

一份过期的项目地图，有时比没有地图更危险。

DocCanon 把 freshness 当成系统的一部分。

它会检查 canonical project knowledge 是否仍然适用于当前 branch，并跟踪实现变化影响了哪些 current-state knowledge。

如果代码已经发生变化，但相关项目知识还没有被更新，DocCanon 不会把当前项目状态视为已经同步。

```text
代码发生变化
     ↓
是否影响项目知识？
     ↓
    是
     ↓
更新 + 验证
     ↓
完成同步
```

所以 DocCanon 不只是“把上下文保存下来”。

它保存的是一份**受治理、可验证的项目上下文**。

---

## 工作原理

对于已经由 DocCanon 管理的项目，基本流程是：

1. **检查可信状态** — 确认当前 branch 上的 canonical context 可以使用。
2. **路由上下文** — 只加载当前任务真正相关的项目知识。
3. **检查代码** — 根据需要查看源码、测试、配置或运行时证据。
4. **完成实现** — 修改真正的代码。
5. **保持同步** — 更新受到影响的 current-state knowledge，并验证最终结果。

用户不需要手动执行这整套流程。

这些事情由 skill 自己负责。

```text
新任务
 ↓
可信项目上下文
 ↓
相关代码
 ↓
实现
 ↓
更新项目知识
 ↓
验证
```

---

## 为什么不用 `AGENTS.md`、`CLAUDE.md` 或普通文档？

这些文件本身都很有价值。

DocCanon 解决的是另一个问题。

普通项目文档可以保存知识，但也可能在代码变化之后悄悄过期。

某个 Agent 专属的 memory 或 rules 文件可以帮助一个 Agent，但这些知识未必能自然迁移到另一个 Agent。

而让每个 Agent 都直接从源码重新理解项目当然也可以，只是会不断重复同样的探索过程。

DocCanon 在这些基础上补上了三件事：

* **可迁移上下文** — 项目知识跟着代码库，而不是绑定某个 Agent。
* **按任务加载** — Agent 先读取最相关的一小部分上下文，再去检查源码。
* **可验证性** — 项目知识不会被默认永久可信，而是需要和真实实现保持一致。

DocCanon **不会取代源码检查**。

它改变的是 Agent 开始工作的起点。

> **先看地图，再核对真实地形。**

### Agent 入口文件是生成物，不是手写笔记

Codex、Cursor、GitHub Copilot、OpenCode 会在 session 启动时读取 `AGENTS.md`；Claude Code 会直接读取它，或通过一个薄 `CLAUDE.md` import 读取。它是每个 Agent 最先看到的内容，所以入口文件里一段过期或已退役的文字，会污染每个 session。

DocCanon 把入口文件当作**生成投影**：

* `AGENTS.md` 只从已验证的 current-state owner 渲染；退役、历史、draft、未分类的内容在构造上不会进入。
* 渲染是幂等的：canonical 内容没变就不写盘、不产生 diff、不制造噪音。
* `check` / `preflight` 是只读的，投影缺失或过期会直接失败；`sync complete` 会在 canonical 更新后自动刷新。
* 文件末尾的用户自定义区原样保留，项目或工具特定笔记不会在重新生成时丢失。

**入口文件是视图，不是第二个真实信息源。**

### 退役内容离开可检索区

退役是一步操作：DocCanon 把文档移入归档根目录，盖上 `historical` 或 `superseded` 标记并写明归属或原因，同时把归档路径写进 `.ignore`，让日常文本搜索默认跳过。需要考古时，按路径或带 ignore/hidden 参数依然能找到。`migrate scan` 会跳过归档区，退役内容不会再作为迁移候选冒出来。

### 未来工作有自己的受治理位置

路线图、上线条件和已知缺口放在 `docs/plans/`，用 `doccanon_authority: plan` 标记。计划在任务相关时会被路由给 Agent，但永远不会冒充已实现的行为；如果某个计划仍指向本次版本且未就绪（`active` 或 `abandoned`），发布就无法完成。目标上线后，结果进入发布历史，计划本身退役。

---

## 试试看它如何发现过期上下文

想先看看 DocCanon 的 trust boundary 是怎么工作的，可以直接运行：

```bash
git clone https://github.com/Heluhan/Doccanon.git
cd Doccanon
python3 scripts/demo.py
```

这个 Demo 会创建一个临时 Git 项目，建立已经治理好的 baseline，然后修改受管理的代码、但故意不更新对应的 canonical owner。

DocCanon 会识别出项目知识已经过期，并拒绝把当前状态视为 synchronized。

---

## 安装

### GitHub CLI

对于使用共享项目 skill 目录的 Agent：

```bash
gh skill install Heluhan/Doccanon doccanon --agent universal
```

也可以针对特定 Agent 安装：

```bash
# Codex
gh skill install Heluhan/Doccanon doccanon --agent codex

# Claude Code
gh skill install Heluhan/Doccanon doccanon --agent claude-code

# Cursor
gh skill install Heluhan/Doccanon doccanon --agent cursor

# OpenCode
gh skill install Heluhan/Doccanon doccanon --agent opencode
```

安装之前也可以先查看 skill 内容：

```bash
gh skill preview Heluhan/Doccanon doccanon
```

### 手动安装

DocCanon 也自带安装器：

```bash
git clone https://github.com/Heluhan/Doccanon.git
cd Doccanon

python3 install.py \
  --agent universal \
  --scope project \
  --project /path/to/project
```

DocCanon 不依赖运行时服务、API Key、向量数据库或特定模型。

辅助脚本需要：

* Git
* Python 3.10+

不同 Agent 的目录位置和发现机制，见 [Agent 兼容性说明](docs/agent-compatibility.md)。

---

## 支持的 Agent

DocCanon 当前提供以下安装目标：

* Codex
* Claude Code
* Cursor
* GitHub Copilot
* Gemini CLI
* OpenCode
* Cline

不同 Agent 对 skill 的发现和激活机制可能不同，但 canonical project knowledge 本身保存在项目仓库里，因此可以在支持的 Agent 之间复用。

---

## Token 效率

DocCanon 背后的思路很简单：

> **不要反复花 context 去重新发现项目已经知道的东西。**

传统方式下，Agent 在每个任务开始前，可能需要大范围搜索代码库。

DocCanon 会先把 Agent 路由到一份小而新的 canonical context，然后再针对当前任务检查必要的源码。

你可以在本地测量 context volume：

```bash
python3 /path/to/doccanon/skills/doccanon/scripts/measure_context.py \
  --project . \
  --intent "change session recovery" \
  --baseline tracked-code \
  --json
```

这个结果只是 **context reduction proxy**，不等同于模型真实 token 用量或费用。

如果需要做受控实验，可以参考 [Token Benchmark Protocol](skills/doccanon/references/token-benchmark.md)。

---

## DocCanon 不是什么

DocCanon 不是源码的替代品，也不是向量数据库或 codebase RAG 服务。

源码、测试、schema、配置和直接运行时证据，依然是实现行为的最终依据。

DocCanon 做的是：

**让 Agent 从更好的项目上下文开始工作，并确保这份上下文持续对真实代码负责。**

---

## 更多文档

* [English README](README.md)
* [Agent 兼容性](docs/agent-compatibility.md)
* [DocCanon Skill Specification](skills/doccanon/SKILL.md)
* [Token Benchmark Protocol](skills/doccanon/references/token-benchmark.md)
* [Contributing](CONTRIBUTING.md)
* [Security](SECURITY.md)

---

## License

MIT.

---

**DocCanon 把“每个 Agent 都要重新建立一次的代码库理解”，变成项目自己可以保存、验证并持续复用的知识。**
