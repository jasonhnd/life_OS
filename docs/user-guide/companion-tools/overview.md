# Companion Tools 总览 · Skill Observability
> 面包屑:[← 产品入口:用户指南首页](../index.md)

> v1.7.1 先交付 **Skill Observability / Skill 观测**：让用户看见本机有哪些 skill、它们来自哪里、是否有上游更新、是否已经太久没有复核。本页聚焦 skill 库存与健康快照，三省六部制 workflow 保持原有职责。

## 本页是什么

Skill Observability / Skill 观测是 Life OS 主流程旁边的 skill 可观察性层。
它服务用户理解本机 skill 环境，为用户提供库存与健康状态。

v1.7.1 本页只描述这个 skill 观测面板。

它回答的是：

- 我现在装了哪些 skill？
- 它们是本地的、内置的，还是来自上游？
- 哪些 skill 有更新？
- 哪些 skill 已经太久没有复核？
- 我能否离线查看本地状态？

它的边界是：

- skill 库存与来源
- skill 更新与新鲜度
- 本地状态是否可离线查看
- 用户可读的触发提示

---

## Skill Observability 解决什么问题

Life OS 会逐步拥有更多 skill、skill 包和本地模板。
如果没有可观察性，用户很难判断当前环境是否可信。

Skill Observability / Skill 观测提供一个轻量状态面板。
它负责观察 skill 库存、报告健康状态、展示用户可读触发提示。
状态面板的输出帮助用户判断环境是否可靠。

这让用户在 Start Session、升级、排查或迁移机器前，可以先获得稳定的环境快照。

---

## 我该不该装

可以按下面 4 个问题顺序判断：

1. 你现在是否管理多个 skill？如果不是，可以先不装。
2. 你是否经常需要查看“本机到底有哪些 skill”？如果是，继续看下一问。
3. 你是否会在升级、迁移机器或排查环境前做状态核对？如果是，建议安装 Skill 观测。
4. 你是否需要知道某个 skill 是本地、内置，还是来自上游？如果是，建议安装 Skill 观测。

如果只有第 1 个问题为“是”，但后续问题都为“否”，可以等到 skill 数量变多后再装。

---

## 当前 CLI

v1.7.1 当前提供 4 个命令。

```bash
life-os-tool skills list
```

列出当前可见的 skills。

```bash
life-os-tool skills check
```

检查本机 skills 与上游信息。

```bash
life-os-tool skills info <name>
```

查看某个 skill 的详细信息。
`<name>` 是用户可见名称，例如 `imagegen`、`openai-docs`、`github:yeet`。

```bash
life-os-tool skills stale
```

列出超过新鲜度窗口的 skills。
v1.7.1 的 stale 口径是：超过 90 天没有更新、确认或刷新。

---

## 验证安装

安装后先运行：

```bash
life-os-tool skills list
```

确认输出里能看到预期的 skill 名称。
如果某个 skill 显示为：

```text
🟢 current / local
```

表示本地记录可读，且当前没有发现需要立即处理的上游差异。

如果列表为空，先确认当前环境确实安装了 skill。
如果出现 `❓ check failed`，优先用离线方式确认本地记录：

```bash
life-os-tool skills list --offline
```

---

## 怎么触发 / 调用

Skill 观测优先作为独立命令使用。

常用调用方式是：

```bash
life-os-tool skills list
life-os-tool skills check
life-os-tool skills info <name>
life-os-tool skills stale
```

这些命令不会自动安装、更新或启用 skill。
它们只展示当前环境状态，方便用户自己决定下一步。

在需要放进 Start Session 前置简报时，可以只集成一行 Retrospective 摘要：

```text
🧰 Skills: N active · M update · K stale
```

这行摘要适合提醒用户当前 skill 环境是否需要复核。
它不是任务分派规则，也不会改变 ROUTER、Cortex 或三省六部制流程。

---

## 通用参数

所有 skills 子命令支持：

```bash
--format {markdown,json}
```

`markdown` 适合人阅读。
`json` 适合脚本、自动化、诊断报告或未来 UI 面板读取。

需要上游检查的命令支持：

```bash
--offline
```

`--offline` 表示只读取本地缓存、本地 manifest 和本地安装记录。
它不会访问 GitHub、skill 索引或远程端点。
弱网、离线、或不希望产生网络请求时，可以使用这个参数。

---

## 输出列

默认 markdown 输出使用固定列：

```text
name | version | installed-at | source | upstream-latest | status | triggers-hint
```

| 列 | 含义 |
|---|---|
| `name` | skill 的用户可见名称 |
| `version` | 本地安装版本或本地声明版本 |
| `installed-at` | 本地安装或首次记录时间 |
| `source` | skill 来源，例如本地目录、内置包、GitHub 仓库或 skill 包 |
| `upstream-latest` | 上游可见的最新版本；离线时可能为空或显示缓存值 |
| `status` | 当前状态，用统一 emoji 表示 |
| `triggers-hint` | 什么时候这个 skill 可能会被使用的简短提示 |

`triggers-hint` 不是调度规则。
它只是帮助用户理解“这个 skill 通常服务什么场景”。

---

## 状态含义

Skill Observability 使用 4 种状态。

| status | 含义 |
|---|---|
| 🟢 current / local | 本地是当前版本，或这是没有上游版本概念的本地 skill |
| 🟡 update available | 上游存在更新，本地还没有安装 |
| 🔴 stale (>90 days) | 超过 90 天没有更新、确认或刷新，建议复核 |
| ❓ check failed | 检查失败，通常是网络、权限、上游不可达或元数据不完整 |

一个 skill stale 不代表它坏了。
一个 check failed 也不代表它不可用。
它只表示观察层没有拿到足够新鲜或可靠的信息。

---

## 示例：列出 skills

```bash
life-os-tool skills list
```

可能输出：

```markdown
| name | version | installed-at | source | upstream-latest | status | triggers-hint |
|---|---:|---|---|---:|---|---|
| imagegen | 1.0.0 | 2026-04-01 | bundled skill | 1.0.0 | 🟢 current / local | 生成或编辑位图视觉资产 |
| openai-docs | 1.2.0 | 2026-03-18 | bundled skill | 1.3.0 | 🟡 update available | 查询 OpenAI 官方文档 |
| local-writing | local | 2025-12-12 | local directory |  | 🔴 stale (>90 days) | 本地写作模板 |
```

这份表是 skill 环境快照，用来帮助用户判断当前库存与健康状态。

---

## 示例：检查上游

```bash
life-os-tool skills check
```

`check` 会尽量刷新上游信息，并比较本地记录与上游可见版本。
如果上游不可达，对应行会显示：

```text
❓ check failed
```

这时可以稍后重试，或使用离线模式查看本地缓存。

```bash
life-os-tool skills check --offline
```

离线检查不能证明上游没有更新；它只能说明本地记录目前是什么。

---

## 示例：查看单个 skill

```bash
life-os-tool skills info <name>
```

`info` 适合理解某个 skill 的来源与状态。
它应该回答：

- 这个 skill 的名称和版本是什么？
- 它安装在哪里？
- 它来自哪里？
- 它上次检查是什么时候？
- 它可能由什么用户意图触发？
- 它有没有上游版本可比对？

JSON 输出适合脚本读取：

```bash
life-os-tool skills info <name> --format json
```

---

## 示例：只看 stale

```bash
life-os-tool skills stale
```

这个命令只显示建议复核的 skills。
它适合月度维护、升级前检查、或迁移到新机器后的核对。

stale 是提醒，不是报警。
稳定的本地 skill 可以长期是 🟢 current / local。
有上游但长期未检查的 skill 可能是 🔴 stale (>90 days)。

---

## 数据来源

Skill Observability 读取两类信息。

本地信息包括：

- 本机 skill 目录
- skill 的 `SKILL.md`
- skill 附带的 manifest
- 本地安装记录
- 本地缓存的上次检查结果

上游信息包括：

- `GET https://api.github.com/repos/<owner>/<repo>/releases/latest`
- `GET https://registry.npmjs.org/<pkg>/latest`
- `GET https://pypi.org/pypi/<pkg>/json`

用户不需要记住底层文件名。
本地信息告诉你“我现在有什么”。
上游信息告诉你“外面是否有更新”。

---

## 上游端点

“上游端点”就是 skill 的来源地址。
常见来源包括：

- `GET https://api.github.com/repos/<owner>/<repo>/releases/latest`
- `GET https://registry.npmjs.org/<pkg>/latest`
- `GET https://pypi.org/pypi/<pkg>/json`

运行 `life-os-tool skills check` 时，命令会尝试访问这些来源。
运行带 `--offline` 的命令时，命令只使用本地已保存的信息。

如果上游需要权限，而当前环境没有权限，状态会是：

```text
❓ check failed
```

这通常表示“无法确认”，不是“这个 skill 不能用”。

---

## 与 Retrospective 的关系

Skill Observability 可以为 Start Session 前的环境简报提供一行摘要。
Retrospective briefing line 必须使用这一句格式：

```text
🧰 Skills: N active · M update · K stale
```

含义是：

- `N active`：当前可见且可用的 skills 数量
- `M update`：发现上游更新的 skills 数量
- `K stale`：超过新鲜度窗口、建议复核的 skills 数量

这行摘要只是环境信息。
它不会让 RETROSPECTIVE 自动启用、禁用或升级 skill。

---

## 与 ROUTER 的关系

ROUTER 和 Skill Observability / Skill 观测在 v1.7.1 没有集成。

Skill Observability 面向用户展示：

- 哪些 skill 存在
- 哪些 skill 有更新
- 哪些 skill 太久没检查
- 某个 skill 的触发提示是什么

ROUTER 仍按既有语义合同处理用户消息。
`triggers-hint` 只是给人看的提示，不是 ROUTER 的 routing table。

---

## 与 Cortex 的关系

Cortex 和 Skill Observability / Skill 观测在 v1.7.1 没有集成。
Cortex 负责认知前置、跨会话记忆、概念检索、GWT 仲裁与 narrator grounding。
Skill Observability 负责技能环境体检。

它不会写入 `[COGNITIVE CONTEXT]`。
它不会生成 `signal_id`。
它不会参与 hippocampus、concept-lookup、soul-check 或 gwt-arbitrator。
它也不会影响 Narrator + Validator 的引用校验。

当前结论是：

**ROUTER and Cortex are not integrated.**

---

## 观测边界

本页只定义 Skill Observability / Skill 观测的库存与健康视图。

它关注：

- skill 是否存在
- skill 来自哪里
- skill 是否有上游更新
- skill 是否太久没检查
- skill 的用户可读触发提示是什么

这些信息帮助用户理解环境状态。
后续自动选择、执行路径和回退策略不属于 v1.7.1 范围。

---

## 推荐使用节奏

日常查看：

```bash
life-os-tool skills list
```

升级或排查前：

```bash
life-os-tool skills check
```

离线或弱网环境：

```bash
life-os-tool skills list --offline
```

只处理过期项：

```bash
life-os-tool skills stale
```

查看单项详情：

```bash
life-os-tool skills info <name>
```

---

## 常见问题

### 看到 🟡 update available 是否必须马上更新？

不一定。它只说明上游有新版本。
是否更新取决于你当前是否需要新功能、是否能接受兼容性变化，以及是否有时间验证。

### 看到 🔴 stale (>90 days) 是否表示 skill 失效？

不是。它表示超过 90 天没有刷新或确认。
如果这个 skill 仍然能稳定完成你的任务，可以先记录并择机复核。

### 看到 ❓ check failed 是否表示网络坏了？

不一定。可能是网络、权限、上游地址变更、远程仓库不可见、或 manifest 不完整。

### `triggers-hint` 会影响 ROUTER 吗？

不会。v1.7.1 中 ROUTER 和 Cortex 都不会消费这列。

### `life-os-tool skills list` 会安装 skill 吗？

不会。它只读取当前可见的本地记录和缓存信息。

### `life-os-tool skills check` 会自动更新 skill 吗？

不会。它只检查本地记录和上游信息的差异。

### 离线模式能证明没有新版本吗？

不能。`--offline` 只说明本地缓存里记录了什么，不能代表上游当前状态。

### 我应该每天运行 Skill 观测吗？

通常不需要。日常可以用 `list` 快速查看；升级、迁移机器或排查环境前再运行 `check`。

### Skill 观测会读取我的历史会话内容吗？

不会。本页定义的是 skill 库存与健康视图，不读取历史会话正文，也不进入 Cortex 认知上下文。

---

## 设计边界

Skill Observability / Skill 观测刻意保持克制。
它的职责是提供可靠、可读、可脚本化的状态面板；修复、升级、改写 skill、下一步意图推断和三省六部制审议仍由既有流程处理。

它只是提供一个可靠、可读、可脚本化的状态面板。
Markdown 服务用户。
JSON 服务自动化。

---

## 深入阅读

用户指南：

- [Cortex 总览](../cortex/overview.md) - 理解 v1.7 的认知前置层，以及为什么本页不把 Skill Observability 接入 Cortex
- [Session Lifecycle](../session-lifecycle/overview.md) - 理解 Start Session / Adjourn 的用户流程
- [Second Brain](../second-brain/overview.md) - 理解 Life OS 的本地知识与记忆承载方式
- [Storage and Sync](../storage-and-sync/overview.md) - 理解本地文件、同步与可移植性

推荐搭配:

- [Life OS 社区推荐的 companion tools](../../companion-tools.md) - 具体推荐的 skill 与工具清单(huashu-design / markitdown / claude-mem 等)及安装命令

规格与实现参考：

- `SKILL.md` - Life OS 根目录权威行为定义
- `pro/AGENTS.md` - Codex host 下的 orchestration 协议
- [Skill 观测权威规格](../../../references/skills-spec.md) - Skill Observability / Skill 观测的 authoritative spec
- `references/cortex-spec.md` - Cortex 语义合同
- `references/data-model.md` - Life OS 数据模型

---

**下一篇**:[companion-tools.md](../../companion-tools.md) - 具体推荐的外部 skill/tool 清单及安装命令。
