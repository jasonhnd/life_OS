# `themes/` 不该加什么

> **故意保持近空原则**：本目录只放**显示层呈现**。每个 theme 定义 9 个主题（3 语言 × 3 文化设定）的 display 名、emoji 和语气。加新 theme 是 lifeos 最贵的操作之一 —— 之后每个新 agent / spec / 命令都要付这个角色名的成本。

## 什么 **不** 属于这里

1. **引擎逻辑** —— 如"archiver phase 2 做什么"。→ 去：`agents/archiver.md`。
2. **Spec 内容** —— 如"session frontmatter 定义"。→ 去：`references/session-index-spec.md`。
3. **Agent 行为的翻译** —— theme 只翻**显示名**，**不翻**行为。行为跨 theme 完全一致。
4. **"反正闲着没事就加"的新文化设定** —— 见下方"加新 theme 前"。
5. **子领域的 theme 变体** —— 如"zh-classical-finance"用金钱聚焦显示名。Theme 是 session 级，不是 domain 级。
6. **每用户定制** —— 用户改 `meta/config.md` 切换 theme，不是自己加新 theme。

## 什么 **属于** 这里

完整 theme 文件含全部：
- `Role Mapping` 表 —— SKILL.md 每个引擎角色映射到 display 名 + emoji + 报告标签
- `Domain Mapping` 表 —— 6 个 domain 映射到 theme 等价物
- `Trigger Words` —— theme 特定触发词（如 zh-classical 的"上朝"）
- `Tone` —— theme 使用的叙述声音

任何一项缺失，theme 不完整，会 fallback 到引擎 ID（丑）。

## 加新 theme 前 — 门槛高

新 theme 意味着：
- 每个既有 agent 的显示名都要翻译
- 每个未来 agent（如 v1.8.7 的 memory-keeper）必须在本 theme 加一行
- Trigger words 仔细选（不能跟既有 theme 撞）
- Tone / 文化框架在 22+ 个 agent 间内部一致
- 三语对齐（如果是某既有 theme 的翻译）

**加之前真正要问的**：有没有用户（或社区）实际要这个 theme，还是为了工程而工程？后者别加。

## 当前发布的 theme（9 个）

| 语言 | Themes |
|------|--------|
| 英文 | `en-roman.md`（罗马共和国）/ `en-usgov.md`（美国政府）/ `en-csuite.md`（公司 C-Suite） |
| 中文 | `zh-classical.md`（三省六部）/ `zh-gov.md`（中国政府）/ `zh-corp.md`（公司部门） |
| 日文 | `ja-meiji.md`（明治政府）/ `ja-kasumigaseki.md`（霞が関）/ `ja-corp.md`（企業） |

加第 10 个 theme 需要面向用户的理由 + RFC 条目 + 维护承诺。

## 引用

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12 + §9 Q3（memory-keeper 同时加到全部 9 个 theme —— 体现成本）
- 模式来源：`tinyhumansai/openhuman` `.claude/rules/README.md`
- 配套：SKILL.md `## Theme System`
