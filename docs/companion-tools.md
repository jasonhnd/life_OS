# Companion Tools 推荐清单

> Life OS 用户社区可选搭配的 skill、CLI 与命令清单。

Breadcrumb: [Life OS docs](./) > Companion Tools 推荐清单

本页是社区搭配清单，Life OS 规范以根目录 `SKILL.md` 为准。

插件执行设计由对应规格处理。

它只是给用户和维护者一个轻量清单：

哪些 skill、CLI 或命令值得关注；

它们大致解决什么问题；

如何安装；

以及和 Life OS 的边界在哪里。

如果你只想理解 Life OS 自己的 skill 模型，请优先读根目录 `SKILL.md`。

如果你想看用户向导版本，请参考：

[docs/user-guide/companion-tools/overview.md](./user-guide/companion-tools/overview.md)

后续该用户向导页可以反向链接到本页，形成双向引用。

## 推荐搭配

| 名字 | 类型 | 安装 | 用途 | 上游 |
|------|------|------|------|------|
| huashu-design | Claude Code skill | `npx skills add alchaincyf/huashu-design` | 设计(HTML 原型 / PPT / 动画) | github.com/alchaincyf/huashu-design |
| markitdown | Python CLI | `pip install 'markitdown[all]'` | 文件转 md(PDF/PPT/OCR) | github.com/microsoft/markitdown |
| claude-mem | Claude Code plugin | `/plugin install thedotmack/claude-mem` | 跨 session 记忆(注:vector DB,和 Life OS Cortex 哲学冲突,仅作为候选) | github.com/thedotmack/claude-mem |

## Life OS 和这些候选项的关系

Life OS 仍然以 Claude Code 原生路由为主。

这些 skill 与 CLI 是用户环境里的辅助项。

Life OS 的调度控制面仍由既有流程负责。

`life-os-tool skills list` 聚焦 Skill 观测：

它帮助你看见当前环境里有哪些 skill、来源是什么、是否值得检查。

安装、更新和任务归属仍由用户或既有流程处理。

中文功能名建议统一写作 **Skill 观测**。

## 使用场景

这些候选项适合在 Life OS 之外补足具体任务场景。

例如：

你要把一个想法快速做成可看的 HTML 原型；

你要把 PDF、PPT 或图片材料转成 Markdown；

你想实验另一套跨 session 记忆机制；

你想确认当前 Claude Code 环境里装过哪些 skill。

这些都可以作为 Life OS 工作流的输入或旁路辅助。

Life OS 的三省六部制流程，以及 ROUTER、PLANNER、REVIEWER、DISPATCHER 的职责边界保持不变。

## huashu-design

`huashu-design` 是偏创作和表达的 Claude Code skill。

它适合把模糊想法变成更有视觉结构的产物。

典型用途包括：

HTML 原型；

PPT 叙事；

动画表达；

视觉化方案草稿。

在 Life OS 里，它适合配合“输出物打磨”类任务。

例如用户已经有战略、会议纪要、项目构想或产品说明。

Life OS 可以先帮助梳理内容结构。

随后用户再用该 skill 做呈现层探索。

推荐把它看成设计协作者，而不是决策者。

## markitdown

`markitdown` 是 Microsoft 维护的 Python CLI。

它的价值在于把多格式文件转成 Markdown。

典型用途包括：

PDF 转 md；

PPT 转 md；

图片 OCR；

Office 文档内容抽取；

把外部材料整理成 Life OS 更容易阅读的文本。

在 Life OS 里，它适合放在资料摄入前。

例如你有一份报告、课件、合同草案或截图。

先把文件转成 Markdown；

再交给 Life OS 做总结、归档、规划或审阅。

这样可以减少模型直接读二进制文件时的不确定性。

## claude-mem

`claude-mem` 是 Claude Code plugin。

它提供跨 session 记忆功能。

但它通常依赖 vector DB 这类向量检索机制。

这一点和 Life OS Cortex 的哲学并不完全一致。

Life OS Cortex 更强调：

显式 session 索引；

概念图；

受控的认知前置层；

以及可审计的上下文合成。

所以 `claude-mem` 在这里仅列为候选。

如果你要实验它，建议先在个人环境中试用。

不要默认把它等同于 Life OS 的正式记忆层。

也不要把它写进 Life OS 的核心路由假设。

## Skill 观测的边界

Skill 观测只回答“我现在有什么”。

它可以展示：

skill 名称；

安装位置；

来源；

上游地址；

可能用途；

本地可见状态；

以及人工可读的备注。

隐藏推理、内部路由规则、自动执行承诺，或把第三方候选项包装成 Life OS 子代理，都属于 Life OS 既有边界之外。

这可以避免把推荐清单误读成调度控制面。

## 选择建议

优先安装你当前真的会用到的候选项。

不要为了“完整”而安装全部候选。

如果你的工作以写作、研究、项目管理为主，`markitdown` 往往最先产生价值。

如果你的工作需要展示、路演、课程或产品原型，可以考虑 `huashu-design`。

如果你正在研究长期记忆体验，可以谨慎评估 `claude-mem`。

如果你只是维护 Life OS 文档，不需要安装任何一个。

## 维护提示

本页可以记录社区常用组合。

每一项都应尽量包含：

名字；

类型；

安装命令；

用途；

上游；

以及是否存在明显边界或风险。

新增条目时优先使用 `skill` 这个术语。

除非上游明确是 Claude Code plugin，否则不要把普通 skill 写成 plugin。

本页新增内容应保持推荐清单与 Skill 观测用途，不扩展到插件执行设计。

也不要把 `life-os-tool skills list` 描述成安装器。

## 风险说明

这些候选项由第三方维护。

它们的安装方式、功能、依赖、许可证和兼容性都可能变化。

本页可能滞后于上游。

Life OS 不保证这些候选项始终可用。

Life OS 也不保证它们和当前版本完全兼容。

使用前请查看对应上游仓库，并按自己的环境做小范围验证。

另见 `docs/user-guide/companion-tools/overview.md`：面向用户的 Companion Tools 使用指南。
