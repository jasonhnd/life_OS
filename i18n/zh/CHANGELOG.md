# 更新日志

## 版本规则

本项目遵循 **Strict SemVer**：MAJOR（破坏性变更）· MINOR（新功能）· PATCH（修复与维护）。同一天的变更合并为单次发布，每次发布打 git tag。

---

## [1.8.0] - 2026-04-28 - Daily Cycle 混合化（cron + monitor + 软化上朝/退朝）

> **Life OS 历史上最大的单次 release**。把 lifeos 从「反应式 chatbot」（必须由用户驱动）转变为「混合 OS」（reactive + autonomous）。三种正交模式并存：业务 session（长期持续）、monitor session（`/monitor`）、cron 自治（10 job + RunAtLoad）。

### 新增 · Session Modes（核心架构变化）

- **Mode 1 · 业务 session**：长期持续，session 可跨天/周。**上朝/退朝降级为可选软触发**。
- **Mode 2 · Monitor session**：`/monitor` slash command 进入运维控制台模式。
- **Mode 3 · Cron 自治**：10 个调度 job + 1 个 RunAtLoad。

### 新增 · Cron jobs（v1.8.0 新增 5 个，共 10 + 1 RunAtLoad）

新增：spec-compliance / wiki-decay / archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency / missed-cron-check。**激活 v1.6.x 起承诺过但 0 次 cron 触发的多个 spec**。

### 新增 · Slash commands（2 个）

- `/monitor` — 进入 monitor 模式
- `/run-cron <job>` — 手动触发

### 新增 · Hooks（3 个）

- `session-start-inbox` — cron→session 桥
- `pre-task-launch` — 机器强制 v1.7.3 carve-out
- `post-task-audit-trail` — 即时 R11 audit trail 检查

### 新增 · Python tools（4 个）+ Cron prompts（5 个）+ Spec docs（2 个）+ 新 subagent

- 4 python: `spec_compliance_report` / `wiki_decay` / `cron_health_report` / `missed_cron_check`
- 5 prompts: `scripts/prompts/{archiver-recovery,auditor-mode-2,advisor-monthly,eval-history-monthly,strategic-consistency}.md`
- 2 specs: `references/{automation-spec,session-modes-spec}.md`
- 1 subagent: `pro/agents/monitor.md`
- 1 trigger script: `scripts/run-cron-now.sh`

### 变更

- **pro/CLAUDE.md** 新增 "Session Modes (v1.8.0)" section
- **scripts/setup-cron.sh** 从 3 → 10 cron jobs + 1 RunAtLoad
- **scripts/setup-hooks.sh** 注册 3 个新 hook
- **scripts/hooks/pre-prompt-guard.sh** 上朝/退朝 reminder 软化
- **版本标记**：SKILL.md + 3 README badge → 1.8.0

### 发布后修复（折回 v1.8.0 — 版本号不变，按"所有 bug 都属于这个版本"原则）

- **R-1.8.0-001 · `scripts/setup-hooks.sh`**：缺失 9 个变量声明（3× `HOOK_*_ID`、3× `V18_*_SOURCE`、3× `V18_*_DEST`），被 `copy_exec` / `register_hook` 引用却从未定义。setup 报错"未定义变量 V18_SESSION_START_INBOX_SOURCE"。已在 line 52-54、66-68、80-82 补齐声明。
- **R-1.8.0-002 · `scripts/run-cron-now.sh`**：使用了 bash 4+ 的 `declare -A` 关联数组。macOS 自带 bash 3.2.57（GPLv2 永远停在那一版），脚本在 Mac 上 100% 失败。改写 JOBS 表为基于 `case` 的 `job_spec()` 查找函数 + 独立的 `JOB_NAMES` 列表。同时把 data root 改成 `$LIFEOS_DATA_ROOT`（环境变量）→ `$PWD`（cwd）→ 失败并清晰报错。
- **R-1.8.0-003 · `scripts/setup-cron.sh`**：灾难性的 root 混淆 bug。`REPO_ROOT` 同时被用于查找 `tools/cli.py`（正确：skill 源码）和生成命令里的 `cd` + `--root .`（错误：应该是用户的 second-brain repo）。结果：所有 11 个 cron job 扫描的是空的 skill 目录，全部报告"0 sessions / 0 SOUL / 0 projects"。引入独立的 `DATA_ROOT`（来自 `$LIFEOS_DATA_ROOT` 或 `$PWD`），并贯穿到 `repo_command{,_pymod,_prompt}`（python：`--root "$DATA_ROOT"`；prompt：`cd "$DATA_ROOT"`），以及全部 6 个 `print_launchd_plist*` 生成器（`<key>WorkingDirectory</key>` 现在来自 `$DATA_ROOT`）。在 `main()` 中加入 `require_data_root()` 早期检查，给出可执行的报错信息。
- **R-1.8.0-004 · `tools/spec_compliance_report.py`**：root 校验 guard 检查 `(root / "SKILL.md").is_file()` 来识别 Life OS root，但 `SKILL.md` 只存在于 skill 源码 — 不在用户 second-brain repo 里。每次安装都会报"no SKILL.md"中断。改为 `(root / "_meta").is_dir()`，匹配真正的数据 root 标记。
- **R-1.8.0-005 · `tools/wiki_decay.py`**：与 R-1.8.0-004 同样的 `SKILL.md`-vs-`_meta/` 不匹配 bug。同样修法。
- **`tools/missed_cron_check.py`**（与 R-1.8.0-004 一起前置修复）：line 134 有同样的 `SKILL.md`-vs-`_meta/` bug 模式；下次 macOS 重启时会通过 RunAtLoad plist 触发。预防性应用 R-1.8.0-004 的同样修法。
- **R-1.8.0-006 · `scripts/setup-cron.sh` · `repo_command_prompt`**：cron 拉起的 `claude -p` session 没有 pre-approved Write 权限，所以每个 prompt-based job（archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency）跑完分析后阻塞在 Write tool 权限弹窗上 — 没人按 yes，session 5-15 分钟后超时退出。结果：exit 0 但**啥都没写** — 100% 数据丢失。给生成的 `claude -p` 命令加 `--dangerously-skip-permissions` flag。安全边界仍由 `cd "$DATA_ROOT"`（无法越界 second-brain）+ prompt 文件版本受控（`scripts/prompts/`）保证。
- **R-1.8.0-007 · `tools/missed_cron_check.py` · `trigger_recovery`**：在 `data_root/scripts/` 下找 `run-cron-now.sh`，但 R-1.8.0-003 修完后 `data_root` 是用户 second-brain — 那里没 `scripts/`。之前装过 v1.8.0 的 Mac 上，`data_root/scripts/` 里残留一份 R-1.8.0-002 修复前的旧 `run-cron-now.sh`（还带 `declare -A`），结果上游虽然 patch 了但被调用的是旧版，报 "declare -A: invalid option"。改成用 `Path(__file__).resolve().parent.parent / "scripts" / "run-cron-now.sh"` 解析路径，**永远调用当前上游版本**，并通过 subprocess env 传 `LIFEOS_DATA_ROOT` 让脚本知道数据 root。
- **R-1.8.0-008 · `scripts/setup-cron.sh` · PATH 扩展**：launchd 拉起的 shell 的 PATH（`~/.local/bin:/opt/homebrew/bin:/usr/local/bin:...`）不包含 Claude Code 常见的安装位置（`~/.claude/local`、`~/.bun/bin`、`~/.npm-global/bin`、`~/.volta/bin`），所以 `command -v claude` 返回 false，`archiver-recovery`（以及所有 prompt job）报 "claude CLI not found"。在全部 3 个命令生成器（`repo_command`、`repo_command_pymod`、`repo_command_prompt`）的 PATH export 行加上这 4 个安装位置。
- **`tools/seed.py`**：`META_GITKEEP_DIRS` 缺失 `_meta/inbox`、`_meta/runtime` 以及三个 `_meta/eval-history/` 子目录（`cron-runs`、`auditor-patrol`、`recovery`）。`tools/seed.py` 新建的 second-brain repo 没有 v1.8.0 cron prompt 与 `session-start-inbox` hook 写入的目录。同时初始化 `_meta/inbox/notifications.md` 头部，使 cron→session 桥接从第一天起就有可写目标。
- **`scripts/setup-cron.sh`**（与 seed.py 修复配套）：新增 `bootstrap_repo_dirs()` 辅助函数，由 `main` 在 `ensure_repo` 之后调用。幂等地为本次修复之前 seed 的**已存在** second-brain repo 补齐相同目录 + notifications.md 头部。现在 keyed off `$DATA_ROOT/_meta` 而非 `$REPO_ROOT/_meta`（R-1.8.0-003 清理）。

- **R-1.8.0-010 · 架构 PIVOT (post-2026-04-29) · cron 架构整体砍掉**：经过两天真实环境测试，R-1.8.0-001~009 修完之后的 cron 架构仍然在用户可靠性测试中失败。5 个 prompt-based cron job（archiver-recovery / auditor-mode-2 / advisor-monthly / eval-history-monthly / strategic-consistency）静默丢数据：cron 拉起的 `claude -p` session 完成分析后用 prompt 模板的礼貌语气问用户「需要我写吗？」—— cron 没人盯着，session timeout，exit 0，`_meta/eval-history/` 是空的。`--dangerously-skip-permissions` flag（R-1.8.0-006）只跳过 OS 级 Write 权限，不能跳过 LLM 自身的对话礼貌。结论：**cron 要求确定性，LLM 是非确定性，这个矛盾没法 patch**。
  - **Pivot 决定（用户拍板）**：把 cron 替换成显式用户提示。用户说「重建索引」/「月度自审」，ROUTER 读 `scripts/prompts/<job>.md` 然后内联执行。无后台进程。
  - **删除 (17 文件)**：`scripts/setup-cron.sh`、`scripts/run-cron-now.sh`、`scripts/commands/run-cron.md`、`tools/missed_cron_check.py`、`tools/cron_health_report.py`、`tools/reindex.py`、`tools/daily_briefing.py`、`tools/backup.py`、`tools/spec_compliance_report.py`、`tools/wiki_decay.py`、`tools/memory.py`、`tools/session_search.py`、`tools/cli.py`、`pro/agents/narrator-validator.md`、`references/automation-spec.md`、`references/session-modes-spec.md`、`docs/architecture/hermes-local.md`。还有 3 个删除工具的 eval scenarios。
  - **新建 (5 个 user-invoked prompts)**：`scripts/prompts/{reindex,daily-briefing,backup,spec-compliance,wiki-decay}.md` —— 替代被删的 python 工具。每个是一个 markdown prompt，ROUTER 读完用 Read/Write/Bash/Glob/Grep 直接做（用户用关键词触发）。
  - **修改 (5 个现有 prompts)**：`scripts/prompts/{archiver-recovery,auditor-mode-2,advisor-monthly,eval-history-monthly,strategic-consistency}.md` —— 把"autonomous cron-triggered"框架换成"user-invoked from session"框架。删了 UNATTENDED CRON CONTRACT 块（不再需要）。
  - **Hooks 重构 (3 个 hook)**：
    - `scripts/hooks/pre-prompt-guard.sh`：删 Cortex always-on enforcement 块（line 111-167）。Memory 关键词检测现在用 Write tool 直接写 `~/.claude/lifeos-memory/<key>.json`，不再调被删的 `tools/memory.py`。上朝/退朝软触发保留。
    - `scripts/hooks/session-start-inbox.sh`：完全重写 —— 之前读 cron 输出，现在扫 10 个维护任务的 glob 找最新文件 mtime（`_meta/eval-history/<job>-*.md`），把 overdue 的总结成 `<system-reminder>`。Hook 只显示，不执行；用户决定要不要触发。
    - `scripts/hooks/post-task-audit-trail.sh`：弱化 —— 删了 Cortex 4 个 subagent + narrator-validator 的 R11 audit trail 强制。只剩 archiver + knowledge-extractor 强制写 trail（它们触碰持久状态）。
  - **Cortex 改 pull-based**（`pro/CLAUDE.md` §0.5 重写）：4 个 Cortex subagent 不再每条消息都 launch。ROUTER 按消息判断回答是否会因为加上历史/概念/SOUL 而变好；会 → launch，不会 → 不 launch。Subagent description 文件全部更新反映 pull-based。
  - **Slash command 重写**：`/monitor` 现在是 view-and-invoke 控制台（不是 cron 监控）；`/memory` 现在直接写 JSON 文件（不调 python 中间层）；`/search` 现在用 Grep tool 直接搜（不走 SQLite FTS5）。
  - **Spec 文档**：`pro/CLAUDE.md` §0.5 + Session Modes section 重写。`references/hard-rules-index.md` 更新 Cortex 不再 always-on。`pro/AGENTS.md`、`pro/GEMINI.md`、`AGENTS.md` 顶部加 pivot 提示指向 `pro/CLAUDE.md` 为权威（完整内容扫描待办）。
  - **统计**：~3500 行 cron 基础设施 + python 中间层删除。~500 行 user-invoked prompt 内容新增。净：23 删、5 创、~25 改。
  - **备份**：`git branch backup-pre-v1.8-pivot @ 7b15509` 保留 pivot 前状态。

- **R-1.8.0-011 · 架构 PIVOT 第二阶段 (post-2026-04-29) · Bash 骨架 + cortex helpers + python 中间层全部砍 → 100% LLM**：R-1.8.0-010 砍了 cron 层之后，R-1.8.0-011 砍下一层"确定性 helpers"：Bash briefing 骨架、cortex Python 数据模型 helpers、剩下的维护 python 工具。目标：最小可行架构 = `hooks（免疫系统）+ approval.py（安全）+ 5 个一次性 bootstrap 脚本 + 其他全部 LLM 直接做`。
  - **Pivot 决定（用户拍板，"全 LLM 因为我要增强实用型"）**：每个 LLM 能合理做的 helper 都该 LLM 化；只有 hooks（OS 协议要求）和 `approval.py`（安全边界）留代码。
  - **删除 (23 文件)**：
    - Cortex helpers (5)：`tools/lib/cortex/{__init__,concept,extraction,session_index,snapshot}.py`
    - Cascade .py (4)：`tools/extract.py`、`tools/rebuild_session_index.py`、`tools/rebuild_concept_index.py`、`tools/migrate.py`
    - Bash 骨架 + telemetry (4)：`scripts/retrospective-briefing-skeleton.sh`、`scripts/archiver-briefing-skeleton.sh`、`scripts/retrospective-mode-0.sh`、`scripts/archiver-phase-prefetch.sh`
    - Cortex broken FTS5 helper (1)：`scripts/lib/cortex/hippocampus_wave1_search.py`
    - 死掉的测试 (9)：`tests/test_{backup,cli,daily_briefing,reindex,extraction,concept_and_snapshot,session_index,package_imports,migrate}.py`
  - **新建 (5 个 user-invoked prompts，替代被删的 python 工具)**：
    - `scripts/prompts/rebuild-session-index.md`、`scripts/prompts/rebuild-concept-index.md`、`scripts/prompts/migrate-from-v1.6.md`、`scripts/prompts/snapshot-cleanup.md`、`scripts/prompts/extract-concepts.md`
  - **Spec 重写 (5 个 agent spec)**：
    - `pro/agents/hippocampus.md` L88-92：FTS5 SQLite helper → 用 Grep tool 直接扫 INDEX.md
    - `pro/agents/retrospective.md` L47-55：删 Python helper 路径，只剩 inline LLM rebuild；L244 R10 boundary 重写
    - `pro/agents/archiver.md`：snapshot Python helper 块 → inline Write + 显式 YAML schema；extraction Python helper → inline tokenize/stopword/slug 步骤；SessionSummary Python helper → 直接 Write + 显式 byte-level 格式合同；v1.7.2.3 rationale 块更新
    - `pro/CLAUDE.md` L268-286：HARD RULE briefing skeleton 块（retrospective + archiver）删除
  - **接受的代价**：retrospective Mode 0 ~30× 慢；archiver Adjourn 10-12 min → ~25-30 min；hippocampus Wave 1 失去 FTS5 stemming
  - **接受的风险**：SessionSummary 格式漂移、Concept slug 漂移（SHA-1 兜底缓解）、SOUL snapshot 累积、6-H2 briefing 可能漏 H2
  - **保留的代码（不可侵犯）**：11 hooks + `tools/approval.py` + `seed.py` / `seed_concepts.py` / `skill_manager.py` + `tools/lib/{config,llm,notion,second_brain}.py` + `scripts/lib/{audit-trail.sh,sha-fallback.sh}` + R-1.8.0-010 的 10 个 cron-replacement prompts
  - **统计**：~3500 行删除，~700 行新增。净：-2800 行。
  - **备份**：`git branch backup-pre-option-A @ 744d034`。

- **R-1.8.0-012 · Monitor mode 改为纯自然语言触发（post-2026-04-29 用户反馈）**：用户原话「这个不能要任何命令全部都要自然语言」。Monitor mode 必须通过自然语言关键词触发，不能要求用户打 `/monitor`。Slash 命令保留为 backup mode（与 `/memory` `/search` `/method` 一致）。
  - **`scripts/hooks/pre-prompt-guard.sh`**：在 `MEMORY_KEYWORD_RE` 检测块后新增 `MONITOR_KEYWORD_RE` 检测块。关键词：监控模式 / 进监控 / 进 monitor / 开监控 / 监控控制台 / 看系统状态 / 看 cron / 看维护状态 / 维护控制台 / ops console / monitor mode / enter monitor / open monitor / 看 lifeos 状态 / 进运维。匹配时注入 `<system-reminder>`（`trigger=monitor`）让 ROUTER 直接 `Task(subagent_type=monitor)` —— 不要引导用户去打 `/monitor`。
  - **`scripts/hooks/pre-prompt-guard.sh`**（同次 edit 中修复 —— R-1.8.0-010 漏修）：MEMORY 块文本还在叫 ROUTER 跑 `python -m tools.memory emit "..."`，但 `tools/memory.py` 已经在 v1.8.0 pivot 中删了。改成让 ROUTER 用 Write tool 直接写 `~/.claude/lifeos-memory/<sanitized-key>.json`，附明确 JSON schema（`value` / `role` / `created` / optional `trigger_time`）。
  - **`pro/CLAUDE.md` Special Triggers 段**：在 上朝 / 退朝 / Quick Mode 旁边加 Monitor Mode 条目。说明自然语言是主路径，`/monitor` 是 backup。
  - **`pro/CLAUDE.md` Auto-Trigger Rules 段**：在 Memory auto-emit 旁边加 "Monitor mode auto-launch" 子段。列出中/英关键词。"4 个 v1.7.3 slash commands"说明扩展为 5 个（包含 `/monitor`）。
  - **`scripts/commands/monitor.md`**：顶部加 "Backup mode" 提示块。告诉 ROUTER 不要引导用户输入 slash 命令 —— 自然语言是主路径。Slash 命令保留给：精确控制 focus 参数（`/monitor wiki`）、auto-trigger fallback（regex 漏匹配）、测试场景。
  - **不破坏任何路径**：`/monitor` slash 命令 power user 还能用；`pro/agents/monitor.md` subagent 本身未改。只是入口扩展。

- **R-1.8.0-013 · 借鉴 llm_wiki 的 5 项改造（post-2026-04-29 用户调研后决定）**：用户原话「1，单独 2，llm 3，折中 4，全，完整」一次性批准全部 5 项借鉴。lifeos 从「纯文本 + frontmatter id」转为「Obsidian-vault 兼容的 wikilink 知识图 + 异步 review queue + LLM 友好的关联度信号 + 页面分类细化」。源参考：[nashsu/llm_wiki](https://github.com/nashsu/llm_wiki)。
  - **借鉴 1 · 全文 Obsidian `[[wikilinks]]` 语法**：`wiki/`、`_meta/concepts/`、`_meta/sessions/`、`_meta/methods/`、`_meta/people/`、`_meta/comparisons/`、`SOUL.md`、`_meta/STRATEGIC-MAP.md` 正文中所有交叉引用统一用 `[[id]]` 或 `[[id|显示名]]`。Frontmatter 保持纯 YAML 字符串（机器可解析），唯一例外：`_meta/concepts/<id>.md` 的 `provenance.source_sessions: ["[[YYYY-MM-DD]]"]` 和 `outgoing_edges[].target: "[[concept-<id>]]"`。`references/wiki-spec.md` 中"禁止交叉引用"规则被划线作废。
  - **借鉴 2 · Obsidian vault 布局**：`tools/seed.py` 现在写入 `.obsidian/app.json`（`useMarkdownLinks: false`、`newLinkFormat: shortest`、`userIgnoreFilters` 排除 `_meta/runtime/`）、`.obsidian/core-plugins.json`（启用 graph + backlinks + outgoing-links + tag-pane）、`.obsidian/.gitignore`（排除 workspace.json 等设备本地状态）。用户可以直接用 Obsidian 打开 second-brain 看图谱 + 反向链接面板。规范：`references/obsidian-spec.md`。
  - **借鉴 3 · 异步 Review Queue（"需要用户处理"的统一入口）**：`_meta/review-queue.md` 把之前散在 7 处的待办整合成一个有序列表（auditor-patrol / advisor-monthly / strategic-consistency / archiver-recovery / eval-history-monthly 各报告的 action items + violations.md + cron notifications.md）。YAML 项 schema：`id`（`r{YYYY-MM-DD}-{NNN}`）/ `created` / `source` / `type` / `priority`（P0/P1/P2）/ `summary` / `detail_path` / `related`（wikilinks）/ `suggested_action` / `status`（open/reviewed/resolved/dismissed）/ `closed_at` / `closed_by`。原地状态变更（必须用 Edit，禁止 Write）；resolved > 100 项自动归档到 `_meta/review-queue/archive/{YYYY-MM}.md`（折中策略，对应用户选 3）。规范：`references/review-queue-spec.md`。新走读 prompt `scripts/prompts/review-queue.md`（"处理 queue" / "看 queue" / "review queue"）逐项处理，提供 A（执行）/ R（看过暂不处理）/ D（dismiss）/ S（skip）/ Q（quit）选择。
  - **借鉴 4 · 4 信号 LLM 友好关联度模型（替换 hippocampus Wave 2 的简单加权公式）**：`relevance(candidate, current) = 3 × direct_link_count + 4 × source_overlap_count + 2 × common_neighbor_count + 1 × type_affinity`。用计数（不用 Adamic-Adar 的 `1/log(degree)`）是因为 LLM 不能可靠算 log（对应用户选 2 "LLM 简化版"）。Type affinity 矩阵：同类 1.0、相关（concept↔wiki/person/method）0.5、不相关 0.0。改在 `references/hippocampus-spec.md` Wave 2 + `pro/agents/hippocampus.md`。
  - **借鉴 5 · 页面分类细化 —— people 和 comparisons 各自独立目录**：新增 `_meta/people/<id>.md`（people 作为一等公民；canonical_name / aliases / relationship / privacy_tier / mention_count / concepts_linked wikilinks；规范：`references/people-spec.md`）和 `_meta/comparisons/<id>.md`（决策对比作为一等公民；options / criteria / decision / confidence / outcome 跟踪；规范：`references/comparison-spec.md`），对应用户选 1 "单独，独立目录而不是只加 frontmatter type 字段"。Sources/synthesis/queries 不拆（与 sessions/wiki 重叠）。
  - **新增规范文件（4）**：`references/people-spec.md`、`references/comparison-spec.md`、`references/obsidian-spec.md`、`references/review-queue-spec.md`。
  - **修改规范文件（3）**：`references/wiki-spec.md`（页面分类 + wikilink convention 段，"禁止交叉引用"被划线）、`references/concept-spec.md`（wikilink convention 含 frontmatter 例外字段示例）、`references/hippocampus-spec.md`（Wave 2 4 信号公式）。
  - **修改 subagent（5）**：`pro/agents/hippocampus.md`（Wave 2 spec 同步）、`pro/agents/archiver.md`（Phase 2 路由 + wikilink 写入 HARD RULE + review queue append）、`pro/agents/knowledge-extractor.md`（同样的路由/wikilink/queue HARD RULE）、`pro/agents/retrospective.md`（Mode 0 简报含 wikilinks + 有项时输出 ## Open Review Queue H2 段）、`pro/agents/monitor.md`（Review Queue Dashboard）。
  - **修改 prompt（5 维护 + 2 新）**：5 个 v1.8.0 维护 prompt（`auditor-mode-2.md` / `advisor-monthly.md` / `strategic-consistency.md` / `archiver-recovery.md` / `eval-history-monthly.md`）都加了 "v1.8.0 R-1.8.0-013 · Review Queue Append (HARD RULE)" 段和源特定 YAML 模板。新增 `scripts/prompts/review-queue.md`（借鉴 3 的走读器）和 `scripts/prompts/migrate-to-wikilinks.md`（全量迁移老内容到 wikilink，对应用户选 4 "全，完整"）。
  - **修改工具（1）**：`tools/seed.py` —— 新增 3 个 `META_GITKEEP_DIRS`（`_meta/people`、`_meta/comparisons`、`_meta/review-queue/archive`）、常量 `_REVIEW_QUEUE` / `_OBSIDIAN_APP_JSON` / `_OBSIDIAN_CORE_PLUGINS` / `_OBSIDIAN_GITIGNORE`、函数 `_write_obsidian_vault(target)` 接入 `_seed_scaffolding()`。冒烟测试通过。
  - **修改 hook（1）**：`scripts/hooks/session-start-inbox.sh` —— 新增 awk 解析 `_meta/review-queue.md` `## Open items` 段，按 P0/P1/P2 分级计数；SessionStart system-reminder 输出 `📋 Review queue: N P0 / M P1 / K P2 open. Latest: <summary>. Say "看 queue" to walk through.`。
  - **R-1.8.0-013 自审修复（同次提交）**：并行 agent 审查发现 7 个真实 bug，全部修复在同一发版（用户原话「全部干完，不要再留任何 bug 了」）：
    - **HIGH · awk priority 正则未锚定** —— 模式 `/priority: P0/` 会匹配正文中如 `summary: "因为 priority: P0 上周没处理"` 的字串导致重复计数。锚定为 `^[[:space:]]*priority:[[:space:]]*P0([^0-9]|$)`（不依赖 GNU awk 的 `\b` 词边界）。同时正确处理无空格（`priority:P0`）和多空格（`priority:    P0`）变体。
    - **HIGH · CHANGELOG 承诺 session-start hook 输出 `Latest: <summary>` 但 hook 只输出计数** —— awk 扩展为捕获最新 open 项的第一个 `summary:` 字段，截断到 80 字符，通过 `Latest: ${REVIEW_QUEUE_LATEST}` 行输出。bash 用 tab 分隔符切分。新增 `[[person-*]]` 项 `privacy_tier: high` 的隐私过滤提示。
    - **HIGH · `source_session(s)` 字段单复数不一致** —— `references/comparison-spec.md`（单数，一个决策时刻）和 `references/concept-spec.md`（复数，累积证据）字段命名不同。在 `references/wiki-spec.md` 例外字段列表中明确语义差异，同步 `pro/agents/archiver.md` + `pro/agents/knowledge-extractor.md` 同时引用两个字段名并说明各自的 cardinality 理由。
    - **HIGH · 4 信号 `type_affinity` related 集合不全** —— CHANGELOG 提到 `concept↔wiki/person/method` 但 spec + agent 只写 `concept↔wiki, concept↔person`。统一到：`concept ↔ wiki, concept ↔ person, concept ↔ method, wiki ↔ method, person ↔ comparison`。
    - **MEDIUM · advisor-monthly 缺 `outcome-unmeasured` 类型枚举** —— 加入 type 列表 + 扩展 priority 包含 P2（用于 comparison-spec 的 outcome-tracking 流程检测「过 90 天 comparison 仍无 ## Outcome」）。
    - **MEDIUM · awk 错误静默吞掉** —— 去掉 awk 命令的 `2>/dev/null`，让解析器回归错误浮到 SessionStart hook log，而不是静默输出空字符串。新建 vault 文件不存在时仍由 `|| true` 保留。
    - **LOW · pre-prompt-guard 两个 hook 块同时触发** —— 同时含 REVIEW_QUEUE + MIGRATE_WIKILINKS 关键词的消息会注入两个相互竞争的 `<system-reminder>`。两个块都加 `[ "$ACTIVITY_REMINDER" != "yes" ]` first-match-wins 守卫。
    - **LOW · `_OBSIDIAN_GITIGNORE` 常量命名与 repo 根的 `_GITIGNORE` 重叠** —— `tools/seed.py` line 244 加 inline 注释说明它是 vault 内部那个。
    - **LOW · 触发关键词列表在 hook + pro/CLAUDE.md + walker prompt 之间漂移** —— 指定 `scripts/hooks/pre-prompt-guard.sh` REVIEW_QUEUE_RE 为权威源，更新 CLAUDE.md 和 `scripts/prompts/review-queue.md` 对齐。
  - **R-1.8.0-013 第二轮自审修复（同次提交）**：6 个 agent 并行深度审查（python-reviewer + silent-failure-hunter + code-reviewer + security-reviewer + comment-analyzer + type-design-analyzer）发现**还有 15 个 bug**，含 3 个 CRITICAL/HIGH 会让每个新装的 vault Obsidian 集成静默失败。全部修复：
    - **HIGH · Obsidian core-plugin ID 错的** —— `tools/seed.py` 写入 `.obsidian/core-plugins.json` 用了 `"backlink"`、`"outgoing-link"`、`"starred"`，但 Obsidian 实际的 plugin ID 是 `"backlinks"`、`"outgoing-links"`、`"bookmarks"`（最后这个在 Obsidian 1.2 / 2023 年 8 月从 `starred` 改名）。Obsidian 对未识别的 plugin ID 是静默忽略——意味着每个新装的 lifeos vault 在 Obsidian 里打开时，反向链接面板、出向链接面板、书签面板全部静默关闭。三个 ID 全改对 + 加 Obsidian 文档 URL 的注释块。
    - **HIGH · `.obsidian/.gitignore` 缺 `cache`、`plugins/`、`themes/`** —— 用户装的 community plugin / theme 会被静默 commit 到 git，污染 repo。补全 + 加 `hot-reload.json`（开发流程）+ 加注释解释为什么需要两个 `.gitignore` 文件（Obsidian Sync 不读 vault-root `.gitignore`）。
    - **HIGH · awk parser 在 CRLF + BOM 上崩** —— Windows 编辑器保存的 `_meta/review-queue.md` 带 CRLF 或 BOM 时会静默出 0 计数。加 `{ sub(/\r$/, "") }` 第一条 awk 规则 + `NR == 1 { sub(/^\xef\xbb\xbf/, "") }` 去 BOM。
    - **HIGH · awk substr() 按字节切 UTF-8** —— POSIX awk substr 是按字节索引，所以 `substr($0, 1, 77)` 可能把 3 字节的中文字符从中间切掉，输出 invalid UTF-8 乱码。改成 `substr($0, 1, 67) "..."`（配合 `length > 70` 守卫），留 3 字节安全余量。同时加 block-scalar 守卫（`if ($0 ~ /^[|>][-+]?[[:space:]]*$/) { next }`）让 YAML `summary: |\n  text` 不会显示成 `Latest: |`。
    - **HIGH · YAML 三层方括号语法是无效的** —— `references/people-spec.md` 和 `references/comparison-spec.md` 例子写的 `concepts_linked: [[[concept-id-1]], [[concept-id-2]]]` 以为是 wikilink 数组，但 PyYAML 把 bare `[[x]]` 解析成嵌套列表 `[['x']]`，不是 wikilink 字符串。已实测验证。改成带引号的字符串：`concepts_linked: ["[[concept-id-1]]", "[[concept-id-2]]"]`。同时给两个 spec 加了 required-fields 列表 + 不变量文档。
    - **HIGH · concept-spec 有两套互相矛盾的 `outgoing_edges` schema** —— 第 82 行原版用 `to: concept_id`、`via:`、`last_reinforced:`；R-1.8.0-013 加的第 417 行用 `target: "[[]]"`、没 `via:`、`last_co_activated:`。实现会随机挑一个。统一：第 82 行现在是权威 wikilink schema，第 414 行注明是迁移前后对比示例。删了误导性的 `weight: -2` 例子（负权重在 lifecycle / decay 里没定义）。
    - **HIGH · `migrate-to-wikilinks.md` 缺词边界要求** —— 朴素名字替换会把 "Algorithm" 弄坏成 `[[person-al]]gorithm` 如果存在叫 "Al" 的人。加显式 `\bword\b` 边界规则 + wikilinks-inside-wikilinks 守卫 + slug 冲突处理（按 concept-spec § 4.2）+ 跨平台 Windows PowerShell 备份命令 + 显式执行顺序说明（Phase 5 备份必须在 Phase 2 写入之前，尽管编号相反）。
    - **HIGH · review-queue 缺 id 零填充规则 + 并发模型 + 归档排序** —— `r{TODAY}-{NNN}` 模糊（是 001 还是 1？）。文档化：永远 3 位零填充以便字典序可排序。加 lock-free 乐观并发协议（append 前重读 + 冲突重试）。加显式归档排序规则（按 `closed_at` 升序，从 `closed_at` 解析月份）。
    - **HIGH · review-queue + comparison status 没回退守卫** —— `dismissed → open` 文档说无效但无强制。明确文档化为 MONOTONE / 单向 DAG。`closed_at` / `closed_by` 现在声明为 status != open 时 REQUIRED 非空。Comparison 的 `decision` 必须等于 `options[*]` 中之一 OR "deferred" OR "none"。`confidence` 必须在 [0.0, 1.0]。`revisited` 数组限制最多 50 项（溢出转入正文 `## Audit trail`）。给 people-spec 的 enum 加 `relationship: organization`（路由规则中引用了但 enum 缺）。
    - **HIGH · people-spec privacy_tier 没有机器验证器** —— `high` 层只是文字声明的强制。加 Privacy Validator 段：post-write lint 扫正文中 10+ 位数字、街道地址正则、邮箱、canonical 之外的全名 → CLASS_C 违规 + P0 review-queue 项。加 operational tier 表（low/medium/high）说明每层允许什么。加 monotonicity 不变量：`last_mentioned >= first_mentioned`、`mention_count` append-only。
    - **MEDIUM · pre-prompt-guard.sh 中文匹配依赖 locale** —— POSIX/C locale 下运行可能误判 上朝/退朝/监控模式/处理 queue 等多字节 UTF-8 关键词。脚本前面加 `export LC_ALL=C.UTF-8 LANG=C.UTF-8`（en_US.UTF-8 fallback），grep 之前。
    - **LOW · concept-spec 中过期的 `tools/migrate.py` 引用** —— 该文件已在 R-1.8.0-011 pivot 中删除，但 spec 中还引用了 3 次（148、319、351 行）。改为指向替代品 `scripts/prompts/migrate-from-v1.6.md`。
    - **LOW · 互斥注释误导** —— 写的是 "ROUTER 会收到两个相互竞争的 system-reminder 块"，但实际伤害是它们会拼接成一个 banner 错配的合并块。重写注释说明真实伤害。
    - **LOW · MIGRATE_WIKILINKS_EOF heredoc 阶段编号不按执行顺序**（0,1,5,2,3,4,6）—— LLM 顺序跟读会困惑。重写为按执行顺序的 1-10 编号 + 显式说明源 prompt 的阶段编号为何不同。

- **R-1.8.0-013 用户只读 repo 审查（同次提交）**：用户独立审查了所有 67 个 tracked `.py/.sh/.yml` 文件（范围比 R-1.8.0-013 更广），发现 9 个可执行项。全部接受并修复（"全部干完，不要再留任何 bug 了"）：
  - **CRITICAL · `scripts/hooks/pre-bash-approval.sh` fail-OPEN**：3 处 fail-open 让危险命令在 approval bridge 崩溃时静默放行（ImportError、JSON 解析失败、空输出）。3 个路径全部改成 fail-CLOSED —— bridge 错误现在阻止命令并通过 stderr 输出诊断信息（rc=$BRIDGE_RC + 捕获的 stderr + LIFEOS_YOLO_MODE=1 旁路指引）。"未安装"情况仍然放行（不能强制不存在的 guard），但所有其他路径默认拒绝。
  - **CRITICAL · `tools/research.py` SSRF**：研究工具抓取搜索结果中任意 `http(s)` URL，没有私网拒绝列表 —— 可能被精心构造的搜索结果用作内网探测器。加 `_is_private_ip()` 覆盖 IPv4 RFC1918 / loopback / link-local / 云元数据 + IPv6 ::1 / fc00::/7 / fe80::/10 + 字面 hostname 拒绝列表（`localhost`、`metadata.google.internal`、`metadata.azure.com`、AWS 169.254.169.254 等）。加 `_is_safe_url()` 拒绝非 http(s) 协议并跑 IP 检查。在任何网络 I/O 前 wired 到 `_fetch_text` 拦截。被阻止 URL 输出 stderr 让 operator 看到拒绝。同时加 `_MAX_RESPONSE_BYTES = 5 MB` 截断限制内存。
  - **CRITICAL · `tools/sync_notion.py` BaseException 捕获**：每页同步循环捕获 `BaseException`，吞掉 `KeyboardInterrupt` / `SystemExit` 把 Ctrl-C 记录成"page failed"。改成 `(KeyboardInterrupt, SystemExit): raise` 优先，然后 `Exception` 处理实际同步失败。解释器信号现在正确传播。
  - **CRITICAL · `tools/approval.py` Tirith 静默缺失**：optional `tools.tirith_security` 模块的 ImportError 被静默吞掉但 `setup-hooks.sh` 描述声称 "tirith enabled"。加一次性 stderr warning 当 Tirith 不可用 + 模块级 `_TIRITH_UNAVAILABLE_WARNED` flag（每进程 warn 一次，不是每命令）。更新 `setup-hooks.sh` 描述为 "optional tirith if installed" 让说明匹配实际。
  - **CRITICAL · `tools/seed_concepts.py` fresh clone 上崩**：依赖在 R-1.8.0-011 cortex-helper 清理中删除的 `tools.lib.cortex.{concept,extraction}` 模块，所以 `import tools.seed_concepts` 在每个 fresh clone 上都失败（用 `python -c` 实测验证）。功能已被 LLM 驱动的 `scripts/prompts/extract-concepts.md` 和 `scripts/prompts/rebuild-concept-index.md` 替代。删除死模块 + 测试（`tests/test_seed_concepts.py`）。
  - **HIGH · `.github/workflows/test.yml` ruff `continue-on-error: true`**：lint 回归静默通过。移除 `continue-on-error`。需要先清理现有 baseline —— 修了 16 个 lint 错误（12 个自动 + 4 个手动：`B023` `approval.py:455` `get_input` 线程函数 closure 绑定 bug、`SIM105` try/except/pass → `contextlib.suppress`、`PTH105/108` `os.replace/unlink` → `Path.replace/unlink`、`SIM102` `skill_manager.py:272` 嵌套 if 合并）。Ruff baseline 现在干净。
  - **HIGH · `.github/workflows/test.yml` bash 语法检查漏 `scripts/lib/*.sh`**：硬编码 glob 只列了 `scripts/*.sh scripts/hooks/*.sh evals/run-eval.sh tests/hooks/test_*.sh`。改成 `git ls-files '*.sh'` 让任何目录下的新 shell 文件自动覆盖。验证当前 18 个 tracked `.sh` 全部通过 `bash -n`。
  - **HIGH · `scripts/hooks/pre-write-scan.sh` JSON 正则解析**：jq 缺失时用 `grep/sed` 正则解析 JSON 在转义引号 / 多行内容 / 嵌套字段上失败 → 未扫描的写入静默放行。加 Python JSON parser 作为中间层 fallback（Python 在 Claude Code 运行的任何地方都有；用 `\x1f` unit separator 安全分隔 file_path 和 content）。最后一道正则路径现在对敏感路径（`/_meta/`、`/SOUL.md`、`/wiki/`、`/.env`、`/secrets`）FAIL-CLOSED —— 阻止 + 告诉用户安装 jq 或 python。
  - **MEDIUM · `tools/search.py` 吞掉 config 异常**：bare `except Exception` 同时隐藏配置损坏 AND ImportError / AttributeError（config loader 真实 bug）。收紧到 `(FileNotFoundError, OSError, ValueError, KeyError)` + stderr warning 让损坏 config 可见，同时保留 recency_boost_days=90 默认 fallback。
  - **MEDIUM · `tools/export.py` pandoc 无 timeout**：在格式错误的输入或文件系统卡住时无限等。加 `timeout=60` 到 `subprocess.run` + 新 `subprocess.TimeoutExpired` handler 报告输入文件大小和补救建议到 stderr。

净：11 文件修改，2 文件删除（seed_concepts.py + test）。所有之前的 hook 测试仍然通过。3 个之前就存在的 `test_stop_session_verify.sh` 失败未变（最近一次改在 v1.7.3，与本次审查无关）。

- **R-1.8.0-013 用户第三轮审查（同次提交）**：用户在 HEAD `d7639fc` 上做了第三轮独立审查，发现 7 个之前 1/2 轮没抓到的问题。全部确认并修复。第三轮的强项是攻击第二轮安全/解析修复的**边界**：
  - **CRITICAL · `tools/lib/second_brain.py:60` CRLF frontmatter 被忽略**：parser 用字面 `content.startswith("---\n")` 拒绝 Windows CRLF 行尾的文件 —— 它们被当成"无 frontmatter"，body=完整文件。已实测验证。改成正则 `^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n` 接受 LF/CRLF/混合 + 围栏后的尾部空白。在 `tests/test_second_brain.py` 加 4 个回归测试（CRLF parsed、CRLF no-frontmatter、混合行尾、围栏尾空白）—— 25 个 frontmatter 测试全过。
  - **CRITICAL · `tools/research.py:381` SSRF guard 不解析 DNS**：之前的修复只检查字面 IP 和 hostname denylist，所以 `internal.corp.example` 指向 `10.0.0.1` 会通过。加 `socket.getaddrinfo()` 解析 + 对每条 A/AAAA 记录做 IP 检查。DNS 失败（NXDOMAIN/timeout）当作**不安全**处理（fail-CLOSED 加 stderr 提示）。测试用合成 hostname 通过 `LIFEOS_RESEARCH_SKIP_DNS_SSRF=1` 环境变量旁路（生产代码永不设置）。
  - **CRITICAL · `tools/research.py:354` 重定向链旁路**：`httpx.Client(follow_redirects=True)` 意味着只有原始 URL 跑 SSRF 检查；公网 URL 302→ 内网 IP 完全旁路。改成 `follow_redirects=False`，在 `_fetch_text` 里手动遍历 Location 头（最多 5 跳），每跳重跑 `_is_safe_url()`。相对重定向通过 `urljoin` 解析。
  - **CRITICAL · `tools/research.py:452` resp.text 把整个 body 加载到内存**：之前的 max_bytes 截断发生在 httpx 把整个响应加载到内存**之后** —— 对内存保护毫无用处。重写 `_fetch_text` 用 `client.stream()` + 字节计数器在 stream 中途到 `max_bytes` 就停。测试用的 FakeClient 没有 `.stream()`，落到非流式分支（仍由 post-load 截断兜底）—— 安全因为 mock 返回小的合成 body。
  - **CRITICAL · `scripts/hooks/pre-bash-approval.sh:75` missing-source fail-OPEN**：`tools/approval.py` 在任何候选路径都找不到时，hook exit 0（=放行）。我第二轮的修复辩称这是"不能强制不存在的 guard"；审计正确反驳 —— **缺失安全源就是 critical 状态**。改成 fail-CLOSED 加完整诊断（搜索过哪些路径、通过 `setup-hooks.sh` 怎么补救、`LIFEOS_YOLO_MODE=1` 紧急通道）。新增 `tests/hooks/test_pre_bash_approval.sh` 6 个测试用例（safe / hardline / empty / malformed JSON / missing source fail-CLOSED / YOLO bypass）—— 9 个断言全过。
  - **WARNING · `tools/search.py:302` 异常不够语义化**：之前的修复收紧到 `(FileNotFoundError, OSError, ValueError, KeyError)`，但项目有自己的 `ConfigError` 类作为"config 损坏"的标准信号。改成 `except (ConfigError, FileNotFoundError)` —— config loader 的真实 bug（ImportError、AttributeError）现在传播让用户能看到。
  - **WARNING · `tools/lib/notion.py:215` rich_text > 2000 字符静默失败**：`_body_to_children` 把整个 body 包进一个 rich_text 对象，但 Notion API 对每个对象的 content 拒绝 > 2000 字符。长 body 同步静默失败。加段落边界分块到 1900 字符（段落本身超过就硬切），每块发一个 paragraph block。空 body 仍然发一个空 paragraph（匹配老行为）。新常量 `_NOTION_RICH_TEXT_MAX = 1900`。

验证：
- 18 个 tracked .sh 全部 `bash -n` 通过
- Ruff baseline: All checks passed
- `pytest tests/test_research.py`（28 测试）+ `test_second_brain.py`（25 测试）+ `test_sync_notion.py`（14 测试）= 67 通过
- Hook 测试套件：6/7 通过（唯一失败 `test_stop_session_verify` 是 v1.7.3 起就存在的 pre-existing 失败，未变）
- 新 `tests/hooks/test_pre_bash_approval.sh`: 9/9 断言通过

架构层面备注（推迟 —— 审计中提及但不在本轮范围）：
- `tools/approval.py:713` 224 行 god function 拆 5 层
- 2 个 hook 重复的 session discovery → `_lib.sh` 帮助函数
- `tools/lib/config.py:137` 119 行 load_config 拆分
- `evals/run-tool-eval.sh:223` frontmatter `eval`（用 repo-trust scope 缓解，未移除）
- research/notion 的 `Any` types → `Protocol` 定义
- `ApprovalDecision` TypedDict
- `tools/search.py:212` SQLite/FTS sessions index
- `tools/export.py:210` streaming generator
- `--notion-token-stdin` UX 改进
- Hook JSON parser 去重
- `setup-hooks.sh:310` SKILL.md install meta 分离

这些都是真实的改进，但每个都是多小时的重构；按"先修安全/正确性，再修复杂度债务"明确推迟。

- **R-1.8.0-013 用户第 4 轮再审计（同次提交）**：审计确认第三轮修复落地正确，但又发现 7 个新问题打破"CI 绿/零遗留"声明。全部确认并修复。第四轮的强项是检查**基础设施层**（CI gate、包安装、全量 pytest 收集）：
  - **CRITICAL · `tests/test_integration.py:26` fresh clone import 失败**：依赖 R-1.8.0-011 删掉的 `tools.lib.cortex`，所以全量 `pytest --collect-only` 在第三轮的目标测试运行前就 ERROR 了。功能已被 LLM prompt 替代。删掉死测试文件。
  - **CRITICAL · `pyproject.toml:58` 损坏的 `life-os-tool` console script**：指向不存在的 `tools.cli:main`（R-1.8.0-011 删掉）。fresh clone 上 `pip install` 会因为 entry-point 验证失败。移除 `[project.scripts]` 段。
  - **CRITICAL · `LIFEOS_RESEARCH_SKIP_DNS_SSRF` env var 旁路**：第三轮加这个给测试，但用户 shell 可在生产环境 set 这个 var 来禁用 SSRF DNS 检查。改用 `PYTEST_CURRENT_TEST` 检测 —— 只有 pytest 自己能 set 这个变量。测试 fixture 删除 `monkeypatch.setenv` 行。
  - **HIGH · mypy --strict 25 个错误阻塞 CI gate**：`tools/approval.py` 有裸 `dict` 返回和没类型的参数；`notion_client / markdown_it / genanki / httpx / markdownify / tools.tirith_security` 没 stub 导致 6 个 import-not-found。给这 6 个模块加 `[[tool.mypy.overrides]]`。给 `approval.py` 加类型注解：7 个函数 `dict` → `dict[str, Any]`，callback 参数 `Callable[..., str] | None`，收紧 `tirith_result["findings"]` 类型。修 `prompt_dangerous_approval` 线程函数的 B023 closure 绑定 bug。删除 `skill_manager.py:34` + `export.py:433` 没用的 `# type: ignore` 注释。修 `socket.getaddrinfo` `sockaddr[0]: str | int` 收窄。`Callable` 从 `collections.abc` 导入（现代风格，ruff UP035）。结果：**0 个 mypy 错误**（之前 25 个）。
  - **HIGH · `test_compliance_check.py` 5 个失败**：fixture 用 R-1.8.0-013 之前的极简 briefing 结构，但 checker 现在要求 6 个 H2 段 + 版本标记 + Cortex 状态。建立可复用 `_FULL_START_BRIEFING_BASE` 常量。重写 4 个 `TestStartSession` fixture。发现 3 个 fabricate/preflight 测试调用了 `start-session-compliance` scenario 但它已不打包那些检查；改成调用专门的 `preflight-check` / `fabricate-path-check` scenario。修 `test_clean_adjourn_passes` fixture 加 `## Phase 1` … `## Phase 4` H2 + `## Completion Checklist`。修 escape-phrase 用英文 `"lightweight briefing path"`（实际 denylist 条目；中文版从来不在 denylist 里）。11 个 compliance 测试全过。
  - **HIGH · `test_stop_session_verify.sh` 3 个失败**：2 个独立 bug：
    1. `stop-session-verify.sh` `ARCHIVER_TAIL` awk 在每次匹配都 `start = NR`（覆盖），所以 transcript 有 4 个 phase 行都匹配 `archiver` 时，只有最后一行存活 → 误报 Phase 1/2/3 缺失 → T2 在 transcript 实际完整时误报违规。修成 `start == 0 { start = NR }`（锁定第一次匹配）。
    2. T2 的伪 lockfile（5 分钟冷却，按 transcript 第一行 sha 算）阻止 T3/T4（同样的第一行 `User: 退朝`）运行。每个测试用例前加 `rm -f $HOME/.cache/lifeos/stop-hook-*` 清理。结果：**11/11 hook 测试用例全过**（之前 8/11）。
  - **MEDIUM · 4 个 `test_export.py` 失败因为缺 optional extras**：之前被 mypy 标记为 unused 的 `# type: ignore[import-untyped]` 注释掩盖了。给 `TestExportHtml` 加 `@pytest.mark.skipif(not find_spec("markdown_it"))`，给 `TestExportAnki` 加 `find_spec("genanki")`。默认 install：测试干净跳过。`uv sync --extra export` 时：正常运行。

- **R-1.8.0-015 · Subagent 数量漂移清理 + tag 对齐（2026-04-30 用户第九轮审计后）**：用户第九轮审计在 R-1.8.0-014 STRICT 通过后又抓到两个残留：(a) subagent 数量漂移——根 `AGENTS.md` 已是 23，但 `pro/AGENTS.md`、`pro/GEMINI.md`、`docs/index.md`、`docs/installation.md`、`SKILL.md`、三语 README 以及约 14 个用户向文档仍说 16；(b) `v1.8.0` git tag 仍指向 `02aea0d`（R-1.8.0-013 commit）而不是最新的 Spec-GC HEAD `6cb3d79`。语义计数漂移正是 R-1.8.0-014 扫描器抓不到的那种问题——STRICT 只验已删除路径 / 禁用 token，不验用户可见的语义数字。
  - **批量数量更新（16 → 23）**：跨所有 active（非 legacy 非 CHANGELOG）文档机械替换。涉及文件：`SKILL.md`、`pro/AGENTS.md`、`pro/GEMINI.md`、`README.md`（EN）、`i18n/zh/README.md`、`i18n/ja/README.md`、`docs/index.md`、`docs/installation.md`、`i18n/zh/docs/installation.md`、`docs/getting-started/{first-session,choose-your-platform,what-is-life-os}.md`、`i18n/zh/docs/getting-started/what-is-life-os.md`、`i18n/ja/docs/getting-started/what-is-life-os.md`、`docs/architecture/{system-overview,roadmap}.md`、`docs/evals/{overview,writing-new-scenarios}.md`、`docs/guides/multi-platform-setup.md`、`docs/user-guide/second-brain/{second-brain-overview,obsidian-integration}.md`、`docs/reference/version-history.md`。覆盖模式：`16 subagents`、`16 个 subagent`、`16 个 agent`、`16 个独立 agent`、`All 16 subagents`、`16 independent agents`、`16 個の独立した agent`、`16 functional IDs`。`version-history.md` 里 v1.6.0 历史迁移条目改写为 `v1.6.0 当时的 agent 文件重命名（v1.6.0 时为 16 个，至 v1.8.0 增至 23 个）`，让历史引用仍然准确。
  - **`docs/architecture/system-overview.md` subagent 列表更新**：之前 "23 个 subagent" 标题下列的还是 16 个名字。补全为全部 23 个 ID（新增：`hippocampus`、`concept-lookup`、`soul-check`、`gwt-arbitrator`、`narrator`、`knowledge-extractor`、`monitor`）。
  - **扫描器扩展（`scripts/check-spec-drift.sh`）**：`FORBIDDEN_TOKENS` 新增 7 条 subagent 数量漂移 token。tokens 用 bash 相邻字符串拼接（`"16 sub""agents"`）写出，扫描器源码本身不携带字面子串——这样用户端跑 `rg "16 subagents"` 审计仓库时，扫描器自己 0 命中，只剩真正的漂移候选。legacy frontmatter（`status: legacy` 或 `authoritative: false`）豁免依旧生效；v1.7 时代 spec / 档案文件仍历史性提到 "16"，被正确跳过。
  - **`v1.8.0` tag 强制对齐**：删除本地 + 远程 tag，在 HEAD `6cb3d79` 重新打 annotated tag，让拉 `v1.8.0` 的消费者拿到完整的 Spec-GC + subagent 数量清理（R-1.8.0-014 + R-1.8.0-015），不再是旧的 R-1.8.0-013 snapshot。（`git tag -d v1.8.0 && git push origin :refs/tags/v1.8.0 && git tag -a v1.8.0 <head> && git push origin v1.8.0`。）
  - **验证**：`STRICT=1 bash scripts/check-spec-drift.sh` 退出 0；`git ls-files | xargs grep -l "16 subagents|16 个 subagent|16 个 agent|All 16 subagents"` 过滤非 legacy 非 CHANGELOG 文件：**active 0 命中**；mypy --strict tools/ → 0 错误 / 16 文件；ruff → 干净；pytest → 232 通过 / 3 deselected；31 个 tracked .sh `bash -n` 全过。

- **R-1.8.0-014 · Spec GC 冲刺收尾（2026-04-30 用户第八轮审计后）**：完成跨第 5–8 轮审计积累的 spec drift 清理。STRICT 模式 CI 闸门（`STRICT=1 bash scripts/check-spec-drift.sh`）现在通过——active 文件不再引用任何已删除脚本/CLI/subagent/cron 架构。v1.7 时代的 legacy spec 已用 YAML frontmatter（`status: legacy` 和/或 `authoritative: false`）显式标注。
  - **扫描器升级（`scripts/check-spec-drift.sh`）**：
    - **计数器子 shell bug 修复**：`broken_paths` 自增因为 `... | sort -u | while ...` 跑在子 shell 而丢失。改为先把唯一路径写到临时文件再在父 shell 里循环，STRICT 退出码恢复正确。
    - **legacy frontmatter 豁免范围扩大**：现在 `status: legacy` *或* `authoritative: false` 都豁免。这两个标记历史上在 v1.7 references 里混用，现在两者都认。
    - **多行上下文 lookback 5 → 8 行**：覆盖常见 markdown 模式——`### Removed in v1.8.0 pivot` 这种 H2/H3 标题 + 空行 + 4–6 个删除条目。原来 5 行窗口会让最后一个条目脱离标题上下文。
    - **CONTEXT_ALLOW 关键字扩充**：增加大写 `Removed`/`Deleted`/`Deprecated`、`in v1.8.0 pivot`、`in pivot`、`R-1.8.0-012`、`R-1.8.0-013`、`TBD`、`planned`、`will be created`，让"已删除"类注释真的命中。
    - **forbidden-token 单词边界检测**：从字面 `index($0, token)` 改成字符类构造的单词边界正则（awk 没有 `\b`），子串 `life-os-tool` 不再误命中合法的 `pyproject.toml` 包名 `life-os-tools`（复数）。
  - **Active 文件改写**（已删除脚本引用全部加上"v1.8.0 pivot 删除"的明示注释，或迁移到 pull-based 等价物）：
    - `docs/getting-started/what-is-life-os.md` Layer 4 段落（× EN/ZH/JA）：把 cron 时代的 `scripts/{decay-audit,dream-trigger-check,monthly-review,session-index,wiki-conflict-check}.py` 列表换成 R-1.8.0-011 后实际发布的 `python -m tools.<name>` 模块。
    - `tools/README.md`：重写 Status + Authoritative Spec 段落，把"Planned Modules"表格换成"Currently Shipped Modules"，列出实际存在的 10 个工具，已删除的 dispatcher / cron 脚本 / cortex helper 标为历史背景。
    - `pro/agents/monitor.md` Related Specs：`references/automation-spec.md` 和 `references/session-modes-spec.md` 标为 v1.8.0 pivot 删除（被 `pro/CLAUDE.md` Session Modes 替代）。
    - `evals/scenarios/tool-seed.md`：`references/SOUL-template.md` 与 `references/tools-spec.md §6.10` 标为 legacy/已删除；`tools/seed.py` 现在内联生成 skeleton。
    - `docs/user-guide/themes/adding-a-theme.md`：删除对不存在的 `themes/zh-classical-tw.md` 的引用，改为描述繁体中文需用户自行创建。
  - **legacy frontmatter 批处理（第 8 轮累计 · 71 文件分两批标注）**：`docs/architecture/`、`docs/guides/v1.7-migration.md`、`docs/user-guide/cortex/*`（× EN/ZH/JA）、`references/{cortex-spec, cortex-architecture, narrator-spec, tools-spec, v1.7-shipping-report, templates/concept-template, concept-spec, data-layer, eval-history-spec, hippocampus-spec, method-library-spec, session-index-spec, snapshot-spec, compliance-spec}.md`（× EN/ZH/JA）、`evals/scenarios/*` 全部带 `status: legacy`（或 `authoritative: false`），扫描器把它们识别为历史档案而非 active spec。
  - **验证**：`STRICT=1 bash scripts/check-spec-drift.sh` 退出 0（active 文件 broken paths：0；active 文件 forbidden-token hits：0）。`mypy --strict tools/` 0 错误 / 16 文件。`ruff check tools/ tests/` 干净。`pytest tests/` 232 通过 / 3 deselected。

验证（CI 矩阵现在真的绿）：
- 30 个 tracked .sh 全部 `bash -n` 通过
- `mypy --strict tools/`: **0 个错误**（16 个源文件检查）—— 之前 25 个
- `ruff check tools/ tests/`: All checks passed
- `pytest tests/` 全套: **223 通过，9 跳过（optional extras），3 deselected** —— 之前 5+ 失败
- Hook 测试套件: **7/7 通过** —— 之前 6/7
- pytest 收集: 232/235（3 deselected；之前 232/235 + 1 个 test_integration 收集 ERROR）

### 迁移

```bash
# 从你的 second-brain repo 内部跑（含 _meta/、SOUL.md、wiki/ 的那个目录）：
cd /path/to/your/second-brain
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
bash ~/.claude/skills/life_OS/scripts/setup-cron.sh install
# 如果不能 cd，可用：LIFEOS_DATA_ROOT=/path/to/second-brain bash ... install
```

无第二大脑数据迁移需求。v1.7.x 数据完全兼容。`$PWD`（或 `$LIFEOS_DATA_ROOT`）若没有 `_meta/` 目录，install 会清晰报错退出，错误配置会响亮失败而不是静默扫错根目录。`bootstrap_repo_dirs` 幂等 — 已有目录的 repo 重跑安全。macOS 重新安装后：`launchctl unload ~/Library/LaunchAgents/com.lifeos.hermes-local.*.plist && launchctl load ~/Library/LaunchAgents/com.lifeos.hermes-local.*.plist` 让新的 `WorkingDirectory` 与 `--root` 路径生效。

### Audit 结论（v1.8.0 final）

v1.7.3 audit 发现的「spec 承诺但从未自动化」缺口现已 close。AUDITOR Mode 2 / ADVISOR monthly / eval-history monthly / strategic consistency / wiki decay / spec compliance / archiver recovery / boot catch-up 全部 ✅。

用户反馈：「Hermes 和 cortex 的问题」→「为什么设计好了但没跑起来」→「不要 routines 也能实现」→「我不可能每天都开新 session」→「完整版必须一次性全部做完」。

---

## [1.7.3] - 2026-04-26 / 2026-04-27 - Cortex 强制启动 + 自动触发 + archiver Phase 2 拆分 + 4 个死代码模块删除

> "让工具真能用起来" release window。三轮迭代全部 squash 进单一 v1.7.3 release：
>
> 1. **v1.7.3 base (2026-04-26)**：Cortex always-on hook、4 slash commands、approval guard wired、4 dead modules removed。
> 2. **v1.7.3 自动触发补丁 (2026-04-27)**：用户反馈后 slash commands 降级为 backup 模式。pre-prompt-guard.sh 加 memory 关键词检测。
> 3. **v1.7.3 archiver 拆分 (2026-04-27)**：Phase 2 拆出独立 `knowledge-extractor` subagent，修复 80%+ 最近 archiver placeholder 违规。spec 一致性修复 + stop-session-verify LLM_FILL 检测。
>
> 三轮全部合并为单一 v1.7.3 release，按用户要求：「版本号不能变，还是 1.7.3，都要在这个版本里面全部修完」。

### 新增

- **Cortex always-on 强制启动 (hook 注入)**：`scripts/hooks/pre-prompt-guard.sh` 现在输出 `<system-reminder>` 块（trigger=cortex），在 prompt 长度 ≥ 80 字符或含决策关键词时强制 ROUTER 在回答前并行 launch 5 个 Cortex subagent（hippocampus / concept-lookup / soul-check / gwt-arbitrator / narrator-validator）。修复 v1.7.2 audit 发现的静默降级问题。短对话填充（"好"、"继续"）会跳过 Cortex。
- **4 个 slash command 接入 Claude Code**：新增 `scripts/commands/{compress,search,memory,method}.md` 源文件；`scripts/setup-hooks.sh` 安装时复制到 `~/.claude/commands/`。命令：
  - `/compress [focus]` — inline 上下文压缩，归档到 `_meta/compression/<sid>-compress-<ts>.md`。
  - `/search <query>` — 基于 `tools.session_search` CLI 的 FTS5 跨 session 搜索。
  - `/memory emit|read|remove|path` — 基于 `tools.memory` CLI 的 24-48h 短期记忆。
  - `/method create|update|list` — 基于 `tools.skill_manager` CLI 的方法论库管理。
- **Approval guard 接入 (PreToolUse Bash hook)**：新增 `scripts/hooks/pre-bash-approval.sh`，把每次 Bash 命令桥接到 `tools/approval.py`。修复 v1.7.2 缺口：47 个危险命令 pattern + hardline + tirith guards 之前 0 调用。Hook 读 stdin JSON，跑 `check_dangerous_command()`，exit 0（静默放行）或 exit 2 + stderr（拦截并显示原因）。绕开方式：`export LIFEOS_YOLO_MODE=1`。注册为 `life-os-pre-bash-approval`（PreToolUse · matcher Bash · timeout 5s）。
- **Memory 自动 emit 检测（自动触发补丁 · 2026-04-27）**：`pre-prompt-guard.sh` 也检测中/英/日 memory 关键词（记一下 / remind me / 覚えて / TODO 等），注入 `<system-reminder>`（trigger=memory）强制 ROUTER 自动跑 `python -m tools.memory emit`，而不是把用户引导到 `/memory`。新增 `trigger=memory` 值到 hook activity log。
- **pro/CLAUDE.md → Auto-Trigger Rules section（自动触发补丁 · 2026-04-27）**：明文定义 memory 自动 emit、compress 自动建议、search 自动触发（通过 Cortex hippocampus）、method 自动 create（通过 archiver Phase 2 → knowledge-extractor）。原则："如果 ROUTER 让用户切换到 slash command，那是 UX bug——直接做动作"。
- **knowledge-extractor subagent (Phase 2 拆分 · 2026-04-27)**：新增 `pro/agents/knowledge-extractor.md`（Opus tier，[Read, Grep, Glob, Bash, Write] tools）。执行 7 个 Phase 2 sub-step（wiki 六准则审查 / SOUL 维度变化 / methods / concepts + Hebbian / SessionSummary / snapshot / strategic-map）并写 7 个持久文件。同时写 7 个 extraction reports 到 `_meta/runtime/<sid>/extraction/*.md` 供 archiver 读回。R11 audit trail 写到 `_meta/runtime/<sid>/knowledge-extractor.json`。原因：之前 monolithic archiver 有 80%+ placeholder 违规（最近 10+ 次 adjourn 在 `pro/compliance/violations.md` 2026-04-25 至 2026-04-27），因为它一次要做太多事。ROUTER 必须在 launch archiver 之前先 launch knowledge-extractor。

### 变更

- **narrator-validator audit trail HARD RULE**：`pro/agents/narrator-validator.md` frontmatter `tools` 从 `[Read]` 扩展到 `[Read, Bash, Write]`；新增 "Audit Trail (R11, HARD RULE)" section，要求返回 YAML 前必须写 `_meta/runtime/<sid>/narrator-validator.json`。
- **版本标记**：`SKILL.md` frontmatter 和 3 份 README badge 更新到 `1.7.3`。
- **spec 文档更新为 inline 压缩**：`SKILL.md` Trigger Execution Templates `/compress` section、`references/hard-rules-index.md` manual compression bullet、`evals/scenarios/cortex-retrieval.md` CX11 positive case 全部重写为说 ROUTER inline 压缩，替代已删的 `tools/context_compressor.py`。
- **4 个 slash command 文件降级为 backup mode（自动触发补丁 · 2026-04-27）**：每个 `scripts/commands/{compress,search,memory,method}.md` 开头加 "⚠️ Backup mode" header，指向对应的 pro/CLAUDE.md Auto-Trigger Rules 子段。Slash command 保留功能，用于：(1) 用户精确控制，(2) 开发者冒烟测试，(3) 自动触发 fallback。
- **archiver.md Phase 2 拆分 + spec 一致性修复（拆分 · 2026-04-27）**：`pro/agents/archiver.md` line 77 修正（之前 "12-section Adjourn Report Completeness Contract" 是 v1.7.2 旧措辞，现在改为 v1.7.2.3 的 "6-H2"）。Phase 2 spec 完整重写：主路径委托给 `knowledge-extractor` subagent；legacy 7-sub-step inline spec 保留作 fallback。`pro/CLAUDE.md` Step 10 更新：ROUTER 必须先 launch `knowledge-extractor`，再 launch `archiver`。新 launch 顺序模板。
- **stop-session-verify hook LLM_FILL 检测（拆分 · 2026-04-27）**：`scripts/hooks/stop-session-verify.sh check_phase()` 增强。之前只检测 phase header 行的 TBD / `{...}` / "placeholder"。现在也扫描每个 phase header 之后 30 行内的未填 `<!-- LLM_FILL: ... -->` pattern 和 `LLM_FILL:` 字符串，标记为 `placeholder_phases`。捕获最近 archiver 违规的真实根因（LLM 把 Bash skeleton 原样输出而没填占位符）。

### 删除（4 个死代码模块 · 1830 行）

- **`tools/prompt_cache.py` 删除**（118 行 0 调用）：Claude Code 包月场景下无意义。
- **`tools/mcp_server.py` 删除**（227 行 0 调用 0 client 连接）：MCP stdio wrapper fork 进来但从未接入 client。
- **`tools/context_compressor.py` 删除**（1370 行 0 调用）：压缩改由 ROUTER inline 执行。
- **`tools/manual_compression_feedback.py` 删除**（51 行 0 调用）：已删 compressor 的输出 helper。
- **`docs/architecture/prompt-cache-strategy.md` 删除**：已删 prompt_cache 的 spec doc。
- **`docs/architecture/mcp-server.md` 删除**：已删 mcp_server 的 spec doc。
- **`docs/architecture/hermes-local.md` 清理**：从 `related:` frontmatter 移除已删模块引用；重写 Borrow/Fork Surface 模块列表反映 v1.7.3 实际状态（approval 已 wired，memory + session_search + skill_manager 保留）；移除 `context_compressor` naming-note 段。

### 迁移

重跑 `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh` 完成：
1. 安装 4 个新 slash command 到 `~/.claude/commands/`
2. 注册新的 `life-os-pre-bash-approval` PreToolUse(Bash) hook
3. 更新 `pre-prompt-guard.sh`（新增 Cortex always-on + memory 关键词检测）
4. 更新 `stop-session-verify.sh`（新增 LLM_FILL 检测 + 30 行 section body 扫描）

安装后，Claude 每次跑 Bash 命令都会被 47 个危险 pattern 筛查；如被拦截，stderr 中会出现 🛡️ 守门人 提示。

无第二大脑迁移需求。

### Audit 结论（v1.7.3 final 后）

v1.7.2 所有 dead-weight 发现 + v1.7.3 archiver 违规根因都已 close：
- Cortex always-on：强制启用（hook 注入）✅
- approval.py 47 patterns：已 wired（PreToolUse Bash hook）✅
- 4 个死代码模块删除（1830 行）✅
- Slash command 接入并降级为 backup mode（自动触发为主）✅
- Memory 自动 emit：hook 检测关键词强制 ROUTER 自动 emit ✅
- archiver Phase 2 拆出 knowledge-extractor subagent ✅
- archiver.md spec 内部一致性恢复（12-section vs 6-H2 修复）✅
- stop-session-verify LLM_FILL 检测加上 ✅

驱动这次 release window 的用户反馈：
1. "我为什么要用这样的方式来启动这些命令？这些命令不可以直接自动启动吗？" → 自动触发补丁
2. "重新检查一下上朝流程和退朝流程" → 揭示 80%+ archiver placeholder 违规 → 拆分
3. "C 还是1.7.3" + "版本号不能变，还是 1.7.3，都要在这个版本里面全部修完" → 全部 squash 到单一 v1.7.3 release

---

## [1.7.2.3] - 2026-04-26 - RETROSPECTIVE 骨架所有权

> Subagent D ownership patch。范围仅限 `pro/agents/retrospective.md`、`SKILL.md`、三份 README 和三份 CHANGELOG。

### 变更

- **收窄 RETROSPECTIVE 职责**：`pro/agents/retrospective.md` 现在说明 ROUTER 通过 Bash skeleton 预渲染 Mode 0 约 80% 内容。
- **单一 LLM 填充槽**：subagent 只填 `<!-- LLM_FILL: today_focus_and_pending_decisions -->`，用约 5-15 行生成 Today's Focus + Pending Decisions；ROUTER 再把该块拼回 skeleton。
- **版本标记**：`SKILL.md` 与 README badges 更新为 `1.7.2.3`。
- **install_sha 字段补齐 SHA 缺口**：`SKILL.md` frontmatter 现在携带 `commit_sha` 和 `install_date` 字段。`setup-hooks.sh` 会在 git clone 部署时自动写入它们。新增的 `scripts/lib/sha-fallback.sh` 提供 3 层解析：`SKILL.md` frontmatter → `.install-meta` JSON → `git rev-parse HEAD` → `unknown`。关闭 install-skill 部署中的 `Local commit SHA: unknown` bug。
- **SOUL/DREAM 显示恢复(回归 v1.6.x 体验)**：`scripts/retrospective-briefing-skeleton.sh` 现在用 Bash 完整 paste `SOUL.md` 全文 + 最新 `_meta/journal/*-dream.md` 全文到 fenced markdown block。LLM 只在上面加 delta 解读(confidence trend / today implications),不能压缩 SOUL/DREAM 结构内容。`pro/agents/retrospective.md` ## 2 / ## 3 spec 改为"Bash paste 全文 + LLM 趋势解读"模型。撤销 v1.7.2.1 过度减法把 SOUL Health 压缩到"仅变化维度" + DREAM 压缩到"1-2 句 digest"的副作用。
- **退朝 12 H2 → 6 H2 + LLM token budget(速度修)**:`pro/agents/archiver.md` Adjourn Report Completeness Contract 从 12 H2 减到 6 核心 H2(Phase 0/1/2/3/4 + Completion Checklist)。AUDITOR Mode 3 / Subagent self-check / 子代理调用清单 / Hook fired / total tokens-cost 折叠为 Completion Checklist 下的 H3 子项。新增"Phase 2/3 LLM Token Budget" HARD RULE:Phase 2 narrative ≤ 1500 tokens(合并 wiki/SOUL/method/concept/strategic/SessionSummary/snapshot/last_activity),Phase 3 narrative ≤ 800 tokens。verbatim DREAM journal 不计入 budget(Bash paste)。速度目标:archiver Adjourn 25 分钟 → 10-12 分钟。
- **archiver-briefing-skeleton.sh 新建(archiver 的 Bash 骨架)**:新 `scripts/archiver-briefing-skeleton.sh` 镜像 `retrospective-briefing-skeleton.sh` 设计 — 输出 6 H2 Adjourn Report 框架,Bash paste Phase 0/1/4 + 实测数据(outbox 路径 / decision-task-journal 计数 / wiki-SOUL-DREAM stat / git status / Stop hook 健康)。LLM 只填 `<!-- LLM_FILL -->` placeholder(Phase 2/3 narrative + Completion Checklist 值)。已 wire 进 `pro/CLAUDE.md` / `pro/GEMINI.md` / `pro/AGENTS.md` Step 10 Adjourn Session 段。与现有 `archiver-phase-prefetch.sh`(R11 audit trail)互补。
- **Session Binding HARD RULE 重写(产品方向修正)**:`pro/CLAUDE.md` / `pro/GEMINI.md` / `pro/AGENTS.md` Session Binding HARD RULE 澄清:**discussion scope ≠ data write scope**。Session binding 约束**数据持久化**(decisions/wiki/SOUL 写哪个项目),不约束**讨论话题**。ROUTER 直接处理用户提出的任何议题(财务 / 战略 / 人际 / 跨项目 / 抽象)。ROUTER 禁止 deflect 措辞 "本窗口角色只做 X" / "请转到其他窗口" / "translate to planner trigger paste for another window" / "召唤翰林院 panel" 除非用户明确要求。撤销 13 轮 hardening 累积的"LLM 把 session binding 误读为业务议题禁区"副作用。恢复 Life OS 决策思考助手的初心。

### 迁移

无需 second-brain 迁移。

---

## [1.7.2.1] - 2026-04-26 - 报告形态与主题审美减法热修复

> 只做减法的小型热修复：减少可见规则，恢复主题审美，并固定版本标记位置。不新增超过 v1.7.2.1 的版本线。

### 变更

- **恢复主题审美**：面向用户的 briefing 回到当前主题的视觉语言，不再被合规脚手架主导。
- **收敛报告表面**：用户可见报告从 17 个 H2 块减少到 6 个，让用户看到必要流程，而不是过量仪式。
- **固定版本标记**：版本标记保持在稳定、可预期的位置，便于人工和脚本检查。

### 移除

- **移除 wrapper 强制要求**：compressed paste wrappers 不再作为用户可见报告结构的必需项。
- **用户路径规则更少**：移除重复的呈现规则，让审计模型继续可执行，同时避免每次响应都显得程序化。

### 产品重心回正（v1.7.2.2 说明）

- **AUDITOR 默认静默**：AUDITOR 转为默认静默的后台验证；只有出现实质性阻塞、需要升级处理，或用户明确要求审计结果时才进入主路径。
- **不再前置 Compliance Watch**：`Compliance Watch` 信号不再插入用户可见 briefing 第一行；相关信号保留在审计 / 后台通道，而不是占据开场。
- **新的 H2 结构**：面向用户的报告采用新的 H2 结构，以 briefing 实质内容、决策、下一步和证据为中心，而不是以合规脚手架为中心。
- **trail `SESSION_ID` 锁定**：runtime audit trail 锁定到当前 `SESSION_ID`，确保 trail 证据绑定当前会话，不漂移到其他会话上下文。
- **second-brain 回到前台**：系统审计明确退回后台，用户的 second-brain 内容、优先级和工作记忆重新成为前台主角。

### 迁移

不需要 second-brain 数据迁移。

---

## [1.7.2] - 2026-04-26 - Hermes Local、Cortex 常开与压缩加固

> 面向本地执行面、Cortex 编排和透明压缩报告的补丁发布。

### 新增

- **Hermes Local 命名与归因**：`Hermes Local` 是 Life OS 本地防护与自动化的用户可见名称；内部 / spec 标签仍保持 `execution layer`、`Layer 3`、`Layer 4`；文档现在明确归因借鉴 / fork 自 `NousResearch/hermes-agent`（MIT License）的本地工具组件。
- **Hermes Local fork 模块域**：记录并归因 6 个借鉴 / fork 的模块域：`tools/approval.py`、`tools/context_compressor.py` + `tools/manual_compression_feedback.py`、`tools/prompt_cache.py`、`tools/memory.py`、`tools/session_search.py`、`tools/skill_manager.py`。Life OS 压缩器模块名使用 `context_compressor`。
- **cron 与 MCP 本地自动化**：新增 `scripts/setup-cron.sh`，用于幂等安装本地 reindex / daily briefing / backup 计划任务；新增 `tools/mcp_server.py` 和 `docs/architecture/mcp-server.md`，为 Life OS CLI 工具提供可选 MCP stdio 入口。
- **Method library 与 eval-history 闭环**：新增 method candidate extraction、method context injection、`_meta/eval-history/` writeback 和 monthly self-review readback，让重复出现的方法信号与合规信号进入闭环。

### 变更

- **Cortex 常开编排**：当 Cortex 启用时，Step 0.5 会尝试覆盖每条用户消息，包括 Start Session 和 direct-handle 候选路径；索引缺失时触发 `tools/migrate.py` auto-bootstrap，并通过 `degradation_summary` 降级，而不是静默跳过。
- **ROUTER 粘贴压缩**：用 compressed paste wrappers + R11 audit-trail links 替代 v1.7.1 的完整子代理输出重复粘贴；ROUTER 使用 `tools/context_compressor.py` 语义，并保留实质性论断、决策、阻塞项、副作用和证据。
- **手动 `/compress` 触发器**：ROUTER 现在将 `/compress [focus]` 视为用户触发的上下文压缩，并按 `tools/manual_compression_feedback.py` 语义返回 message count、粗略 token 估算和 no-op 提示。

### 修复

- **版本检查预取**：retrospective Mode 0 现在消费 ROUTER 预取的 Step 8 marker，把本地 / 远端版本详情复制到 Platform + Version Check，并使用 `lifeos-version-check.sh --force` 执行远端检查，避免 stale cache 或子代理重跑行为掩盖版本漂移。

### 迁移

不需要 second-brain 数据迁移。可选：运行 `bash scripts/setup-cron.sh install` 安装本地计划任务；仅在使用 MCP stdio server 时安装 `mcp`。

---

## [1.7.1] - 2026-04-25 - 版本、i18n 与 hard-rule 索引

> 本补丁把 27 项加固合并为一次发布，重点覆盖透明度、编排证据、hook 可靠性、i18n 漂移控制和合规索引。

### 新增

- **Token 透明度**：briefing 和编排说明现在会展示与 token 相关的执行、跳过和升级原因，不再用泛化摘要遮蔽成本判断。
- **Hard-rule 索引**：`references/hard-rules-index.md` 记录当前权威 HARD RULE 来源和每个 host 的 marker 计数，README 不再写死过期数字。
- **Pre-commit i18n 漂移守卫**：`.git/hooks/pre-commit` 执行 `bash scripts/lifeos-compliance-check.sh i18n-sync`，在本地提交前阻断翻译漂移。
- **v1.7.1 发布说明**：英文、中文和日文 README / CHANGELOG 现在按 Added / Fixed / Migration 对齐覆盖本次加固。

### 修复

- **ROUTER 输出保真**：ROUTER 必须原样粘贴子代理报告，不得压缩或静默摘要，并且继续隔离 triage reasoning，避免泄露给下游代理。
- **AUDITOR 证据路径**：AUDITOR 加固优先使用程序化检查、Bash stdout 证据、来源计数 marker、版本/路径校验和 briefing-completeness 分类，减少同源 LLM 判断。
- **Hook 可靠性**：hook 活动可见性、hook health check、stop-hook 行为和 marker 消歧都已收紧，缺失或歧义 backstop 更容易被发现。
- **Cortex 与 DREAM 展示**：Cortex context emit、显式 GWT 仲裁、frame markdown resolution 和 DREAM full-output display 的契约更清晰。
- **Git 安全与 force push 处理**：force push 场景会升级处理，不再被普通化；发布文档避免暗示不安全恢复动作。
- **i18n 审计清理**：本地化 README / CHANGELOG 已对齐，降低明显混用语言的发布说明泄漏。

**R9 修复(根因):**
- stop-session-verify.sh ADJOURN_RE: 从全文 grep 改为只看末尾 50 行。消除 dev session 讨论 archiver/adjourn spec 内容时的 false-positive (旧版全文 grep 匹配 transcript 任何位置的 "adjourn"/"退朝"/"dismiss" 字面)。不再推迟到 v1.7.2 — v1.7.1 内修复。

**R10 架构转向（真正关闭“5 项 skip”问题）:**
- retrospective Mode 0：18 个步骤中已有 11 个改为由 ROUTER 通过 scripts/retrospective-mode-0.sh 预取（Bash literal stdout，LLM 无法跳过）。步骤 2/3/4/5/8/10/11/12/13/14/17 是确定性的。LLM 只处理步骤 1/6/9/16/18（需要判断）。
- 新违规类别 C-step-skipped（P0）：briefing 中缺失任意一个 11 个 [STEP N · ...] marker。
- 对 LLM 合规上限的结构性回答 — spec 规则无法强制 LLM 行为；程序化 Bash 输出不能被跳过。

**R11 Audit Trail 文件通道:**
- 每个 subagent 现在都会把运行时审计轨迹写入 `_meta/runtime/<session_id>/<subagent>-<step>.json`；AUDITOR 通过 channel 1 程序化读取这些文件，而不是信任 ROUTER 的 LLM 粘贴 channel 2。
- 新增 3 个违规类别：`C-no-audit-trail`、`C-trail-incomplete`、`B-trail-mismatch`。
- 新增辅助脚本与规范：`scripts/lib/audit-trail.sh`、`scripts/archiver-phase-prefetch.sh`、`references/audit-trail-spec.md`；Step 10a Notion sync 现在自动执行，不再询问用户。

**R12 fresh invocation 合同：**
- 每次 `上朝` / `退朝` 触发都必须重新完整执行；LLM 不得复用上一份 briefing 或退朝报告。
- `retrospective-mode-0.sh` 发现已有 `index_rebuild_state` 数据时按 `rebuild=force` 处理，缓存的 index 状态不能成为跳过 Start Session 重建的理由。
- 新增 P0 违规类：`C-fresh-skip`；禁用短语、长度坍缩、缺少 fresh marker 都纳入 fresh-invocation 场景覆盖。
- Runtime audit trail JSON 新增 `fresh_invocation:true` 与 `trigger_count_in_session`。

### 迁移

1. 安装或保留 `.git/hooks/pre-commit`，确保本地提交前运行 `i18n-sync`。
2. 修改发布文档后运行 `bash scripts/lifeos-compliance-check.sh i18n-sync`。
3. 使用 `references/hard-rules-index.md` 查看当前 HARD RULE 计数；不需要迁移 second-brain 数据。

---

## [1.7.0.1] - 2026-04-25 · Briefing Contract + Hook Self-check + Cortex Config

> 本补丁收紧 v1.7 GA 合同：最终 briefing 现在有固定必需区块，Mode 0 会先自检 hook 安装状态，Cortex 统一通过 `_meta/config.md` 显式 opt-in。

### 修复

- **lifeos-version-check.sh cache 鲜度** — 新增 `--force` flag 和基于远端 SHA 的 cache 失效机制。同一天内远端发布新版本不再卡住。
- **Briefing 完整性现在可测试** — Start Session 和 Adjourn 输出必须给出固定标题与具体值；缺失或占位内容会记录为 `C-brief-incomplete`。
- **RETROSPECTIVE 不再假设 hooks 已安装** — Mode 0 先执行 pre-session hook health check；Claude Code hook backstop 缺失或不完整时，显示准确的 `setup-hooks.sh` 修复命令。
- **Cortex config 路径统一** — 撤销 R1 误改的路径分裂 — Cortex 配置仍在 `_meta/config.md`(与 v1.7.0 已发布版本一致),`cortex_enabled: false` 默认 opt-in。
- **Cortex 默认值明确** — config 缺失时降级为 `cortex_enabled: false`；用户显式启用前，Cortex 保持 OFF / opt-in。
- **AUDITOR Mode 3 程序化检查** — AUDITOR 现在调用 Bash（`lifeos-compliance-check.sh` + `grep`），不再依赖 LLM 推理；消除同源虚构，避免 2026-04-25 testbed-machine「private repo」案例再次放行。

### 新增

- **反虚构加固** — Step 8 强制 Bash literal stdout 嵌入,ROUTER 预取 ground truth,AUDITOR Mode 3 扫描虚构短语黑名单 + 工具调用 evidence,新增 B-fabricate-toolcall 违规子类。关闭 2026-04-25 「private repo」虚构案。
- **Briefing Completeness Contract** — RETROSPECTIVE 与 ARCHIVER 的最终报告现在定义固定位置的必需区块与最小 evidence 字段。
- **Briefing 遗漏的 compliance taxonomy** — `C-brief-incomplete` 独立记录缺失标题、session/source metadata 与 escalation 行为，不与基础 Class C 混用。
- **`briefing-completeness` compliance check** — `scripts/lifeos-compliance-check.sh` 现在可在回归中校验 retrospective / archiver briefing 标题。
- **第一层 hook 自动安装** — retrospective Step 0 + archiver Phase 0 + ROUTER 触发词检测发现 hook 缺失时自动跑 `setup-hooks.sh`。`git pull` 后无需手动安装。
- **PRIMARY-SOURCE PRECOMPUTE briefing 标记** — wiki/sessions/concepts 的实测计数现在必须以 `[Wiki count: measured X · index Y · drift Δ=Z]` 格式出现在 briefing 中。缺失 → `C-brief-incomplete`；|Δ|≥3 且没有 `⚠️ DRIFT` → `B-source-drift`。
- **STATUS.md 陈旧检测** — retrospective Step 0.5 检查 STATUS last-updated 与 git HEAD 年龄；≥7 天 → briefing 中抑制 STATUS 叙述。新增 `B-source-stale` 类。
- **30d-≥3 Compliance Watch 自动横幅** — retrospective 读取 `violations.md`，当阈值触发时自动在 briefing 第 1 行前置 `🚨 Compliance Watch: <class> (X/30d)`。缺失 → `C-banner-missing`。
- **ROUTER 对 subagent 输出做事实核查** — `SKILL.md` 要求 ROUTER 在展示给用户前调用 Bash，验证 briefing 中的数字、版本、路径声明。这是 subagent self-check + AUDITOR Mode 3 之后的第三层防线。

### 从 v1.7.0 迁移

1. 检查曾经隐式启用 Cortex 的 second-brain，只在确实需要 Cortex 的工作区通过 `_meta/config.md` 保持启用。
2. 对 opt-in 的工作区，在 `_meta/config.md` 写入 `cortex_enabled: true`；其他地方保持字段缺失或设为 `false`。
3. 如果 Mode 0 报告 hook health warning，运行 `bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh` 重新安装 Claude Code hooks。
4. 更新 Start Session / Adjourn eval baseline，加入固定 briefing 标题，并运行 `briefing-completeness`。

---

## [1.7.0] - 2026-04-22 · Cortex 认知层 · 正式发布

> Cortex 从 alpha 毕业,正式上线 GA。`v1.7.0-alpha.2` 之后 65 个 commits 关闭了剩余 TBD:5 个 shell hook 的完整运行时强制 + 共享 `_lib.sh`、10 个 Python 工具统一收敛到 `life-os-tool` CLI、3 个共享 Python 库、`docs/` 公共文档树发布、三语认知层文档、Step 0.5 / Step 7.5 契约同步到 CLAUDE / GEMINI / AGENTS 三个 host,以及一条保留每个现有 v1.6.2a second-brain 的迁移路径。

### ✨ 亮点

- **Cortex 路由前认知层转 GA** — 不再是 alpha 选装;完整契约 + 确定性降级
- **5 个 shell hook 运行时强制** — pre-prompt-guard / pre-write-scan / pre-read-allowlist / post-response-verify / stop-session-verify,共享 `_lib.sh`
- **10 个 Python 工具统一收敛到 `life-os-tool`** — reindex / reconcile / stats / research / daily-briefing / backup / migrate / search / export / seed(+ embed 占位 + sync-notion)
- **3 个 Python 库** — `tools/lib/{config, llm, notion}` 作为所有工具的共享底座
- **三语用户指南落地** — 6 个新 Cortex 指南(EN)+ cortex-spec / hippocampus-spec 的中日翻译
- **host 无关 orchestration 契约** — Step 0.5(路由前认知)+ Step 7.5(Narrator 校验)已在 CLAUDE.md / GEMINI.md / AGENTS.md(root + `pro/`)成为规范
- **Life OS agents 注册为 Claude Code 原生 subagents** — install 会从 22 个 `pro/agents/*.md` 定义生成 21 个可被 Task 调用的 `~/.claude/agents/lifeos-*.md` wrapper，跳过 ROUTER-internal 的 narrator 模板，确保 `Task(lifeos-retrospective)` 不再 fallback 到 `general-purpose`

### 功能

- **Cortex 子代理(路由前认知层)** — hippocampus 3 波会话检索 · GWT top-5 信号 salience 仲裁 · 概念图匹配 + 突触查找 · SOUL 维度冲突检测 · Narrator 引用包装 · Narrator-Validator 审计(Sonnet 层)
- **Shell hooks(5 个强制点 + 共享库)**
  - `pre-prompt-guard.sh` — UserPromptSubmit 时机的 Class B/C 策略 + Cortex 启用门禁
  - `pre-write-scan.sh` — 阻断对 `second-brain/wiki/**` 等受保护面的注入
  - `pre-read-allowlist.sh` — SSH/密钥黑名单 + cwd 白名单
  - `post-response-verify.sh` — 校验 `[COGNITIVE CONTEXT]` 分隔符 + adjourn checklist
  - `stop-session-verify.sh` — session 结束合规兜网(Adjourn Phase 4 在位、narrator 引用纪律)
  - `scripts/hooks/_lib.sh` — 5 个 hook 共用辅助函数(路径解析、JSON 读取、日志)
- **Python 工具(10 个交付 + 1 占位 + 1 Notion sync = `life-os-tool` 下 12 个)**
  - `reindex` — 一次性重建 session INDEX + concept INDEX + SYNAPSES
  - `reconcile` — 检测 SOUL / Wiki / Strategic-Map 与 session summaries 的漂移
  - `stats` — 违规升级阶梯 + `--period / --since / --output` 分析
  - `research` — deep-research 脚手架(Exa 做 web/code/company)
  - `daily_briefing` — 从 INDEX / STATUS / SOUL top-5 生成晨报
  - `backup` — 30d 归档 / 90d 删除轮转 + 违规日志季度归档
  - `migrate` — v1.6.2a → v1.7 迁移执行器(3 个月 backfill 窗口)
  - `search` — 子串 + 概念 slug 跨 second-brain 检索
  - `export` — 把 second-brain 序列化为可移植 bundle
  - `seed` — 从用户模板引导空 second-brain
  - `embed` — 占位(显式 no-op,符合 v1.7 决策 "不做向量 DB")
  - `sync_notion` — Notion 双向镜像(走 `tools/lib/notion.py`)
- **Python 库** — `tools/lib/config.py`(env + pyproject 解析)· `tools/lib/llm.py`(带重试 + token 记账的 LLM 调用封装)· `tools/lib/notion.py`(Notion API 客户端)
- **编排** — Step 0.5(路由前认知层)和 Step 7.5(Narrator 校验)同步入 CLAUDE.md、GEMINI.md、AGENTS.md(root 和 `pro/` 两级);契约从此 host 无关
- **引导工具** — `tools/seed_concepts.py` + 3 个面向用户的 second-brain bootstrap 模板;11 个测试

### 文档

- **6 个新 Cortex 用户指南** 落在 `docs/user-guide/cortex/`
  - `overview.md` — "Cortex 是什么" 入口
  - `hippocampus-recall.md` — 3 波 session 检索的工作方式
  - `concept-graph-and-methods.md` — 概念节点晋升 + 方法库信号
  - `narrator-citations.md` — 如何阅读和 trace `[S:][D:][SOUL:]` 引用
  - `gwt-arbitration.md` — salience 公式 + 为什么某信号进入 top-5
  - `auditor-eval-history.md` — eval-history 自反馈闭环
- `docs/guides/v1.7-migration.md` — 新增 "升级后的第一周:日常体验对标" 节
- `devdocs/architecture/cortex-integration.md` — 标记为 **deprecated**,对齐 spec freeze(真理源迁移到 `references/cortex-spec.md`)
- `docs/architecture/system-overview.md` — 更新 `_meta/` 分片路径 + Step 0.5 / Step 7.5 编排图
- `docs/getting-started/what-is-life-os.md` — Cortex 正式被列为第二大脑、决策引擎之外的第三根支柱
- `MIGRATION.md` — 开发机切换手册(修复了以 dash 开头路径的 tar 语法 bug)

### i18n

- `i18n/{zh,ja}/references/{concept,cortex,eval-history,gwt,hippocampus,hooks,method-library,narrator,session-index,snapshot,tools}-spec.md` — 11 份已冻结 v1.7 spec 的中日译本
- `i18n/{zh,ja}/docs/getting-started/what-is-life-os.md` + `i18n/{zh,ja}/docs/user-guide/cortex/*.md` — 本地化入门页 + 6 篇 Cortex 用户指南
- `README.md` + `i18n/{zh,ja}/README.md` — 三语主题块顺序、语言切换器与决策示例文案已对齐

### 基础设施

- **CI** — pytest 测试套件 **184 → 400(+216)**;ruff 告警 **50+ → 0**;bash 语法检查 **11/11** 绿
- **Makefile** — 常用开发命令(test / lint / format / build-docs)收敛
- `UV_LINK_MODE=copy` 写入 `~/.bashrc`,解决 `uv sync` 时 Dropbox 硬链接冲突
- `.github/workflows/test.yml` pytest 矩阵扩展,覆盖 10 个新工具模块 + 3 个新库模块
- `evals/scenarios/hook-compliance/` 下 8 个新 hook 合规场景(01-start-compliant-launch 到 08-arbitrary-prompt-silent)

### 破坏性变更 / 迁移

- 从 **v1.6.2a → v1.7.0** 的用户必须跑 `uv run life-os-tool migrate` — 迁移工具会把最近 3 个月的 journal / snapshot 数据回填到新的 `_meta/cortex/` 分片布局
- 在 v1.7.0 里,Cortex **新装默认启用**(相对 v1.7.0-alpha 的默认关闭翻转);现有 second-brain 沿用各自原有的 `cortex_enabled` 设置
- 完整迁移流程:`docs/guides/v1.7-migration.md`

### 合规

- Cortex GA 运行过程抓到 **2 个事件档案**
  - `backup/pro/compliance/2026-04-19-court-start-violation.md` — 已归档(已解决,经验吸收进 L1/L2 hook)
  - Narrator-spec 违规 — **已于 2026-04-22 解决**(已吸收到 Step 7.5 narrator-validator 契约)

### 涉及文件(节选,alpha.2 之后的 commits)

```
65b0d57 docs(i18n): publish zh/ja v1.7 specs and Cortex guide translations
170ca07 docs: publish v1.7 public docs trees (exclude plugin-system drafts)
8e47d61 docs(release): path docs/→devdocs/ in 8 specs + CHANGELOG SHA rewrite + tri-lingual sync
91b7896 chore(tests): remove unused pytest import in seed_concepts cleanup
fdf8748 chore(cli/tests): wire 10 v1.7 tools, fix Windows encoding, and track compliance dossiers
1b41f85 feat(tools): add seed.py + tests
9159e38 feat(tools): add migrate.py + tests
f2d5a1d feat(tools): add research.py + tests
b33f7dd feat(tools): extend stats.py aggregates and add sync_notion.py
7240446 feat(tools): add daily_briefing.py + tests
d2d43d8 feat(tools): add export.py + tests
b7e7335 feat(tools): add reconcile.py + tests
f8a26c6 feat(tools): embed.py placeholder + search.py (S5+S4 parallel-sprint merge)
032bdc7 feat(tools): add reindex.py + tests
2b7226f test(hooks): add 8 hook-compliance eval scenarios
0e5128b chore(hooks): extend setup-hooks.sh for v1.7 all 5 hooks
63e923e feat(hooks): add pre-read-allowlist.sh
5ff0d32 feat(hooks+lib): stop-session-verify.sh + Notion lib + pyproject (S1+S2 parallel-sprint merge)
4a2590f docs(orchestration): update root AGENTS.md with host-agnostic Step 0.5/7.5 contract
4ae2a65 feat(hooks): add pre-write-scan.sh
bf7f87e docs(orchestration): sync Step 0.5/7.5 to pro/AGENTS.md
877c629 feat(lib): add tools/lib/llm.py + tests
efa339d feat(lib): add tools/lib/config.py + tests
1414677 feat(hooks): add post-response-verify.sh
7c1fd3a docs(orchestration): sync Step 0.5/7.5 to GEMINI.md
a503301 feat(hooks): add pre-prompt-guard.sh
```

(另有 `tools/seed_concepts.py` + 模板、`MIGRATION.md`、`Makefile`、后续 spec/docs 发布 commits、三语 CHANGELOG 三份同步。)

---

## [1.7.0-alpha.2] - 2026-04-21 · v1.7.0-alpha 后续跟进打包

> 📚 **完整概览**：参见 [`references/v1.7-shipping-report-2026-04-21.md`](../../references/v1.7-shipping-report-2026-04-21.md) — 单页叙事文档，涵盖 v1.6.3 COURT-START-001 修复 + v1.7 Cortex 两条线。推荐作为"今天发了什么？"的起点。

> v1.7.0-alpha tag 之后 13 个 commit，关闭 alpha CHANGELOG 的 TBD + 加工具/测试基础设施。将合入 v1.7.0 稳定版。

### 🔧 新工具

- `tools/cli.py` — 统一子命令派发；`pyproject.toml` 启用 `life-os-tool` 控制台脚本
- `tools/backup.py` — 快照轮转（30d 归档、90d 删除）+ violations 日志按季度归档
- `scripts/lifeos-compliance-check.sh` — `check_adjourn()` + `check_cortex()` 实现（关闭 alpha 占位）
- `tools/lib/cortex/__init__.py` — 22 个辅助符号包级导出

### 📋 新 eval 场景

- `evals/scenarios/adjourn-compliance.md` — Class C/D/E + A3 检测
- `evals/scenarios/cortex-retrieval.md` — CX1-CX7 检测 + 降级路径

### ✅ 测试套件扩展

- `tests/test_backup.py` — 19 测试
- `tests/test_cli.py` — 8 测试
- `tests/test_compliance_check.py` — 11 subprocess-based 测试
- `tests/test_integration.py` — 7 端到端集成测试

**总测试数：122，全部 0.68s 通过。**

### 🚀 CI

- `.github/workflows/test.yml` — pytest 矩阵 + bash 语法 + smoke 测试

### 📚 架构文档

- `references/cortex-architecture.md` — 端到端数据流 + 信息隔离矩阵 + 失败级联 + 成本概况 + 合规映射

### 🔌 接线打磨

- `pro/CLAUDE.md` Information Isolation 表扩展全 6 个 v1.7 子代理
- `pro/agents/archiver.md` 加 "Phase 2 Mid-Step — SOUL Snapshot"

### 🐛 Bug 修复

- `tools/cli.py` `_print_usage(stream=sys.stdout)` 默认值求值时机 bug
- `scripts/lifeos-compliance-check.sh` `set -e` + `grep -c` 静默退出 bug
- 正则 `\s` (GNU only) → POSIX `[[:space:]]` 可移植性

### 涉及文件(alpha 之后的 commits)

```
b1bf474 feat: tools/cli.py dispatcher + check_cortex() + pyproject scripts entry
4fa8db9 feat: check_adjourn() implementation + cortex-retrieval eval scenario
81c96ec feat: v1.7.0-alpha follow-up — backup.py + adjourn eval + CI workflow
2fecaa9 test: end-to-end integration tests for Cortex pipeline (7 tests)
72c942c feat: tools.lib.cortex package exports + Info Isolation table + archiver snapshot step
eb477a5 feat: tests/test_cli + test_compliance_check + cortex-architecture doc
```

（另加 1ce61d1 v1.7.0-alpha 发布 commit 本身。）

---

## [1.7.0-alpha] - 2026-04-21 · Cortex 路由前认知层

> Life OS 历史上首次 Layer 2 架构升级。把跨会话记忆、概念图、身份信号作为每次决策工作流的输入。今日 19 个 commit 将 v1.7 从 spec 草稿推到功能完整。

### 🧠 路由前认知层（编排 Step 0.5）

当 `_meta/config.md` 设 `cortex_enabled: true` 时，所有非 Start-Session 的用户消息在 ROUTER 分诊**之前**经过 4 个并行子代理：

```
user message
    ↓
Step 0.5（路由前认知层）
    ├─ hippocampus       → 3 波会话检索（5-7 个 sessions）
    ├─ concept-lookup    → 概念图匹配（5-10 个 concepts）
    └─ soul-check        → SOUL 维度信号（top 5）
         ↓
    gwt-arbitrator        → 用 salience 公式选 top-5 信号
         ↓
[COGNITIVE CONTEXT] 块前置到 user message
    ↓
Step 1（ROUTER 用注释化输入分诊）
```

REVIEWER 终审后，可选的 `narrator` 用 `[source:signal_id]` 引用包装 Summary Report 实质性主张。`narrator-validator`（Sonnet 层）审计引用纪律。

### 📋 6 个新子代理（~900 行 markdown 契约）

| 代理 | 文件 | spec |
|------|------|------|
| hippocampus | `pro/agents/hippocampus.md` | `references/hippocampus-spec.md` |
| concept-lookup | `pro/agents/concept-lookup.md` | `references/concept-spec.md` |
| soul-check | `pro/agents/soul-check.md` | 派生自 soul-spec + gwt-spec §6 |
| gwt-arbitrator | `pro/agents/gwt-arbitrator.md` | `references/gwt-spec.md` |
| narrator | `pro/agents/narrator.md` | `references/narrator-spec.md` |
| narrator-validator | `pro/agents/narrator-validator.md` | narrator-spec validator 部分 |

6 个代理全部强制信息隔离：拒绝同层 Pre-Router 代理的输出。全部只读——只在 archiver Phase 2 发生写入。

### 🐍 Python 工具（~1500 行 · 纯 stdlib + pyyaml）

| 模块 | 职责 |
|------|------|
| `tools/lib/second_brain.py` | 11 种 second-brain 类型 dataclass + frontmatter parser/dumper + 路径解析 |
| `tools/lib/cortex/session_index.py` | SessionSummary IO + INDEX.md 编译（幂等）|
| `tools/lib/cortex/concept.py` | Concept IO + INDEX/SYNAPSES 编译 + Hebbian 更新 |
| `tools/lib/cortex/snapshot.py` | SoulSnapshot IO + 归档策略（30d/90d）|
| `tools/stats.py` | 合规违规升级阶梯执行 |

### 🔧 4 个 CLI 工具

```bash
uv run tools/rebuild_session_index.py [--root PATH] [--dry-run]
uv run tools/rebuild_concept_index.py [--root PATH] [--dry-run] [--no-synapses]
uv run tools/stats.py [--violations PATH] [--json]
bash scripts/setup-hooks.sh   # 自动注册 SessionStart + UserPromptSubmit hooks
```

### ✅ 77 个 pytest 测试 — 全部通过 0.23 秒

| 文件 | 测试数 |
|------|------|
| `tests/test_second_brain.py` | 15（frontmatter / dataclass / 路径）|
| `tests/test_session_index.py` | 16（truncate / write / compile / rebuild / 幂等）|
| `tests/test_concept_and_snapshot.py` | 18（concept IO / INDEX / SYNAPSES / Hebbian / 快照策略）|
| `tests/test_stats.py` | 18（parse / 升级 / 阈值 / 路径解析）|

```bash
python3 -m pytest tests/ -v        # 77 passed in 0.23s
```

### 🚦 默认 OFF（按需启用）

Cortex 在 v1.7.0-alpha 默认禁用。用户启用：

```bash
echo "cortex_enabled: true" >> _meta/config.md
```

建议在 second-brain 累积 ≥30 个 sessions 后启用。成本：~$0.05-0.25/turn（Opus tokens 跨 Pre-Router 子代理）。

### 📊 Cortex 合规分类（已加入 AUDITOR Mode 3）

| 代码 | 名称 | 严重度 |
|------|------|------|
| CX1 | Skip Pre-Router subagents | P1 |
| CX2 | Skip GWT arbitrator | P1 |
| CX3 | Missing [COGNITIVE CONTEXT] delimiters | P1 |
| CX4 | Hippocampus session cap exceeded | P1 |
| CX5 | GWT signal cap exceeded | P1 |
| CX6 | Cortex isolation breach | P0 |
| CX7 | Cortex write breach | P0 |

`cortex_enabled: false` 时跳过所有 CX 检测。

### 📁 涉及文件（19 个 commits）

Specs：`references/{cortex,hippocampus,gwt,concept,snapshot,session-index,narrator,hooks,tools,eval-history,method-library}-spec.md` + 8 个既有 references 修改。
子代理：`pro/agents/{hippocampus,gwt-arbitrator,concept-lookup,soul-check,narrator,narrator-validator}.md`。
接线：`pro/CLAUDE.md`、`pro/agents/{archiver,retrospective,auditor}.md`。
工具：`tools/lib/{second_brain.py,cortex/*}`、`tools/{stats,rebuild_session_index,rebuild_concept_index}.py`。
项目：`pyproject.toml`、`.python-version`、`tools/README.md`。
测试：`tests/{__init__,test_second_brain,test_session_index,test_concept_and_snapshot,test_stats}.py`。
Hooks：`scripts/lifeos-compliance-check.sh`（v1.6.3 链的 L5 闭环）。
文档：3 个 README + 3 个 CHANGELOG（本 commit）。

### 🚧 已知限制 / 待办

- **生产验证待办** — alpha 通过 pytest + 规格合规性测试，但未在真实 user second-brain 大规模实战
- **`concept-lookup` 不做边遍历** — 仅 Wave 1；Wave 2/3 是 hippocampus 的领域
- **Narrator validator** Phase 2 用自检环；独立 validator 子代理待 Phase 2.5
- **`tools/backup.py`** 快照归档轮转：延后到 v1.7.0 稳定版
- **adjourn-compliance eval 场景** 仍为占位

### 迁移

现有用户（v1.6.3b → v1.7.0-alpha）：
1. 重装 skill：`/install-skill https://github.com/jasonhnd/life_OS`
2. 重跑 hooks 安装：`bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh`
3.（可选）安装 Python 工具：`cd ~/.claude/skills/life_OS && uv sync`
4.（可选）启用 Cortex：`echo "cortex_enabled: true" >> {你的 second-brain}/_meta/config.md`

默认 OFF 意味着现有用户除非主动启用否则零行为变化。v1.6.3 五层合规防御保持激活不变。

---

## [1.6.3b] - 2026-04-21 · AUDITOR Mode 3 自动触发已接线

> v1.6.3 把 Mode 3（Compliance Patrol）规格交付到 `pro/agents/auditor.md`，但**没人实际调用它**。在用户 second-brain 的首次生产运行确认了这个缺口：retrospective Mode 0 完成、简报显示，但没有 AUDITOR Compliance Patrol 报告。五层防御的第 4 层处于失活状态。

### 🔧 修复

`pro/CLAUDE.md` Orchestration Code of Conduct 新增规则 #7：

> **AUDITOR Compliance Patrol 自动触发** — 每次 `retrospective` Mode 0（Start Session）完成或 `archiver` 返回后，orchestrator 必须启动 `auditor` 的 Mode 3（Compliance Patrol）。不可跳过。HARD RULE。

3 个配套文档更新使契约显式：

- `pro/agents/retrospective.md` — 加 "Auto-Follow: AUDITOR Compliance Patrol" 段，注明 orchestrator 在 Mode 0 返回后链接 Mode 3。子代理本身不启动 AUDITOR。
- `pro/agents/auditor.md` — Mode 3 "When to run" 段加明确触发契约：orchestrator 启动，非自启动，交叉引用 `pro/CLAUDE.md` 规则 #7。
- `SKILL.md` — 版本 1.6.3a → 1.6.3b。

### 📊 五层防御状态（v1.6.3b 后）

| 层 | 状态 |
|-------|--------|
| L1 · UserPromptSubmit hook | ✅ v1.6.3 交付 · setup-hooks.sh 自动安装（v1.6.3a）|
| L2 · Pre-flight Compliance Check | ✅ 已交付 + 2026-04-21 生产验证 |
| L3 · Subagent Self-Check | ✅ 已交付 + 2026-04-21 生产验证 |
| L4 · AUDITOR Compliance Patrol（Mode 3）| ✅ 规格已交付（v1.6.3）· **触发已接线（v1.6.3b）** |
| L5 · Eval 回归 | ✅ 场景已交付（v1.6.3）· auto-runner 扩展延后到 v1.7 |

### 涉及文件

- `SKILL.md`（版本 1.6.3a → 1.6.3b）
- `pro/CLAUDE.md`（+ Orchestration 规则 #7）
- `pro/agents/retrospective.md`（+ Auto-Follow 段）
- `pro/agents/auditor.md`（Mode 3 "When to run" 触发契约明确化）
- `README.md` + 三语（徽章）
- `CHANGELOG.md` + 三语

### 迁移

用户无需操作。现有 v1.6.3a 安装会在下次会话自动启用规则 #7。今后每次 Start Session 和 Adjourn 结束都会出 AUDITOR Compliance Patrol 报告。无违规时的输出格式：

```
🔱 [theme: auditor] · Compliance Patrol (v1.6.3)
✅ All 6 Start Session compliance checks passed
No violations logged. Session adheres to v1.6.3 HARD RULES.
```

---

## [1.6.3a] - 2026-04-21 · v1.6.3 热修补 · 第 1 层安装缺口 + Hook 假阳性守卫

> v1.6.3 在用户 second-brain 的首次生产运行（同日）验证了第 2-5 层防御端到端 work。同时暴露 2 个真实 gap：
> 1. **第 1 层（UserPromptSubmit hook）未自动注册** — `/install-skill` 只复制文件，不改 `~/.claude/settings.json`。默认安装下 L1 直接没了。
> 2. **Hook regex 误报粘贴内容** — 粘贴的转录里含触发词时会错误触发 reminder。

### 🔧 修复 1 — 第 1 层安装自动化

`scripts/setup-hooks.sh` 重构：
- 单次运行同时安装 SessionStart hook（版本检查）和 UserPromptSubmit hook（第 1 层防御）
- 加入 `register_hook()` 辅助函数，DRY 幂等注册跨事件类型
- 幂等：可安全反复运行；已注册的 hook 跳过
- 向后兼容：现有 v1.6.3 安装不受影响；重跑会干净地补上 L1

用户在 install/upgrade 后跑一次：
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```

### 🔧 修复 2 — Hook 假阳性降低

`scripts/lifeos-pre-prompt-guard.sh` 在 regex 匹配前加两道前置检查：
- **长度检查**：prompt 整体 ≤ 500 字符（长 prompt = 对话/粘贴，非指令）
- **首行检查**：首个非空行 ≤ 100 字符（过滤掉段落式开头的粘贴块）

触发词 regex 现仅对**首行**匹配（此前为多行）。粘贴含触发词的转录不再触发 hook。

### 🆕 F 类 · 假阳性

加入 `references/compliance-spec.md` Type Taxonomy 和 `pro/compliance/violations.md` Type Legend：

| 代码 | 名称 | 默认严重度 |
|-----|------|-----------|
| **F** | False positive | P2（信息性）— hook 触发在粘贴/引用内容，非真实用户指令。从升级阶梯中排除。|

首条 F 类记录：2026-04-21T13:42 — 在 dev repo 粘贴 v1.6.3 生产验证转录触发了 hook。Assistant 正确识别为粘贴上下文并拒绝启动 retrospective。已由修复 2 缓解。

### 📋 COURT-START-001 状态推进

`pro/compliance/violations.md` 中 4 条 incident 条目加注生产验证证据：
- L2（Pre-flight Compliance Check）— 2026-04-21 user second-brain 验证 work
- L3（Subagent Self-Check）— 2026-04-21 user second-brain 验证 work
- L4（AUDITOR Compliance Patrol）+ L5（eval 回归）— 等观察窗

`partial → true` 转换仍按 `references/compliance-spec.md` 等待 eval 回归通过 + 30 天无复发窗。

### 涉及文件

- `SKILL.md`（版本 1.6.3 → 1.6.3a）
- `scripts/setup-hooks.sh`（重构 + register_hook 辅助函数 + UserPromptSubmit 注册）
- `scripts/lifeos-pre-prompt-guard.sh`（+ 长度检查 + 首行提取）
- `references/compliance-spec.md`（+ F 类入 Type Taxonomy）
- `pro/compliance/violations.md`（+ F 类入 legend，+ 1 条 F 记录，+ 4 条 COURT-START-001 加 L2/L3 验证注解）
- `pro/compliance/violations.example.md`（+ Example 11 F 类）
- `README.md` + 三语（版本徽章 + v1.6.3a 热修补提示）
- `CHANGELOG.md` + 三语

### 迁移

现有 v1.6.3 安装：
```bash
bash ~/.claude/skills/life_OS/scripts/setup-hooks.sh
```
激活第 1 层防御。其他无需操作；L2-5 不变。

新安装：同一行命令一次激活所有层。

---

## [1.6.3] - 2026-04-21 · COURT-START-001 修复 · 五层防御

> 用户在 Life OS 开发 repo 说"上朝"，ROUTER 跳过 retrospective 子代理，在主上下文模拟 18 步流程，并编造不存在的路径 `_meta/roles/CLAUDE.md § 0 Pre-Court Preparation` 作为权威源。用户反应："这样的 life os 如何拿给别人用？？？我无法接受。"本次发布交付五层防御，让每一条 HARD RULE 真正 hard。

### 🛡️ 针对 A / B 类违规的五层防御

COURT-START-001 根因：文档完整，但**每一条 HARD RULE 都是描述性的——零强制机制**。作者本人都会被 LLM 糊弄；普通用户被糊弄是必然。五层独立防御守护每个触发词：

1. **Hook 层** — `scripts/lifeos-pre-prompt-guard.sh` 在 `UserPromptSubmit` 时触发，检测触发词（上朝 / start / 閣議開始 / 退朝 / 等，覆盖 9 个主题），在助手响应前把 HARD RULE 文本 + 违规分类作为 `<system-reminder>` 注入上下文。
2. **Pre-flight Compliance Check** — `SKILL.md` 要求 ROUTER 在任何工具调用前先输出 1 行确认：`🌅 Trigger: [词] → Theme: [名] → Action: Launch([agent]) [Mode]`。缺此行 = A3 类违规，登记。
3. **子代理自检** — `pro/agents/retrospective.md` Mode 0 第一句必须是：`✅ I am the RETROSPECTIVE subagent (Mode 0, not main context simulation). Reading pro/agents/retrospective.md. Starting Step 1: THEME RESOLUTION.`。证明子代理真的被启动。
4. **AUDITOR 合规巡检（Mode 3）** — `pro/agents/auditor.md` 新增 Mode 3，含 7 类违规分类（A1/A2/A3/B/C/D/E）和 Start Session / Adjourn 路径的 6 项检测。每次 retrospective Mode 0 和 archiver 完成后自动运行。
5. **Eval 回归** — `evals/scenarios/start-session-compliance.md` 把 COURT-START-001 的 6 个失败模式固化为质量检查点，含 grep 失败检测命令。

### 📋 违规分类（7 类）

| 代码 | 名称 | 默认严重度 |
|-----|------|-----------|
| A1 | 跳过子代理 — ROUTER 在主上下文模拟子代理的步骤 | P0 |
| A2 | 跳过目录检查 — dev repo 绕过 retrospective Step 2 | P1 |
| A3 | 跳过 Pre-flight — 首次响应缺 `🌅 Trigger: ...` 行 | P1 |
| B | 编造事实 — 引用不存在路径 / 章节作为权威 | P0 |
| C | 阶段未完成 — archiver 未跑完 4 阶段就退出 | P0 |
| D | 占位值 — 完成清单含 `TBD` / `{...}` / 空值 | P1 |
| E | 主上下文执行阶段 — ROUTER 在主上下文跑 Phase 1-4 逻辑 | P0 |

### 📁 双仓库 compliance 日志（md + git · 遵循用户约束）

用户明确要求："我可以接受本地的 sh 命令执行，但是数据库还是要 md 文件和 github 去储存。"违规持久化到：

- `pro/compliance/violations.md` — dev repo（公开，随 Life OS 发布）
- `_meta/compliance/violations.md` — user second-brain（私有，每用户独立）

同一格式：`| Timestamp | Trigger | Type | Severity | Details | Resolved |`。

**升级阶梯**（由 v1.7 的 `tools/stats.py` 实现，在此之前由开发者手动观察）：
- 30 天内同类 ≥3 → hook 提醒加严
- 30 天内同类 ≥5 → retrospective briefing 顶部加 `🚨 Compliance Watch`
- 90 天内同类 ≥10 → AUDITOR 每次 Start Session 都跑合规巡检

### 🗂️ 新增文件

- `scripts/lifeos-pre-prompt-guard.sh` — UserPromptSubmit hook（bash，已 chmod +x）
- `.claude/settings.json` — dev repo 的 hook 注册
- `references/compliance-spec.md` — 完整规格：分类、双仓库策略、写入/读取路径、升级阶梯、归档、解决协议、隐私
- `pro/compliance/violations.md` — dev-repo 实时日志（含 COURT-START-001 的 5 条种子条目）
- `pro/compliance/violations.example.md` — 每类 10 个示例条目 + grep 配方
- `pro/compliance/2026-04-19-court-start-violation.md` — 完整 incident 档案（473 行，12 节）
- `evals/scenarios/start-session-compliance.md` — COURT-START-001 的 6 个失败模式回归测试

### ✏️ 修改文件

- `.claude/CLAUDE.md` — 新增 Start Session 触发约束的 HARD RULE 段
- `SKILL.md` — 版本 1.6.2a → 1.6.3，Start Session 路由前新增 Pre-flight Compliance Check 段
- `pro/agents/retrospective.md` — 执行步骤前新增子代理自检块
- `pro/agents/auditor.md` — Mode 3（合规巡检），含 7 类违规分类 + 检测逻辑

### 🔄 解决协议

违规状态流转 `false → partial → true`，经过三个闸门：
- **Gate 1**（`false → partial`）：底层修复已交付（Details 字段注版本号）
- **Gate 2**（`partial → true`）：eval 回归通过 + 30 天已过 + 无复发（注版本 + eval-id + 观察日）

COURT-START-001 的 4 条 incident 条目在本次发布转为 `partial`。转 `true` 需要 `evals/scenarios/start-session-compliance.md` 通过 + 30 天观察窗。

### 迁移

现有安装无需操作。升级后首次 Start Session：
- hook 注册（仅 dev repo，经 `.claude/settings.json`）
- Pre-flight 行成为必填
- AUDITOR 在首次 retrospective Mode 0 后跑合规巡检
- violations.md 如缺失则自动创建（空表）

希望启用双仓库违规登记的 second-brain 用户，按 `references/compliance-spec.md` 在自己的 `.claude/settings.json` 加 hook 块即可。

---

## [1.6.2a] - 2026-04-19 · Notion 同步回归编排层

> archiver subagent 报告"Notion MCP 未接入"，因为 Notion MCP 工具是环境特定的，在 subagent 内不可用。Notion 同步现在从 archiver 中拆出，由编排层（主上下文）执行，主上下文拥有 MCP 工具访问权限。

### 变更

- **archiver.md**：Phase 4 缩减为仅 git 操作；Notion 同步移除并注明 MCP 工具限制
- **CLAUDE.md**：新增 Step 10a — 编排层在 archiver 返回后执行 Notion 同步
- **GEMINI.md / AGENTS.md**：同步 Step 10a
- **SKILL.md**：退朝模板更新为包含 Notion 同步作为 archiver 后续步骤

---

## [1.6.2] - 2026-04-17 · 退朝防御 + Wiki/SOUL 自动写入 + DREAM 10 触发器

> 三项加固同时发布：(1) 退朝流程无法被部分跳过；(2) wiki 和 SOUL 在严格标准下自动写入，不再询问用户确认；(3) DREAM 获得 10 个具体的自动触发行动。

### 🛡️ 退朝三层防御

此前 bug：ROUTER 有时在主上下文中执行 Phase 2（知识提取），而非启动 ARCHIVER 子代理，导致 4 阶段流程被拆分。

三重独立防御：
- **SKILL.md + archiver.md 措辞加固** — HARD RULE 禁止 ROUTER 在主上下文中执行任何 Phase 内容；archiver.md 新增明确的"Subagent-Only Execution"条款
- **退朝状态机（pro/CLAUDE.md）** — 列出合法/非法状态转换；AUDITOR 将每次违规记入 user-patterns.md
- **强制启动模板** — SKILL.md 新增"Trigger Execution Templates (HARD RULE)"章节，钉死 Start Session / Adjourn / Review 的精确输出格式

### 📚 Wiki 自动写入（无需用户确认）

此前：archiver 列出 wiki 候选让用户挑选保存。中断流程且鼓励跳过。

现在：archiver 在 **6 项严格标准 + 隐私过滤器** 下自动写入：
1. 跨项目可复用
2. 关于世界而非关于你（价值观 → SOUL，不进 wiki）
3. **零个人隐私** — 姓名、金额、账户 ID、具体公司、家人朋友信息、可追溯的日期+地点组合 → 剥离；若剥离后结论变得无意义 → 丢弃
4. 事实或方法论
5. 多个证据点（≥2 个独立）
6. 不与现有 wiki 矛盾（矛盾 → 现有条目 `challenges: +1`，不创建竞争条目）

初始置信度：3+ 证据 → 0.5；恰好 2 个 → 0.3；1 个或更少 → 丢弃。

用户事后调整：删除文件 = 废弃；说"撤销最近 wiki"回滚最近的自动写入；手动将 `confidence` 调至 0.3 以下即可抑制。

### 🔮 SOUL 自动写入 + 持续运行时

此前：SOUL 维度只通过用户确认创建；只定期显示。

现在：
- **ADVISOR 每次决策自动更新** — 每次 Summary Report 后，为现有 SOUL 维度递增 `evidence_count` 或 `challenges`；检测到 ≥2 证据点的新维度时，以 `confidence: 0.3` 自动写入，"What SHOULD BE"字段故意留空让用户自行填写
- **REVIEWER 强制引用 SOUL** — 每次决策必须引用相关 SOUL 维度，或明确标注"无直接相关维度，此决策可能开启一个新维度"
- **SOUL 健康报告固定在简报顶部位置** — 每次上朝，Pre-Session Preparation 之后第一个区块即 🔮 SOUL Health Report（当前画像带趋势箭头、新检测出的待输入维度、冲突警告、30+ 天休眠维度、轨迹变化）

置信度公式不变：`confidence = evidence_count / (evidence_count + challenges × 2)`。

### 💤 DREAM 10 个自动触发行动（REM 阶段）

REM 现在评估 10 个具体模式，匹配即自动执行：

| # | 模式 | 自动行动 |
|---|------|---------|
| 1 | 新项目关系 | 写 STRATEGIC-MAP 候选 + 简报显眼位置 |
| 2 | 行为 ≠ driving_force | 注入下次 ADVISOR 输入 |
| 3 | Wiki 被新证据反驳 | 该条目 `challenges: +1` |
| 4 | SOUL 维度休眠 30+ 天 | 简报警告 |
| 5 | 跨项目认知未使用 | 下次 DISPATCHER 强制注入 |
| 6 | 检测到决策疲劳 | 建议"今天不做重大决策" |
| 7 | driving_force 价值漂移 | 自动提议 SOUL 修订 |
| 8 | 陈旧承诺（30+ 天无行动） | 简报唤起 |
| 9 | 情绪化决策模式 | 下次 REVIEWER 加情绪状态检查 |
| 10 | 重复相同决策 | 简报提示"你在回避承诺吗？" |

所有标志写入 dream journal 的 `triggered_actions` YAML 块。下次上朝时 RETROSPECTIVE 在固定的"💤 DREAM Auto-Triggers"简报区块显示。

### 🔬 设计细化（详细规范）

在以上四根概念支柱之上，v1.6.2 还交付了详细的行为规范：

**DREAM 触发器检测逻辑** —— 10 个触发器每一个都具备：
- **硬性阈值**（定量规则，自动触发）
- **软性信号**（LLM 定性线索，以 `mode: soft` 触发并需要 AUDITOR 审核）
- 明确的数据源、24 小时反重复抑制、结构化输出

示例：决策疲劳 = "24 小时内 ≥5 决策 且 后半段平均分 ≤ 前半段 -2"；价值漂移 = "30 天内 ≥3 挑战 且 ≤1 新证据 且 confidence 下降 >30%"；陈旧承诺 = "'我会 X'正则匹配 + 30 天无对应完成"；情绪化决策 = "ADVISOR 情绪标记 + REVIEWER 建议冷静 + 仍推进"；重复决策 = "主题关键词与过去 30 天 ≥2 决策重叠 >70%"。完整 10 项见 `references/dream-spec.md`。

**ADVISOR SOUL Runtime 统一** —— 合并了旧的只读"SOUL 行为审计"节与新的自动更新机制。单一统一流程：逐维度影响（支持/挑战/中立）→ 写入 evidence/challenge 增量 → 检测新维度 → 冲突预警 → 输出 🔮 SOUL Delta 块。每次决策运行，不仅限于散朝。

**SOUL 快照机制用于趋势箭头** —— archiver Phase 2 现在在每次会话结束时向 `_meta/snapshots/soul/YYYY-MM-DD-HHMM.md` 导出一份最小化快照（仅数字元数据，不重复内容）。RETROSPECTIVE 在下次上朝时读取最新快照并计算：
- `confidence_Δ > +0.05` → ↗
- `confidence_Δ < -0.05` → ↘
- `|confidence_Δ| ≤ 0.05` → →
加上特殊状态：🌟 新晋核心、⚠️ 从核心降级、💤 休眠、❗ 冲突区。归档策略：>30 天 → `_archive/`，>90 天 → 删除（git + Notion 保留）。

**REVIEWER SOUL 3 层引用策略** —— 避免 SOUL 维度多时产生噪音：
- **Tier 1**（confidence ≥ 0.7）：全部引用，无上限 —— 核心身份必须考虑
- **Tier 2**（0.3 ≤ confidence < 0.7）：通过强/弱匹配判断挑选语义最相关的 3 条
- **Tier 3**（confidence < 0.3）：仅计数，不露面（ADVISOR 在 Delta 中追踪）

决策挑战 Tier 1 维度 → REVIEWER 在 Summary Report 顶部加 ⚠️ SOUL CONFLICT 警告（半否决信号）。每个被评估的 Tier 2 维度必须列出入选理由，供 AUDITOR 审查质量。

### 涉及文件

- `SKILL.md`（版本 + 触发模板）
- `pro/CLAUDE.md`（状态机 + wiki/SOUL 自动写入描述）
- `pro/GEMINI.md` / `pro/AGENTS.md`（跨平台 Gemini CLI + Codex CLI 一致性）
- `pro/agents/archiver.md`（Phase 2 自动写入 + 快照导出 + Phase 3 10 触发器检测逻辑）
- `pro/agents/advisor.md`（统一 SOUL Runtime：5 步，每次决策）
- `pro/agents/reviewer.md`（3 层 SOUL 引用策略）
- `pro/agents/retrospective.md`（Step 11 扩展为 11.1-11.6：快照读取 + 趋势计算）
- `references/wiki-spec.md` + 三语（6 标准 + 隐私过滤器 + 用户调整）
- `references/soul-spec.md` + 三语（自动写入 + 快照机制 + 分层引用）
- `references/dream-spec.md` + 三语（10 触发器逐节含硬/软检测）
- `references/data-layer.md` + 三语（`_meta/snapshots/` 加入目录树 + 反映自动写入）
- `README.md` + 三语（v1.6.2 新特性 + 第五节重写 + 架构图）
- `CHANGELOG.md` + 三语

### 迁移

用户无需操作。现有 wiki/SOUL 条目继续工作。新条目将从下次会话开始自动写入。升级后首次上朝将显示"暂无趋势数据"，直到第二次会话提供快照基线。要抑制某个自动写入条目但不删除：在 frontmatter 中将 `confidence: 0.0`。

---

## [1.6.1] - 2026-04-16 · 九大主题 — 每种文化，每种风格

> 主题系统从 3 个扩展到 9 个。每种语言现在提供三种治理风格：历史、现代政府、企业。

### 新增主题

**English**（共 3 个）：
- 🏛️ Roman Republic — Consul, Tribune（veto 的发明者）, Senate
- 🇺🇸 US Government — Chief of Staff, Attorney General, Treasury, GAO
- 🏢 Corporate — CEO, General Counsel, CFO（已有，未变）

**中文**（共 3 个）：
- 🏛️ 三省六部 — 丞相、中书省、门下省（已有，未变）
- 🇨🇳 中国政府 — 国务院总理、发改委、人大常委会、审计署
- 🏢 公司部门 — 总经理、战略规划部、法务合规部、内审部

**日本語**（共 3 个）：
- 🏛️ 明治政府 — 内閣総理大臣、参議、枢密院、大蔵省、元老
- 🏛️ 霞が関 — 内閣官房長官、内閣法制局、財務省（已有，未变）
- 🏢 企業 — 社長室、経営企画部、法務部、内部監査室

### 主题选择器更新

选择器按语言分组显示。触发词推断更智能：
- "上朝" → 自动加载三省六部（唐朝专属词）
- "閣議開始" → 自动加载霞が関（现代政府专属词）
- 通用触发词（"开始"、"はじめる"、"start"）→ 显示该语言的 3 个子选项

---

## [1.6.0] - 2026-04-15 · Theme Engine — 一套引擎，服务所有文化

> 一位日本用户试用了 Life OS，体验很差——不是因为逻辑有问题，而是因为"三省六部"是中国文化概念，对非中文用户造成了学习门槛。v1.6.0 通过将决策引擎与文化呈现分离来解决这个问题。

### 核心变化

Life OS 现在是一个**通用决策引擎**，搭配**可切换的文化主题**。治理逻辑（规划 → 审查 → 否决 → 执行 → 审计）在所有主题下完全一致——只有名称、语气和隐喻发生变化。

### 三层架构

**Layer 1: Engine** — 16 个 agent，使用功能性 ID（ROUTER, PLANNER, REVIEWER, DISPATCHER, 6 个领域分析师, AUDITOR, ADVISOR, COUNCIL, RETROSPECTIVE, ARCHIVER, STRATEGIST）。语言中立，文化中立。

**Layer 2: Theme** — 可切换的文化皮肤，将功能性 ID 映射到熟悉的名称：
- `zh-classical` — 三省六部（唐朝治理制度）：丞相、中书省、门下省、六部、御史台……
- `ja-kasumigaseki` — 霞が関（日本中央省庁）：内閣官房長官、内閣法制局、財務省、会計検査院……
- `en-csuite` — C-Suite（企业高管）：Chief of Staff、General Counsel、CFO、Internal Audit……

**Layer 3: Locale** — 自动检测用户语言，推荐匹配的主题。用户可随时切换。

### 主题选择 UI

每次开朝时，RETROSPECTIVE agent 呈现一个简洁的选择界面：
```
🎨 选择你的主题：
 a) 🏛️ 三省六部 — 唐朝治理制度（中国古典）
 b) 🏛️ 霞が関 — 日本中央省庁（霞が関）
 c) 🏛️ C-Suite — 企业高管架构（英文）

输入 a、b 或 c
```

- **主题选择是每个会话独立的**——不同终端窗口可以使用不同主题，互不影响
- 主题选择不会跨会话持久化；每次新会话都会重新提示选择
- 会话中随时可以说"切换主题"来更换

### 具体变更

- **16 个 agent 文件重命名**：中文拼音（chengxiang.md, zhongshu.md...）→ 功能性英文（router.md, planner.md...）
- **themes/ 目录创建**：3 个主题文件（每个约 60 行），定义角色映射、语气、触发词、输出标题
- **i18n agent 重复消除**：48 个 agent 文件（16 × 3 语言）→ 16 个文件。主题处理展示，agent 处理逻辑
- **约 42 个翻译后的 agent/编排文件删除**：不再需要——每个 agent 一个事实来源
- **departments.md → domains.md**：六部 → Six Domains（PEOPLE, FINANCE, GROWTH, EXECUTION, GOVERNANCE, INFRA）
- **所有编排协议更新**：CLAUDE.md、AGENTS.md、GEMINI.md 使用功能性 ID
- **所有参考文档更新**：data-layer、data-model、strategic-map-spec、wiki-spec、soul-spec、dream-spec、scene-configs
- **所有评估场景更新**：测试用例使用功能性 ID（router-triage.md、council-debate.md）

### 为什么重要

- **日本用户**看到財務省、法務省、会計検査院——零学习成本
- **英语用户**看到 CFO、General Counsel、Internal Audit——直觉即懂
- **中文用户**仍然看到丞相、中书省、门下省——什么都没丢
- **开发者**维护 16 个 agent 文件而非 48 个——每次逻辑变更只需改一处
- **新主题**只需一个约 60 行的文件——不需要修改引擎

### 零功能损失

所有 28 条硬规则保持不变。所有评分标准完整。所有输出格式保持不变（名称随主题变化）。SOUL、DREAM、Wiki、Strategic Map、Completion Checklist、封驳循环、会话生命周期——一切运作如前。已通过完整的 34 项保存清单验证。

---

## [1.5.0] - 2026-04-15 · 战略地图 — 从项目助手到人生战略师

> Life OS 能出色地分析任何单个项目，但对项目之间的关联视而不见。当多个活跃项目共享依赖、资源和隐藏的战略目的时，系统需要一个关系层。战略地图正是为此而生——并与 SOUL、Wiki、DREAM 深度集成，形成统一的认知系统。

### 问题

你有多个项目。有些向其他项目输送知识，有些共享你有限的时间，有些存在的目的与你真正的动机并不相同。当一个项目停滞时，它会悄悄阻塞另外三个。但早朝简报只展示一个扁平列表——没有关系、没有优先级、没有"今天我到底该做什么？"。

### 新增内容

**战略线** — 按战略目的对项目分组。每条战略线有 `purpose`（正式目的）、`driving_force`（真正驱动你的动力）和 `health_signals`（关注指标）。多个项目可以不同角色服务同一条战略线：`critical-path`、`enabler`、`accelerator`、`insurance`。

**流动图** — 定义项目间的流动：`cognition`（知识）、`resource`（交付物）、`decision`（约束）、`trust`（关系资本）。当项目 A 的决策使项目 B 的假设失效时，系统会警告你。

**叙事式健康评估** — 不再使用"6/10 🟡"评分。基于 Klein 的识别启发式决策模型，系统将项目匹配到健康原型（🟢 稳步推进 / 🟡 受控等待 / 🟡 动量衰减 / 🔴 失控停滞 / 🔴 方向漂移 / ⚪ 休眠），并撰写叙事：发生了什么、意味着什么、该怎么做。

**早朝简报升级** — 扁平的"领域状态"列表变为按战略线分组的战略概览，附带盲点检测和可操作建议：
- 🥇 最高杠杆行动（附工作量估算和不行动的代价）
- 🥈 值得关注
- 🟢 可安全忽略（主动抑制降低认知负荷）
- ❓ 需要决策（结构性缺口，由用户填补）

**跨层集成** — 战略地图与 SOUL、Wiki、DREAM 作为一个系统协同工作：
- SOUL × 战略：检查你的 driving_force 是否与表达的价值观一致
- Wiki × 流动：验证 cognition 流是否真正承载 wiki 知识（检测纸上流动）
- DREAM × 战略：REM 阶段使用流动图作为脚手架发现跨层洞察
- 行为模式 × 战略：标记行为与战略优先级矛盾的情况

**盲点检测** — 基于预测编码神经科学：系统主动寻找缺失的东西，而不仅仅是已有的东西。未归属的项目、断裂的流动、被忽视的 driving_force、缺失的生活维度、临近的时间窗口但没有准备。

### Agent 集成

| Agent | 如何使用战略地图 |
|-------|----------------|
| 早朝官 | 上朝时编译 STRATEGIC-MAP.md（步骤 8.5）。简报按战略线分组 |
| 丞相 | 用战略线术语构建跨项目问题。按角色推荐时间分配 |
| 中书省 | 存在流动时添加跨项目影响维度。标记 enabler 依赖风险 |
| 门下省 | 检查决策传播（下游影响）+ SOUL-战略对齐 |
| 兵部 | 按战略角色加权任务优先级。建议利用等待期 |
| 起居郎 | 检测新关系（Phase 2 候选）。更新 last_activity。DREAM REM 使用流动图脚手架增强 |

### 数据架构

- `_meta/strategic-lines.md` — 战略线定义（用户定义，类似 config.md）
- `projects/{p}/index.md` strategic 字段 — 项目级关系（类似现有的 status/priority 字段）
- `_meta/STRATEGIC-MAP.md` — 编译视图（类似 STATUS.md / wiki/INDEX.md — 禁止手动编辑）
- 认知管线：5 阶段 → 6 阶段（在 Associate 和 Emerge 之间新增"Strategize"）
- 遵循现有模式：单一事实源、outbox 合并、用户确认候选、从零生长

### 设计基础

基于认知科学研究：
- **目标系统理论**（Kruglanski 2002）— 双层意图（purpose vs driving_force）
- **识别启发式决策**（Klein 1998）— 原型匹配 + 叙事评估取代数字评分
- **预测编码**（Friston 2005）— 通过缺失监测实现盲点检测
- **控制期望值**（Shenhav et al. 2013）— 基于杠杆的行动建议，考虑工作量和机会成本
- **偏向竞争**（Desimone & Duncan 1995）— "可安全忽略"作为主动认知抑制

---

## [1.4.4b] - 2026-04-15 · 防止编造时间戳

> LLM 在生成 session-id 时编造时间戳而不读取系统时钟。所有 session-id 生成指令现在明确要求执行 date 命令。模板式规范改为命令式规范。

### 变更

- **qiju.md**：session-id 步骤从模板格式改为"执行 date 命令，使用真实输出。硬规则。"
- **data-layer.md + data-model.md**：session-id 生成同步更新为命令式措辞
- 所有变更同步至 EN/ZH/JA 三语

---

## [1.4.4a] - 2026-04-15 · 强制 Agent 文件加载

> LLM 在退朝时偷懒，不读 qiju.md 而凭记忆执行简化版流程。此补丁增加 3 层强制：SKILL.md 路由改为"必须读文件"、qiju.md 增加必填完成清单、编排准则新增第 6 条。

### 强制机制变更

- **SKILL.md**：上朝/退朝路由从"路由给 X"改为"必须读取 `pro/agents/X.md` 并以 subagent 方式启动。硬规则。"
- **qiju.md**：新增必填完成清单——每个 Phase 必须填入实际值（commit hash、Notion 同步状态等）。缺项 = 退朝未完成。
- **编排行为准则**：新增第 6 条——"触发词必须加载 agent 文件。禁止凭记忆执行角色而不读定义文件。硬规则。"

### 同日包含的审计修复

- zaochao.md git 健康检查：自动修复改为检测→汇报→确认（GLOBAL.md 安全边界 #1）
- GLOBAL.md："完整思考过程"改为"可发布的推理摘要"（跨模型兼容性）
- 14→16 subagent 数量修复
- AGENTS.md 死链 notion-schema.md 修复
- adapter-github.md：恢复命令改为 text 块 + 手动确认标注
- evals/run-eval.sh：退出码捕获、路径清洗、三语标题支持
- setup-hooks.sh：写文件前先做前置校验
- lifeos-version-check.sh：XDG 缓存路径、grep 版本解析

---

## [1.4.4] - 2026-04-14 · 起居郎——Session 关闭专家

> 早朝官拆分为两个角色：早朝官负责会话启动（读取），起居郎负责会话关闭（写入）。DREAM 融入起居郎——不再单独调用 agent。

### 📝 新角色：起居郎

以唐朝记录皇帝朝会言行的官员命名。当你说"退朝"时，起居郎负责一切：

- **Phase 1 — 归档**：decisions/tasks/journal → outbox
- **Phase 2 — 知识萃取**（核心职责）：扫描所有 session 素材提取 Session Candidate（wiki + SOUL）→ 用户当场确认
- **Phase 3 — DREAM**：3 天深度复盘 → DREAM Candidate（wiki + SOUL）→ 下次上朝确认
- **Phase 4 — 同步**：git push + Notion 同步（4 项具体操作）

### 关键改进
- 知识萃取是起居郎的核心使命——不再是 298 行文件中的 step 6.5
- DREAM 融入退朝流程——少一次 agent 调用，不再是"最后一步可选操作"
- Session 对话摘要传给起居郎——可从丞相直接处理的对话中提取知识
- Notion 同步显式保证——4 项具体写入，失败明确报告
- 16 角色（原 15）：早朝官 + 起居郎替代原来的合体角色
- `dream.md` 删除——完全融入 `qiju.md`

---

## [1.4.3e] - 2026-04-13 · SKILL.md 瘦身——纯路由文件

> SKILL.md 从 384 行压缩到 93 行。Lite Mode 移除。所有角色详细定义、输出格式和配置都已在 agent 文件和 reference 文档中。

### Token 节省
- **SKILL.md**：384 → 93 行（−291 行 ≈ −4,700 tokens/session）
- 移除：御史台/谏官/政事堂/早朝官详细描述、奏折格式、存储配置、Lite Mode 流程、两种审议辨析表、Pro Mode 安装详情
- 所有移除内容已存在于 agent 文件（`pro/agents/*.md`）或 reference 文件（`references/*.md`）

### 行为准则重新分配
- 丞相相关规则（8 条）留在 SKILL.md
- 编排规则（#2 封驳、#7 自动触发、#11 完整输出、#14 真 subagent、#9 降级）移至 `pro/CLAUDE.md` 新增"编排行为准则"段
- 通用 agent 规则已由 `pro/GLOBAL.md` 覆盖

### 六部按需启动
- `zhongshu.md`：新增"六部选择（硬规则）"——仅分配相关部门并注明理由
- `shangshu.md`：新增"仅分发已分配的部门（硬规则）"——不分发未分配的部门

### Lite Mode 移除
- Life OS 的核心价值是独立 subagent 的制衡——单上下文模拟违背了这一目的
- README 安装表：移除 Lite Mode 行，注明不支持单上下文平台

---

## [1.4.3d] - 2026-04-13 · 版本检测变为输出格式必填项

> 版本检测从独立指令（LLM 会跳过）变为朝前准备输出模板的必填字段（LLM 可靠地填写）。

- **版本显示变成模板字段**：`🏛️ Life OS: v[本地] | 最新: v[远程]`，更新方法内联显示
- **zaochao.md Mode 0 + Mode 1**：步骤 3 通过 WebFetch 获取远程版本；本地和远程版本都是必填输出字段
- **chengxiang.md**：朝前准备格式同步为相同的版本显示
- **SKILL.md**：删除冗长的版本自检段（已移至输出格式）
- 原理：LLM 可靠地填写输出模板（HARD RULE #13），即使跳过独立指令也会填

---

## [1.4.3c] - 2026-04-13 · 版本自检移至 SKILL.md

> 版本检测从 agent 文件移到 SKILL.md——每个 LLM 最先读取的文件。解决了旧版 agent 文件无法检测自身更新的自举悖论。

- **版本自检段**添加到 SKILL.md 顶部（丞相指令之前）：通过 WebFetch 检查远程版本，提示更新，报告失败
- **zaochao.md 简化**：Mode 0 和 Mode 1 的版本检查改为引用 SKILL.md，不再重复 WebFetch 逻辑
- 即使 zaochao.md 或其他 agent 文件过时也能工作——SKILL.md 总是最先被读取

---

## [1.4.3b] - 2026-04-13 · 退朝流程知识萃取

> Wiki 提取不再完全依赖 DREAM。退朝流程现在直接扫描 session 产出并在 DREAM 运行前向用户提出 wiki 候选。

- **退朝知识萃取（步骤 6.5）**：收朝和退朝模式现在扫描 session 产出中的可复用结论 → 向用户提出 wiki 候选 → 确认的条目写入 outbox wiki/
- **Outbox wiki 合并**：上朝合并现在处理 outbox 中的 wiki/ 文件 → 移动到 wiki/{domain}/{topic}.md
- **DREAM 去重**：DREAM N3 检查退朝流程是否已提取 wiki 候选（通过 manifest）→ 跳过重复提议，只关注遗漏的结论
- **Outbox 格式**：manifest.md 的 outputs 中新增 `wiki` 计数

---

## [1.4.3a] - 2026-04-13 · Wiki & SOUL 初始化引导

> 系统现在能检测到 wiki/ 和 SOUL.md 尚未初始化，并引导用户完成首次设置和旧格式迁移。

- **Wiki 首次初始化**：早朝官检测到空 wiki/ 或缺失 INDEX.md → 提议从已有 decisions/journal 提取结论
- **Wiki 旧格式迁移**：检测到旧格式 wiki 文件（无 front matter 的调研报告）→ 提议提取结论并归档原件
- **SOUL 引导启动**：SOUL.md 不存在时，DREAM 在首次退朝时从 user-patterns.md 提出初始条目
- **上朝检测**：步骤 5.5（SOUL 检查）和 10.5（wiki 健康检查）现在在晨报中报告初始化状态

---

## [1.4.3] - 2026-04-13 · Wiki 活化——知识管线终于跑通了

> 认知管线的"沉淀→涌现"阶段终于跑起来了。Wiki 从一个空目录变成了活跃的知识参与者。

### 📚 Wiki 规范（`references/wiki-spec.md`）

Wiki 本来就设计在第二大脑里，但从来没有接入任何工作流——没有 agent 写它，没有 agent 读它。现在四要素齐全：

- **谁写**：DREAM 在 N3 阶段提出 wiki 候选（与 SOUL 候选并行）
- **何时写**：每次退朝后，用户在下次上朝时确认
- **谁读**：丞相读取 wiki/INDEX.md，门下省检查一致性，御史台审计健康度
- **何时读**：每次会话开始、每次决策审议、每次巡查

### 🔍 丞相知识匹配

丞相现在在路由前扫描 wiki/INDEX.md。如果该领域存在高置信度条目："📚 该领域已有 N 条确立的结论。从已知知识出发，还是从头调研？"——用户同意时跳过重复分析。

### ⚖️ 门下省 Wiki 一致性检查

门下省现在检查新结论是否与已确立的 wiki 条目矛盾。如果检测到矛盾："⚠️ 此结论与 [wiki 条目]（confidence X）矛盾。"要么分析需要修正，要么 wiki 需要更新。

### 🔱 御史台 Wiki 健康审计

巡查现在覆盖 wiki 健康：confidence < 0.3 且 90 天以上未更新的条目（建议退役）、challenges > evidence 的条目（建议复查）、有决策记录但无 wiki 条目的领域（知识空白）。

### 📨 尚书省 Wiki 上下文

当丞相标记了相关 wiki 条目，尚书省在分发中包含它们："📚 已知前提——以此为起点，不要重新推导。"

### 🧠 认知管线重排

管线现在反映真实的信息流：`感知→捕获→判断→沉淀→关联→涌现`。沉淀分为 SOUL（人）和 Wiki（知识）。关联发生在丞相匹配新请求与 wiki 时。涌现发生在 DREAM 的 REM 阶段发现跨域连接时。

### 设计原则

不新增 agent，不新增流程。Wiki 插入已有节律：DREAM 写入 → 早朝官编译 INDEX → 丞相读取 → 门下省检查 → 御史台审计。

---

## [1.4.2] - 2026-04-12 · Outbox — 多 Session 并行零冲突

> 多个 session 现在可以同时在不同项目上工作。没有 git 冲突，没有锁。每个 session 退朝时写入自己的 outbox；下一个上朝的 session 负责合并所有 outbox。

### 📮 Outbox 架构

旧模型假设同一时间只有一个 session，用 `.lock` 文件警告并发。新模型拥抱并行：

- **每个 session 退朝时写入自己的隔离目录**（`_meta/outbox/{session-id}/`）— 决策、任务、日志、index delta、patterns delta、manifest
- **收尾和退朝期间不直接写共享文件** — `projects/`、`STATUS.md`、`user-patterns.md` 在合并前不会被触碰
- **合并发生在上朝时** — 下一个上朝的 session 扫描所有 outbox，按时间顺序合并到主结构，编译 STATUS.md，清理已合并的 outbox
- **session-id = `{platform}-{YYYYMMDD}-{HHMM}`**，在退朝时生成（不是 session 开始时）
- **零冲突保证** — 不同目录、不同文件、不会对同一路径并发写入
- **merge-lock** 兜底同时上朝的极端情况（< 5 分钟，自动清理）

### 覆盖场景

- 单 session 正常流程 ✅
- 多平台交替 ✅
- 多窗口并行 ✅
- 多台电脑 ✅
- session 跨越多天 ✅
- 同一 session 多次上朝退朝 ✅
- 空 session（无输出，不创建 outbox）✅
- push 失败（本地保存，下次重试）✅
- Lite 用户（无 second-brain，无 outbox）✅
- 手机 Notion 捕获（inbox/，不变）✅

### 改动文件

- `pro/agents/zaochao.md` — Mode 0/1 加 outbox 合并，Mode 3/4 改写 outbox
- `references/data-model.md` — 删除 session lock，新增 outbox 规则 + manifest/delta 格式
- `references/data-layer.md` — 目录结构 + Housekeeping/Wrap-Up 流程更新
- `references/adapter-github.md` — commit convention 改为 outbox 模式
- `SKILL.md` — 存储配置段新增并行 session 说明

---

## [1.4.1] - 2026-04-12 · SOUL + DREAM — 系统开始了解你是谁

> SOUL.md 从你的决策中生长，记录你是谁。DREAM 在你离开后处理记忆 — 就像大脑在睡眠中做的事。两者结合，给 Life OS 一个自我认知的反馈循环。

### 🔮 SOUL — 用户人格档案

你的价值观、信念和身份 — 以证据为基础的条目，从零开始生长。每条记录有两面：你实际做了什么（实然）和你希望怎样（应然）。两者的差距就是成长空间。

- **自然生长** — 从空白开始，随决策和行为积累
- **四个来源** — DREAM 发现、谏官观察、翰林院浮现、你直接写入
- **用户确认** — 系统提议，你决定。不自动写入
- **置信度缩放** — 新条目只影响谏官；深度验证的条目影响全系统
- **每个角色读法不同** — 丞相问更精准的问题，中书省加相关维度，门下省查价值一致性，谏官做行为审计，翰林院匹配思想家

### 💤 DREAM — AI 睡眠周期

每次退朝后系统"入睡" — 灵感来自人类睡眠架构：

- **N1-N2（整理）** — 分类信箱、标记过期任务、发现孤立文件
- **N3（固化）** — 提炼反复主题为 wiki、更新行为模式、提出 SOUL 候选
- **REM（连接）** — 发现跨领域关联、检查价值行为一致性、生成意想不到的洞察
- **范围**：仅最近 3 天。梦境报告存储在 `_meta/journal/`，下次上朝呈现
- **新 agent**：`pro/agents/dream.md`

### 📐 新参考文件

- `references/soul-spec.md` — SOUL 格式、生命周期、置信度计算、各角色使用规则
- `references/dream-spec.md` — DREAM 触发、三阶段、输出格式、约束

---

## [1.4.0] - 2026-04-12 · 人类智慧殿堂 + 三省深挖 + 单一事实源

> 一句话：翰林院进化为人类智慧殿堂；五个核心角色全面强化；修复了 STATUS.md 与 index.md 版本漂移的架构级 bug — index.md 是唯一权威源，STATUS.md 从它编译。

### 🏗️ 架构修复 — 单一事实源

`projects/{p}/index.md` 现在是项目版本、阶段、状态的唯一权威源。`_meta/STATUS.md` 从 index.md 编译生成，禁止手写。修复了 STATUS.md 和 index.md 版本号不一致的 bug。御史台巡检新增版本一致性 lint 规则。

### 🎋 翰林院 → 人类智慧殿堂

翰林院不再只是"第一性原理 + 苏格拉底 + 奥卡姆剃刀"。现在你可以和苏格拉底聊人生，和马斯克拆解商业逻辑，让老子和尼采辩论人生意义。

- **18 个领域、70+ 位思想家** — 从科学到哲学，从东方思想到法律正义，覆盖人类文明的全部重要维度
- **深度角色扮演** — 不是"用苏格拉底的方法"，而是苏格拉底本人在和你对话。他的口吻、他的案例、他的追问方式
- **三种对话模式** — 单人深谈（一对一探索）、圆桌会议（多位思想家各抒己见）、辩论（正反交锋）
- **独立 subagent** — 每位思想家运行在独立的 context 中，翰林院本身担任主持人
- **结尾仪式** — 思想家临别赠言 → 翰林院总结你的思路变化 → 存入 second-brain

### 🔍 门下省 — 从"走过场"到"真正的最后防线"

- **10/10/10 悔恨测试** — 10 分钟后、10 个月后、10 年后，三个时间尺度必须分别回答，不接受笼统的"不会后悔"
- **红队审查** — 假设计划一定会失败，找出最脆弱的假设、最依赖运气的环节、最被刻意淡化的风险
- **否决格式结构化** — 否决不再只是一句"不通过"，必须说清哪个维度不行、问题本质是什么、具体怎么改

### 🏛️ 政事堂 — 从"模糊触发"到"量化规则 + 结构化辩论"

- **量化触发** — 两部评分差 ≥ 3 分，或一部说做一部说不做，自动触发朝堂议政
- **新建独立 agent** — `zhengshitang.md`，3 轮结构化辩论：陈述 → 交锋 → 最终立场 → 裁决
- **尚书省主持，用户裁决** — 辩论有规则、有字数限制，不会变成独白

### 📨 尚书省 — 从"分配任务"到"智能调度"

- **依赖检测** — 自动识别"户部的结论影响兵部的方案"这类跨部门依赖，先跑 A 组再跑 B 组
- **咨询机制** — 兵部可以问"户部给我一个数字：可用资金是多少？"，尚书省中转，不暴露完整报告

### 🏛️ 丞相 — 意图澄清分类化

- **五类分类策略** — 决策类（判断标准？约束？）、规划类（目标？资源？）、困惑类（情绪？真正困扰？）、复盘类（标准？维度？）、信息类（直接处理）
- **情绪分离协议** — 情绪和决策混在一起时，先一句话回应情绪，再分离事实

### 💬 谏官 — 从"观察"到"学习"

- **行为模式学习循环** — 每次发现新模式或模式变化，标记并写入 user-patterns.md
- **跨会话趋势分析** — 对比近 3 次报告：风险偏好、决策速度、执行力、关注维度的变化趋势
- **正向强化** — 不只说哪里不好。上次建议"要更果断"，这次做到了，必须明确表扬

### ⚖️ 系统级

- **"两种议"对比表** — SKILL.md 新增政事堂 vs 翰林院的区别：一个辩"该不该做"，一个探"你是谁"
- **丞相路由规则** — 数据矛盾走政事堂，价值迷茫走翰林院

---

## [1.3.1] - 2026-04-12 · 过程必须可见

> 一句话：强制所有 subagent 展示完整思考过程，Pro 模式必须启动真实 subagent。

- **emoji 强制** — 所有 subagent 输出必须带 🔎/💭/🎯 标记，省略即违规
- **真实 subagent 强制** — Pro 环境下每个角色必须是独立 agent 调用，禁止单 context 模拟
- **角色边界锁定** — 行为准则 #17：只有 15 个已定义角色，禁止脑补通政使司、大理寺等系统外官职
- **inbox 归丞相** — 丞相正式接管信箱管理
- **上朝自动更新** — 早朝官检查 GitHub 版本，发现新版自动执行平台更新命令
- **git 健康检查** — 上朝前检查 worktree 残留和 hooksPath 断链
- **ko/es 移除** — 韩语和西班牙语占位符删除，保留 EN/ZH/JA
- **tag 清理** — 13 个旧 tag → 5 个正确的 Strict SemVer tag
- **second-brain 整理** — 模板补齐 front matter，旧目录（gtd/records/zettelkasten）删除

---

## [1.3.0] - 2026-04-10 · 三平台 Pro Mode + 存储抽象层

> 一句话：Life OS 从 Claude Code 专属扩展为 Claude + Gemini + Codex 三平台 Pro Mode，数据存储从 Notion 硬编码改为可插拔的三后端架构。

### 存储抽象层

一套标准数据模型（6 种类型、7 种操作），三个可选后端（GitHub / Google Drive / Notion），用户选哪个就加载哪个 adapter。多后端时自动同步，冲突时 last-write-wins 或询问用户。

### 跨平台 Pro Mode

14 个 agent 定义共用，编排文件分平台：`CLAUDE.md`（Claude Code）、`GEMINI.md`（Gemini CLI / Antigravity）、`AGENTS.md`（Codex CLI）。每个平台自动使用最强模型，无硬编码。

### 触发词标准化

英文 / 中文 / 日文三语触发词正式定义，解决了 Claude 和 Codex 在"上朝"时行为不一致的问题。

---

## [1.2.0] - 2026-04-08 · 国际化 + 架构整合

> 一句话：全部 34 个文件翻译为英文（主版本），中文和日文完整翻译，系统架构大幅整合。

### 国际化

英文成为主版本，中文和日文作为 i18n 翻译。README 重新设计，加入 shields.io 徽章和视觉层次。

### 架构整合

- **pro/GLOBAL.md** — 14 个 agent 的通用规则提取为单一权威源，每个 agent 文件精简 30%
- **认知管线** — 五阶段信息流：感知 → 捕获 → 关联 → 判断 → 沉淀 → 涌现
- **御史台巡检模式** — 决策审查之外的第二种运行模式，六部各自巡查自己在 second-brain 中的辖区
- **知识提取四步训练** — 用户决定 → 积累样本 → LLM 归纳规则 → 定期纠偏

### 🔴 破坏性变更

第二大脑目录重构：`zettelkasten/` → `wiki/`，`records/` → `_meta/journal/`，新增 `_meta/` 系统元数据层。

---

## [1.1.1] - 2026-04-05 · 数据层转型

> 一句话：GitHub second-brain 取代 Notion 成为数据主库，Notion 降级为手机端工作内存。

- **GitHub 为主库** — .md + front matter，融合 GTD + PARA + Zettelkasten
- **早朝官三模式** — 家务（自动）、审视（用户触发）、收尾（流程后）
- **会话绑定** — 每次会话锁定一个 project/area，所有读写限定范围
- **退朝指令** — push 到 GitHub + 刷新 Notion
- **CC 强制 Pro** — 检测到 Claude Code 必须启动独立 subagent

---

## [1.1.0] - 2026-04-04 · 文档 + 研究过程 + 记忆层

> 一句话：完整的文档体系上线，所有 agent 获得研究过程展示能力，丞相获得记忆层和思维工具。

- **多平台安装指南** — 7 个平台的详细步骤
- **全 14 个 agent 加入 🔎/💭/🎯 研究过程展示**
- **谏官 21 条观察能力** — 认知偏差、情绪检测、行为追踪、决策质量
- **丞相意图澄清** — 上报前 2-3 轮对话，不再直接升报
- **早朝指标仪表盘** — DTR / ACR / OFR + 4 个周度指标
- **12 个标准场景配置** — 覆盖职业、投资、搬迁、创业等主要决策场景

---

## [1.0.0] - 2026-04-03 · 初始发布

> 一句话：三省六部制个人内阁系统正式发布。15 个角色，制衡与分权。

- 15 个角色：丞相 + 三省 + 六部 + 御史台 + 谏官 + 政事堂 + 早朝官 + 翰林院
- Lite 模式（单 context）+ Pro 模式（14 独立 subagent）
- 10 个标准场景配置
- 六部 × 四司详细职能定义
- Apache-2.0 License
