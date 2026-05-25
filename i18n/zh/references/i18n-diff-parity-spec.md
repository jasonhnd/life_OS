---
spec_id: i18n-diff-parity-spec.v1
description: 改动行三语对齐验证规范。当 `references/*.md` 在两个 tag 间（或 HEAD vs 上个 tag）变化时，对应的 `i18n/zh/references/<同名>.md` 和 `i18n/ja/references/<同名>.md` 必须同范围变化。作为 verify-release check #9 强制（v1.8.7 WARN 级，v1.8.8 目标 BLOCK）。消除 `pro/compliance/violations.md` 反复出现的"EN spec 更新但 zh/ja 漂移"违规。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman AGENTS.md:118-120 (改动行覆盖率 gate 通过 diff-cover)，模式从 "改动覆盖率" 适配到 "改动 i18n 镜像"
introduced_in: v1.8.7
referenced_by:
  - .claude/commands/verify-release.md (check 9)
  - pro/agents/auditor.md (Mode 7 M7-5)
---

# i18n 改动对齐规范 v1

EN spec 文件在 `references/*.md` 在两个 tag 间变化时，对应的 ZH/JA 镜像文件必须同范围变化。本 spec 定义：

1. 如何识别"改动范围"
2. 如何验证 EN ↔ zh / EN ↔ ja 对应关系
3. 什么算对齐（足够）vs 漂移（失败）
4. WARN vs BLOCK 升级时间线

## 适用文件

所有三语镜像文档：

- `references/*.md` ↔ `i18n/zh/references/*.md` ↔ `i18n/ja/references/*.md`
- `CHANGELOG.md` ↔ `i18n/zh/CHANGELOG.md` ↔ `i18n/ja/CHANGELOG.md`
- `README.md` ↔ `i18n/zh/README.md` ↔ `i18n/ja/README.md`
- `MIGRATION.md` ↔ `i18n/zh/MIGRATION.md` ↔ `i18n/ja/MIGRATION.md`（存在时）

**不适用**（故意排除）：

- `SKILL.md` —— 单文件（主题处理输出语言）
- `references/hard-rules-index.md` —— 单文件（dev 内部索引）
- `pro/gotchas.md` —— 单文件（dev 内部知识库）
- `pro/agents/*.md` —— 每 agent 单文件（themes/ 处理显示）
- `pro/*.md`（CLAUDE.md / GEMINI.md / AGENTS.md / GLOBAL.md）—— host 特定编排，不是用户面翻译
- `_meta/**/*` —— 运行时工件和 RFC
- `themes/*.md` —— theme 文件用原生文化语言

## 改动识别（章节级）

"章节"由 `## ` 二级标题标识。diff 对齐检查按章节级进行：

1. 用 `git diff <base>..HEAD -- references/<file>.md` 找改动行
2. 把每行映射到其所属 `## ` 章节（往前找到最近的 `## `）
3. 收集唯一改动章节集合
4. 对每个改动章节，验证 `i18n/zh/references/<file>.md` 和 `i18n/ja/references/<file>.md` 中同章节也变化

章节级粒度（非行级）是有意的：不要求逐字翻译；**实质内容对齐**才是。

## 对应规则

### 章节数对齐（硬性）

适用文件：

```
count(EN 中 ## 章节) == count(zh 中 ##) == count(ja 中 ##)
```

漂移：一种语言加/减章节而另两种没动 = 对齐失败。

### 章节标题对齐（软性）

章节标题**可以**翻成原生语言。为支持自动交叉引用，**鼓励**（v1.8.7 不强制）翻译标题中含英文锚点：

- ✅ `## 背景 (Background)` —— 标题翻译 + 英文锚点
- ✅ `## 背景` —— 标题翻译，无锚点
- ❌ 章节重排导致 "EN 第三节" ≠ "zh 第三节"

有锚点：按锚点交叉引用。
无锚点：按**章节序号位置**交叉引用（第 1、2、3 节）。

跨语言章节重排破坏序号交叉引用，会被 flag。

### 改动章节对齐（硬性）

如果 EN 文件章节 N 在某 commit 变化，zh 文件章节 N **且** ja 文件章节 N 也必须在该 commit **或前 3 个 commit** 内变化（允许翻译工作的轻微时间偏移）。

"3 commit 窗口"容差用于：EN spec 先 commit，zh+ja 翻译跟在下 1-2 commit —— 都属于同一 PR / release 的逻辑组。

## 验证实现（verify-release check 9）

在 `.claude/commands/verify-release.md`（LLM 驱动，因为 lifeos md-only —— 没真 shell 脚本），check 9 LLM 程序：

1. 确定 base tag（上次 release tag）和 HEAD
2. 列适用范围内所有改动文件：`git diff --name-only <base>..HEAD -- references/ i18n/zh/references/ i18n/ja/references/ CHANGELOG.md i18n/zh/CHANGELOG.md i18n/ja/CHANGELOG.md README.md i18n/zh/README.md i18n/ja/README.md MIGRATION.md i18n/zh/MIGRATION.md i18n/ja/MIGRATION.md`
3. 对每个改动的 EN 文件：
   a. 识别改动章节（解析 diff 行范围，往前找最近 `## `）
   b. 验证每个改动章节在 zh 和 ja 镜像也有 diff
   c. 验证章节数对齐（EN 章节数 == zh 数 == ja 数）
4. 聚合发现：
   - **PASS**：每个改动 EN 章节有对应 zh+ja 章节 diff，数量对齐
   - **WARN**（v1.8.7 默认）：某些章节漂移但 EN 文件的 `referenced_by:` 小 / 修复可等
   - **FAIL**：章节漂移，特别是带 HARD RULE 的 spec

v1.8.7 输出无论严重程度都是 WARN 级。v1.8.8 目标把主要漂移升 BLOCK。

## WARN vs BLOCK 升级时间线

**v1.8.7 ship**（当前）：check 9 是 WARN。首次跑可能噪音多（历史漂移）；目标是暴露而非阻塞。

**v1.8.8 目标**（v1.8.7 ship 后 4 周）：如 v1.8.7 WARN 输出稳定（漂移类型可枚举、误报率 <20%），把 check 9 升级到 BLOCK 级以下类别：

- 带 `authoritative: true` frontmatter 的 spec（真相源 spec）
- README + CHANGELOG（用户面文档）
- MIGRATION（用户升级关键）

其他低重要性漂移留在 WARN。

**永久 WARN**：章节排序问题 + 不影响实质内容的小措辞改动。

## 常见漂移模式与补救

### 模式 1：「下个 PR 翻 zh+ja」

EN spec 落地；zh+ja 漂移留待。**补救**：PR 模板要求三语全有或显式 "deferred-to: <PR/issue>" 含截止。按 `references/agent-spec.md` v2，spec 合入前需三语对齐。

### 模式 2：「EN 加了一节，忘了 zh+ja」

章节数发散。**补救**：合入前 AUDITOR Mode 7 M7-5 抓。PR 不能落地直到对齐恢复或显式 `i18n-drift-allowed: <reason>` frontmatter 例外。

### 模式 3：「EN 改了章节名，镜像没改」

章节序号对齐失败。**补救**：鼓励英文锚点 `## 背景 (Background)`，重命名通过锚点匹配检测。

### 模式 4：「EN 实质内容重写，镜像只修了 typo」

镜像 diff 存在但浅。**补救**：check 9 不自动抓这种深度差异 —— 在 PR review 中手动 flag 直到 v1.8.8 引入行数比启发式。

## 例外

三个合法不要求对齐的场景：

1. **仅英文锚点调整** 翻译标题 —— 不是实质改动，镜像 diff 不要求
2. **仅翻译 commit** —— 修 zh/ja typo 不改 EN —— commit 本身就是对齐恢复，不算违规
3. **`status: legacy` spec** —— 标 legacy 的历史 spec 不需要持续对齐（内容冻结）

例外通过 frontmatter 记录：

```yaml
i18n_parity_exception: anchor-only|translation-only|legacy
```

AUDITOR Mode 7 M7-5 尊重这些例外。

## 引用

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.3 F11
- 模式来源：`tinyhumansai/openhuman` AGENTS.md:118-120（改动行覆盖率通过 diff-cover）—— 适配 i18n 镜像
- `pro/compliance/violations.md` —— 本 spec 旨在防止的历史漂移事件
