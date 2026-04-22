# 上朝 · 18 步启动流程

**本地备忘。不推送 GitHub。给自己看的技术参考。**

上朝 = Start Session。由 RETROSPECTIVE 子代理（Mode 0）在独立上下文中执行。ROUTER 只输出一行"开始上朝 — 18 步启动"，剩下全部由子代理完成。

触发词：`上朝` / `开始` / `start` / `begin` / `はじめる` / `朝廷開始` 等。

权威源：`pro/agents/retrospective.md` Mode 0。

---

## Phase A · 环境检测（步骤 1-3）

### Step 1. THEME RESOLUTION — 主题解析

判断用户触发词能否唯一锁定某个主题。

- `上朝` → 直接加载 `zh-classical`（唐朝专属词），无需询问。输出 `🎨 Theme: 三省六部`。
- `閣議開始` → 直接加载 `ja-kasumigaseki`。
- `开始` / `开会` → 只确定是中文，不确定是哪个中文主题。显示 d/e/f 三选一：三省六部 / 中国政府 / 公司部门。
- `はじめる` → 日语，显示 g/h/i。
- `start` / `begin` → 英文，显示 a/b/c。
- 如果完全无法识别语言，显示 9 主题完整选择器。

为什么必要：主题一旦选定，整个会话的输出语言就定了（HARD RULE）。不能在日语主题下输出中文。不能混用。切换主题必须在会话中途重新显示选择器，用新语言确认。

### Step 2. DIRECTORY TYPE CHECK — 目录类型检测

在当前目录判断处于哪种情境：

- 当前目录是 Life OS 系统仓库（含 `SKILL.md` + `pro/agents/` + `themes/`）→ 问用户：a) 连接 second-brain  b) 我在开发 Life OS，绑定本仓库  c) 新建 second-brain。选 b 跳过步骤 3-7（不需要同步）。
- 当前目录是 second-brain（含 `_meta/` + `projects/`）→ 正常进入步骤 3。
- 其他情况 → 当作普通项目仓库，去配置路径找 second-brain。

为什么必要：不区分的话，在开发 Life OS 本身时会触发同步，把开发数据写进 second-brain。

### Step 3. DATA LAYER CHECK — 数据层检测

检查 `_meta/config.md` 是否存在。

- 存在 → 继续步骤 4。
- 不存在 → FIRST-RUN 模式：
  1. 报告"📦 首次会话 — 未检测到 second-brain"。
  2. 问存储位置：a) GitHub  b) Google Drive  c) Notion。可多选。
  3. 在目标路径创建目录结构：`_meta/`、`projects/`、`areas/`、`wiki/`、`inbox/`、`archive/`、`templates/`。
  4. 写 `_meta/config.md` 记录所选 backend。
  5. 跳过步骤 4-7（没数据可同步），直接到步骤 8。
  6. 晨报输出"✅ second-brain 已创建。尚无项目。告诉我在做什么"。

为什么必要：没有这一步，新用户第一次用会卡住。

---

## Phase B · 同步（步骤 4-7）

### Step 4. 读 config

`_meta/config.md` → 拿到 backend 列表 + last_sync_time。

### Step 5. GIT HEALTH CHECK — Git 健康检查

在任何同步之前扫描：

- `git worktree list` → 如有 entry 显示"prunable"或路径不存在，记录。
- `.claude/worktrees/` → 如有 `.git` 文件指向不存在路径，记录。
- `git config --get core.hooksPath` → 如指向不存在路径，记录。
- 全部干净 → 静默跳过。
- 有问题 → 报告并询问确认后再修复。

为什么必要：GLOBAL.md Security Boundary #1 — 没有用户确认不能执行破坏性操作。worktree 残留会让后续 git 命令失败。

### Step 6. FULL SYNC PULL — 全量拉取

查询所有已配置的 backend，拿到 last_sync_time 之后的变更：

- 比对时间戳，按 `data-model.md` 的规则解决冲突。
- 把赢家写入主 backend。
- 把主 backend 状态推送到所有同步 backend。
- 更新 `_meta/sync-log.md` 和 `last_sync_time`。

为什么必要：多设备。手机在 Notion 上加了一条，桌面要拿到。手机改了一条，桌面要看到。

### Step 7. OUTBOX MERGE — 离线会话合并

扫 `_meta/outbox/` 下的未合并会话目录。这些是在没连 GitHub 时跑的会话，archiver 只能写到 outbox。

- 如果 `_meta/.merge-lock` 存在且 <5 分钟 → 跳过（另一个会话正在合并）。
- 写 `.merge-lock` 锁。
- 对每个 outbox 目录（按时间排序）：
  - 读 `manifest.md`。
  - 移动 `decisions/` → `projects/{project}/decisions/`
  - 移动 `tasks/` → `projects/{project}/tasks/`
  - 移动 `journal/` → `_meta/journal/`
  - 应用 `index-delta.md` → 更新 `projects/{project}/index.md`
  - 追加 `patterns-delta.md` → `user-patterns.md`
  - 移动 `wiki/` → `wiki/{domain}/{topic}.md`
  - 合并成功后删 outbox 目录。
- 全部合并完 → 编译 `_meta/STATUS.md`，git commit + push。
- 删 `.merge-lock`。
- 报告"📮 合并了 N 个离线会话"。

没有 outbox → 静默跳过。

为什么必要：这是 Life OS 的"offline-first"机制。没网也能开会，上来就合并。

---

## Phase C · 版本 + 项目（步骤 8-9）

### Step 8. PLATFORM + VERSION CHECK — 版本检查

- 读本地版本：`SKILL.md` front matter 里的 `version:` 字段。
- WebFetch 远程版本：GitHub 上最新的 SKILL.md。
- 都必须出现在晨报里。
- WebFetch 失败 → 标记"⚠️ check failed"。

为什么必要：用户需要知道是否有新版本。如果失败也要报告，不能静默。

### Step 9. PROJECT BINDING — 项目绑定

- 步骤 2 已经识别出绑定 → 沿用。
- 否则询问"我们关注哪个项目？"

为什么必要：HARD RULE 之一。会话的所有读写都锁定在绑定的项目 scope。跨项目的决策必须显式标"跨项目决策"。否则会话数据乱写。

---

## Phase D · Context 加载（步骤 10-14）

### Step 10. 读 user-patterns.md

用户行为模式记录（ADVISOR 写的）。例如"用户在做金融决策时倾向过度自信"。如果存在就读。

### Step 11. SOUL state + trend — SOUL 状态 + 趋势

这步是晨报 SOUL Health Report 的数据源。细分 6 个子步骤：

- **11.1** 读当前 `SOUL.md`。不存在 → 标"uninitialized"，跳到 11.6。
- **11.2** 读 `_meta/snapshots/soul/` 下最新的 snapshot 文件（按文件名 `YYYY-MM-DD-HHMM.md` 倒序）。这是上一次会话结束时的 SOUL 状态。
- **11.3** 对当前每个 dimension 算 delta：
  - `evidence_Δ` = 当前 evidence_count − snapshot.evidence_count
  - `challenges_Δ` = 当前 challenges − snapshot.challenges
  - `confidence_Δ` = 当前 confidence − snapshot.confidence
  - 当前有但 snapshot 没有 → 🌱 NEW（不算 delta）
  - snapshot 有但当前没有 → 🗑️ REMOVED（用户删了）
- **11.4** 从 `confidence_Δ` 推导趋势箭头：
  - `> +0.05` → ↗
  - `< −0.05` → ↘
  - `|Δ| ≤ 0.05` → →
- **11.5** 识别特殊状态：
  - 跨过 0.7 向上 → 🌟 "新晋核心"
  - 跨过 0.7 向下 → ⚠️ "从核心降级"
  - `last_validated` >30 天 → 💤 "休眠"
  - 最近 3 个 challenges > 最近 3 个 evidence → ❗ "冲突区"
- **11.6** 把这 5 类数据喂给晨报的 SOUL Health Report。

Edge cases：
- 第一次会话（没 snapshot）→ 所有 dimension 都标 🌱 NEW，箭头省略，晨报加一句"首次会话 — 无趋势数据"。
- snapshot 损坏无法解析 → 退化成"只看当前状态"，晨报加"⚠️ 趋势对比不可用"。
- snapshot >24 小时 → 仍用，但加注"趋势相对于 {时间戳}"。

### Step 12. 读 STATUS.md + lint-state

- `_meta/STATUS.md` — 全局状态。
- `_meta/lint-state.md` — 上次 lint 时间。
- 如果 >4h 没跑 lint → 触发 AUDITOR 轻量巡查。

### Step 13. ReadProjectContext

读绑定项目的完整上下文：`index.md` + `decisions/` + `tasks/` + `journal/`。这个会话之后所有的决策推理都基于这份 context。

### Step 14. Global overview — 全局概览

列出所有 Project + Area 的标题和状态。不深读，只要标题。

---

## Phase E · Strategy + Knowledge（步骤 15-17）

### Step 15. STRATEGIC MAP COMPILATION — Strategic Map 编译

不是每次都跑 — 只有 `_meta/strategic-lines.md` 存在时才跑。

a. 读 `strategic-lines.md` → 所有 line 定义（driving_force、health_signals）。
b. 读所有 `projects/*/index.md` → 收集 strategic 字段。
c. 对每条 line：
   - 收集项目，按 role 排序（critical-path 优先）。
   - 匹配 health 原型（见 `strategic-map-spec.md`）。
   - 写 narrative：在发生什么 + 意味着什么 + 今日行动含义。
   - 检测盲区：断链、衰减、信息缺失。
d. 跨层验证：
   - SOUL × strategic lines：driving_force 是否和 SOUL 对齐？
   - wiki × flows：cognition 流的域是否有 wiki 内容？
   - user-patterns × roles：行为是否匹配战略优先级？
e. 生成 action 建议（🥇🥈🟢❓）。
f. 编译 `_meta/STRATEGIC-MAP.md`。

STRATEGIC-MAP.md 是编译产物 — 不能手改。

为什么必要：让 ROUTER 拿到跨项目视图。否则每次会话只能看当前项目，看不到全局。

### Step 16. DREAM REPORT — 读最近的 DREAM

读 `_meta/journal/` 里最新的 `*-dream.md`（如果存在且未展示过）：

- 晨报显示"💤 上次会话系统做了个梦：[摘要]"。
- 列出自动写入的 SOUL dimension（标 confidence 0.3，等用户填 What SHOULD BE）。
- 列出自动写入的 Wiki 条目（列路径，用户如不认同可删）。
- 列出被丢弃的候选 + 原因（6 条准则未过 / 隐私过滤剥光）。
- 标记为已展示（下次不再显示）。
- 读 `triggered_actions` YAML 块 — 这是晨报 "DREAM Auto-Triggers" 区块的数据源，10 个自动触发器中哪些被触发了。

为什么必要：v1.6.2 的核心设计 — 让 SOUL 和 DREAM 可见。上次会话的发现必须在下次会话露面，否则就是白做。

### Step 17. WIKI HEALTH CHECK — Wiki 健康检查

a. `wiki/` 为空或不存在 → 静默跳过。
b. `wiki/` 有文件但没 `INDEX.md` → 从符合规范的文件编译，报告 legacy 条目。
c. `INDEX.md` 存在 → 重新编译一遍（可能有新条目）。
d. 报告"📚 Wiki: N 个条目，M 个域"。

为什么必要：Wiki 是所有会话共享的知识。没有 INDEX，domain agents 无法知道已有前提。

---

## Phase F · 输出（步骤 18）

### Step 18. GENERATE BRIEFING — 生成晨报

把 1-17 步的所有结果编译成最终输出。格式见 `the-briefing.md`。

---

## 真实触发例子

```
用户: 上朝
ROUTER 输出: 🌅 开始上朝 — 18 步启动准备...
            Launch(retrospective) Mode 0
子代理执行 1-18 步
子代理输出: (完整晨报)
```

如果 ROUTER 自己开始执行步骤内容，就违反 HARD RULE — AUDITOR 会标记为流程违规。ROUTER 的唯一职责：输出那一行触发模板 + launch 子代理。

## 为什么要 18 步这么多

每一步都对应一类历史故障：

- 少了步骤 1 → 语言乱（用户说"上朝"结果输出日文）。
- 少了步骤 2 → 在 Life OS 仓库里开会，把开发数据写进个人 second-brain。
- 少了步骤 5 → worktree 残留导致 git pull 爆炸。
- 少了步骤 7 → 离线会话的数据永远卡在 outbox。
- 少了步骤 11 → SOUL 演化不可见，用户永远不知道系统在看到什么。
- 少了步骤 16 → DREAM 做完就埋了，白白浪费一整个夜间周期。

18 步不是过度设计。是历史 bug 的沉淀。
