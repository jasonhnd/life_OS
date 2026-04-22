# Wiki 条目格式

> 每个 wiki 条目都是一个独立的 markdown 文件，遵循固定的 YAML frontmatter + 正文结构。本文详解字段、INDEX.md 结构、生命周期、confidence 更新规则。

## 文件路径

```
wiki/{domain}/{topic}.md
```

例：
- `wiki/finance/lending-law-npo.md`
- `wiki/startup/mvp-validation.md`
- `wiki/health/intermittent-fasting.md`

`{domain}` 是领域分类（`finance` / `startup` / `health` / `legal` / `tech` / 或具体项目名）。

`{topic}` 是短标识符，用连字符连接单词，全小写。这是**文件名**，不是标题——标题（= 结论）在文件内容里。

---

## 完整 Schema

```yaml
---
domain: "finance"
topic: "lending-law-npo"
confidence: 0.95
evidence_count: 6
challenges: 0
source: session
created: 2025-11-20
last_validated: 2026-04-18
---

# 日本 NPO 贷款无贷金业法豁免

### Conclusion
即使以 NPO 形式运营的贷款业务，在日本仍需完整遵守贷金业法，没有豁免条款。

### Reasoning
- 贷金业法适用于"作为业务的贷款"，不论组织形式
- NPO 法人格不改变金融监管归属
- 金融厅在 2023 年和 2024 年两次明确回答类似询问

### Applicable When
- 设计以 NPO 为载体的金融服务
- 评估社会企业的贷款方案
- 计算小额贷款业务的合规成本

### Source
- 2025-11-20 NPO 项目法律评估 session
- 2026-02-14 社会企业架构讨论
- 2026-04-01 金融厅回函研究
```

---

## 字段详解

### `domain`（必填）

领域分类。用来在 INDEX.md 中分组展示，决定文件放在 `wiki/` 下哪个子目录。

常见 domain 值：
- `finance` / `legal` / `tech` / `health` / `startup` / `product`
- 具体项目名，例如 `life-os` / `project-foo`

不强制预定义——你或系统可以自由创建新 domain。但建议命名保持一致（都小写，英文，单数）。

### `topic`（必填）

文件名的主体部分，短标识符。

原则：
- 全小写，英文
- 单词之间用连字符 `-`
- 尽量短但能唯一识别

例：
- ✅ `lending-law-npo` / `mvp-validation` / `biz-plan-versions`
- ❌ `Lending_Law_NPO`（大小写和下划线）
- ❌ `how-to-do-mvp-validation-for-startups`（太长）

### `confidence`（自动计算）

0 到 1 之间。**你不管理**。

计算公式（和 SOUL 一样）：

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

### `evidence_count` / `challenges`

- `evidence_count`：支持该结论的证据数（决策、经验、参考资料）
- `challenges`：矛盾该结论的证据数

archiver 和 DREAM 在扫描时自动维护这两个字段。

### `source`

条目来源：

| 值 | 含义 |
|----|------|
| `dream` | DREAM N3 阶段发现 |
| `session` | archiver Phase 2 从单次 session 抽取 |
| `user` | 用户直接添加 |

用于追溯。系统不根据 source 做差别对待。

### `created` / `last_validated`

- `created`：首次写入的日期
- `last_validated`：最近一次被新证据或挑战激活的日期

`last_validated` 超过 180 天没更新 → AUDITOR 巡检时标记"过时候选"，建议你审视是否还成立。

---

## 正文结构（4 个固定段）

### Conclusion

**一句话**。就是标题的详细版本。

- ✅ "即使以 NPO 形式运营的贷款业务，在日本仍需完整遵守贷金业法，没有豁免条款。"
- ❌ 长段落（放到 Reasoning）

### Reasoning

支撑结论的证据和逻辑。**简洁**——2-5 条要点，每条 1-2 行。

不是研究报告——是结论的快速佐证。如果你想写长文，那属于 journal 或 decisions，不属于 wiki。

### Applicable When

在什么场景应该想起这个条目。给未来的你一个**召唤提示**。

例：
- "设计以 NPO 为载体的金融服务"
- "评估社会企业的贷款方案"

这一段对 ROUTER 和 DISPATCHER 特别重要——他们判断某条目是否和当前问题相关时，主要看这一段。

### Source

产出这个知识的决策、session、或经验。用日期 + 简短描述即可。

不需要详细链接（wiki 是独立的，每个条目 self-contained）。如果你想追溯具体 session，可以在 decisions/ 或 journal 里找。

---

## 整个条目应该有多长？

**10-30 行**。不是研究报告。

如果你发现一个条目写到了 50+ 行，问自己：
- 是一个结论还是多个？（如果多个，拆成多个文件）
- Reasoning 是否太冗长？（浓缩成要点）
- 是不是把 journal 当 wiki 写了？（journal 记录过程，wiki 只记录结论）

---

## INDEX.md 结构

`wiki/INDEX.md` 是**编译产物**——RETROSPECTIVE 在每次 Start Session 从 wiki/ 目录下所有带 front matter 的文件生成。

格式：

```markdown
# Wiki Index
compiled: 2026-04-18

## Finance
- NPO 贷款无贷金业法豁免 (0.95) → wiki/finance/lending-law-npo.md
- NPO 税收减免的 3 个条件 (0.82) → wiki/finance/npo-tax-deduction.md

## Startup
- MVP 验证需求，不是产品 (0.88) → wiki/startup/mvp-validation.md
- 商业计划书内外版本根本不同 (0.72) → wiki/startup/biz-plan-versions.md

## Health
- 16:8 间歇性断食对我有效 (0.80) → wiki/health/intermittent-fasting.md
```

规则：
- **按 domain 分组**，字母顺序
- **组内按 confidence 降序**
- **每行 ≤ 80 字符**（保证轻量）
- **标题就是结论**（取自文件的 `# Title`）
- **不手动编辑**——你的改动会被下次编译覆盖

INDEX.md 典型 20-100 行。加载成本极低。

---

## 生命周期

```
1. ✅ 自动写入 — archiver Phase 2 或 DREAM N3 通过 6 条标准 + 隐私过滤
2. 📈 强化 — 更多证据积累（evidence_count 上升，confidence 上升）
3. ⚠️ 挑战 — 矛盾经验检测到（challenges 上升，confidence 下降）
4. 🔄 修订 — 用户根据新证据更新结论
5. 🗑️ 用户删除 — 手动删除文件（= 废弃）或说"undo recent wiki"（回滚最近的写入）
6. 🗄️ 归档 — 低 confidence + 90+ 天无活动，或用户删除 → 移到 wiki/_archive/
```

### 自动写入

经过 6 条标准 + 隐私过滤，archiver 写到 `_meta/outbox/{session_id}/wiki/{domain}/{topic}.md`。session 结束 git push 后，下次 Start Session RETROSPECTIVE 会把 outbox 的 wiki 文件移到正式的 `wiki/{domain}/`。

### 强化

每次 session 中 archiver 或 DREAM 发现新证据支持已有条目 → `evidence_count +1`，`last_validated` 更新为今天，confidence 自动重算。

### 挑战

发现矛盾证据 → `challenges +1`，confidence 下降。

### 修订

你自己打开文件修改 Conclusion 或 Reasoning。系统下次读时用新版本。

如果修订后结论变化很大（比如从"X 有效"改成"X 有条件有效"），建议：
- 把修订前的 evidence_count 保留（那些证据仍然支持某种程度的结论）
- 把 challenges 清 0 或部分清（因为结论已经吸纳了矛盾）
- 手动调整一次 confidence（之后系统会接管）

### 删除

直接删除文件。下次编译 INDEX 时就少一条。

或者说"undo recent wiki"一次性回滚最近 session 的自动写入（用于不认可本次产出时）。

### 归档

AUDITOR 巡检时发现条目 confidence < 0.3 且 90+ 天无活动 → 建议归档。归档是把文件从 `wiki/{domain}/` 移到 `wiki/_archive/{domain}/`。归档条目不参与 INDEX 编译，不被任何角色引用，但保留记录。

---

## confidence 更新规则

每次 archiver 或 DREAM 扫描时对每个 wiki 条目评估：

| 情况 | 操作 |
|------|------|
| 本 session 新证据支持该条目 | `evidence_count +1`，`last_validated` = today |
| 本 session 证据矛盾该条目 | `challenges +1`，`last_validated` = today |
| 本 session 和该条目无关 | 不变 |

然后自动重算 confidence。

**特殊**：如果本 session 产出的结论已被现有条目覆盖，不创建新条目，而是给旧条目 `evidence_count +1`。

---

## 领域组织的建议

不要让 domain 过于细碎。理想状态：

- 3-10 个 domain，每个 domain 3-20 个条目
- 单个 domain 超过 20 个 → 考虑拆分
- 单个 domain 只有 1-2 个 → 考虑合并到相关 domain

例：
- ❌ 分 `finance-personal`、`finance-business`、`finance-npo` 三个 domain → 都归 `finance`，在 topic 里区分
- ✅ 分 `finance` 和 `legal` → 即使有交叉内容，分开可以让结论定位更快

**domain 是查找工具，不是精确分类**。让它帮你快速找，不让它成为负担。

---

## 自检清单

定期看 wiki 时问自己：

- [ ] 每个条目的标题都是**结论**而不是话题？
- [ ] 没有"话题汇总"文件（一个文件多个结论）？
- [ ] 每个条目长度 10-30 行？
- [ ] INDEX.md 是否最近编译过（`compiled:` 字段日期 ≤ 7 天前）？
- [ ] 有没有长期 confidence 低的僵尸条目？（建议归档）
- [ ] 有没有 What IS/SHOULD BE 误入 wiki（那是 SOUL 的事）？
- [ ] 有没有个人隐私细节漏过了隐私过滤？（如有，立即修订或删除）

这些是 AUDITOR 巡检时会看的点，你自己偶尔扫一遍也可以。
