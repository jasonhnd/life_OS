# Inbox 捕获 · GTD 零摩擦输入

**本地备忘。不推送 GitHub。给自己看的技术参考。**

Inbox 是 Life OS 的 GTD 收集篮。所有"将来可能要想的事"先丢进来，不分类、不判断、不决策 — **这是它能 work 的核心**。

权威源：`references/data-layer.md`（Cognitive Pipeline: Perceive → Capture → Judge）。

---

## 两个位置

### 1. 手机 → Notion Inbox 数据库

移动端没有 second-brain 的完整结构（手机里没有 git repo）。但 Notion inbox 手机能访问。工作流：

```
你在地铁上想到点子
  ↓
打开 Claude.ai 手机端 / Notion 手机端
  ↓
说一嘴 或 打字一行
  ↓
Notion Inbox 里一条新记录
  Content: "应该调研日本的创业签证"
  Source: Mobile
  Status: Pending
  Time: 2026-04-08 14:32 JST
```

不需要选项目、不需要选领域、不需要分类。就一句话 + 自动打的时间戳。

### 2. 桌面 → `second-brain/inbox/` 目录

在桌面你可能也想快速丢东西。直接在 inbox 目录下建一个 `.md` 文件。或者跟 CC 说"丢个东西进 inbox：xxx"，它会帮你写。

Inbox 里文件没有固定结构 — 是真正的"乱堆"。

---

## 零摩擦原则

### 为什么要零摩擦

研究表明：捕获想法的摩擦力每多 1 秒，实际捕获率降 30-50%。你脑子里有个闪念 → 要打开 app → 要选分类 → 要打标签 → 烦了 → 不记了 → 想法消失。

Life OS 的 GTD 模式是：**手机上只干一件事 — 把话记下来。** 所有分类、判断、决策都留给桌面。

### 不要在手机上做什么

- 不要分类到 project / area。
- 不要写成决策纪要。
- 不要链到 wiki。
- 不要设优先级。

手机阶段只有一个目标：**别让想法丢了**。

### Inbox 示例

```
今天蛋白摄入可能不够
爸爸说他周日要来
那个 DeepL 替代品叫什么来着
XX 公司发新产品了 — 要和我们 Q2 的对比
想明年这时候开始学德语
@mark 说可以聊聊 API 设计
```

一行一条，随便写。不用完整句子。不用准确语法。

---

## 桌面拉取工作流

### 上朝自动拉

每次上朝 RETROSPECTIVE 自动：

1. 读所有 backend 里的 inbox（GitHub inbox/ + Notion Inbox）。
2. 列出所有 pending 条目。
3. 晨报里告诉你有几条待处理。

示例晨报片段：

```
📬 Inbox 待处理: 7 条
  - 今天蛋白摄入可能不够
  - 爸爸说他周日要来
  - 那个 DeepL 替代品叫什么来着
  - XX 公司发新产品了 — 要和我们 Q2 的对比
  - 想明年这时候开始学德语
  - @mark 说可以聊聊 API 设计
  - [... +1 条]
```

### 分流到哪里

你在会话里说"处理 inbox"，系统逐条问你怎么办：

| 条目类型 | 去处 |
|---------|------|
| 可以立刻完成（< 2 分钟） | 马上做，不入库 |
| 需要决策 | 触发 3D6M 或 Express 流程 |
| 要研究 | 写进 `projects/{project}/research/` 或 `areas/{area}/notes/` |
| 是 todo | 写进 `projects/{project}/tasks/` 或 `areas/{area}/tasks/` |
| 是知识点 | 写进 `wiki/{domain}/{topic}.md`（或 DREAM 以后抽） |
| 是 SOUL 线索 | ADVISOR 观察、积累 evidence，不直接写 |
| 没用 / 不想做 | 直接删 |

分流完：Notion 里那条 Status 改成 `Synced`，桌面 inbox 文件删掉或归档。

### 手动处理一条

示例：

```
你：帮我把 "想明年这时候开始学德语" 处理掉
ROUTER：这个看起来是意向/目标类。选一个：
  a) 放进 areas/learning/notes/ 当笔记
  b) 创建一个 project "learn-german"
  c) 存到 wiki/life/language-learning.md
  d) 什么都不做，先删掉

你：a

ROUTER：好，写进 areas/learning/notes/2026-04-08-german-intent.md。
       Notion 里标为 Synced。
```

---

## 跨设备同步时机

### 手机 → 桌面

手机写入 Notion Inbox 是即时的（通过 Notion MCP）。桌面下次上朝 RETROSPECTIVE 全量拉取时读到。

**延迟**：从你手机上说那句话，到桌面看到它 = 取决于你下次上朝的时间。可能是 10 分钟，也可能是 2 天。

### 桌面 → 手机

桌面产生的东西（决策、todo、STATUS）通过 ARCHIVER 的 Step 10a 同步回 Notion。手机端就能看到。

**延迟**：从你下"adjourn"到同步完成 = 通常 30 秒以内。

### 同步不走 Notion 以外的手机途径

iOS 的 Shortcut、Android 的 Tasker 等等都没接。要写进 inbox 就一条路 — **经过 Notion**。

如果你不用 Notion：没有手机捕获通道。桌面独立用。

---

## Inbox 的腐烂问题

Inbox 会腐烂。人性是这样的 — 你不断往里丢，但不处理。3 个月后 inbox 里 80 条，你看都懒得看。

### 反腐烂规则

1. **每天开一次会话**。RETROSPECTIVE 强制展示 inbox 数量。数字太大刺痛你。
2. **设硬上限**。超过 50 条晨报会警告。超过 100 条 ADVISOR 会在下一次 Summary Report 结束后说"建议清理 inbox"。
3. **批量处理模式**。说"清理 inbox"，系统逐条问你，不让你逃。
4. **承认失败**。有些条目你就是不想动。直接删。认怂比堆在那里健康。

### Inbox 里的 AUDITOR 巡查

AUDITOR 定期检查：

- Inbox > 30 天未处理 → 标黄。
- Inbox 里出现和现有 wiki 矛盾的内容 → 标橙。
- Inbox 里有明显是决策但从未被决策的 → 标红（提醒你走流程）。

这些会出现在下一次晨报的 AUDITOR 报告区块。

---

## 一个真实例子 · 从手机到归档

**Day 0, 14:32, 地铁上**

你在 Notion 手机端：

```
应该调研下 Notion 竞品看有没有更开源的选择
```

**Day 0, 22:00, 桌面上朝**

晨报：

```
📬 Inbox 待处理: 1 条
  - 应该调研下 Notion 竞品看有没有更开源的选择
```

你："这个放到 areas/learning/notes/ 吧，当作以后要做的研究笔记。"

ROUTER 写入 `areas/learning/notes/2026-04-08-notion-alternatives.md`，Notion 里那条标 Synced。

**Day 14, 22:00, 桌面**

你："今天想认真研究下 Notion 替代品。" → 触发 Express 分析 → 几个 domain 一起跑 → 产出比较报告 → 写进 `areas/learning/notes/2026-04-22-notion-alternatives-comparison.md`。

**Day 30, DREAM**

ARCHIVER 的 DREAM 阶段扫到两篇笔记累计了足够证据 → 抽取成 wiki 条目 `wiki/tools/notion-alternatives.md`，通过 6 准则 + 隐私过滤 → 自动写入。

**Day 180, 未来的你**

你在做另一个项目时提到 Notion。晨报的 wiki INDEX 匹配上，告诉你"我们已经研究过 Notion 替代品了，看 `wiki/tools/notion-alternatives.md`"。

一个零摩擦捕获 → 6 个月后变成可复用的知识。这就是 inbox → wiki 的生命周期。
