# Wiki 规范

Wiki 是系统的知识档案——一个持续生长的、关于世界的可复用结论集合。它位于 second-brain 的 `wiki/` 目录。

## 定位

| 存储 | 记录什么 | 示例 |
|------|---------|------|
| `decisions/` | 你决定了什么（具体、带时间戳） | "2026-04-01：决定用信托结构" |
| `user-patterns.md` | 你做什么（行为模式） | "倾向于回避财务维度" |
| `SOUL.md` | 你是谁（价值观、人格） | "风险偏好：中高" |
| `wiki/` | 你知道什么（可复用结论） | "日本 NPO 放贷没有貸金業法豁免" |

**SOUL 管的是人，Wiki 管的是知识。两者不能混用。**

---

## 核心原则

1. **从零生长**——wiki/ 从空开始，不需要预初始化
2. **基于证据**——每条条目链接到支持它的决策/经验
3. **在严格条件下自动写入**——wiki 条目由 archiver 和 DREAM 在满足严格标准时自动创建；用户通过删除来调整（删除文件 = 退役；说 "undo recent wiki" = 回滚）
4. **标题 = 结论**——每个条目的标题必须是结论本身，而不是话题
5. **一个文件一个结论**——不做多话题合辑

---

## 自动写入标准（6 条规则）

每个候选结论在自动写入前都必须通过 6 条标准。任何一条失败 → 丢弃，不写入低置信度条目。

1. **跨项目可复用**——结论在观察它的会话以外的项目/领域也有用
2. **关于世界、不是关于你**——事实、规则、方法。不是价值观或个人偏好（那是 SOUL 的事），不是行为模式（那是 user-patterns.md 的事）
3. **零个人隐私**——无姓名、金额、账号、ID、特定公司、家人朋友信息、或可追溯的日期+地点组合。若结论离开这些内容就失去意义 → 它就不是 wiki 素材，跳过
4. **事实或方法**——描述"发生了什么"或"如何做 X"，而非感受或意见
5. **多证据点（≥2 条独立）**——至少 2 个案例、数据点、决策或引用。单次观察丢弃（那属于日志，不属于 wiki）
6. **不与既有 wiki 冲突**——如果新结论与既有条目冲突 → 给那条既有条目 `challenges: +1`，而**不是**另起一条竞争条目

**初始置信度**（通过全部 6 条后）：
- 3+ 独立证据 → `confidence: 0.5`
- 恰好 2 条证据 → `confidence: 0.3`
- 1 条或以下 → **丢弃**（违反第 5 条）

**隐私过滤器**——每次写入前应用：
- 去除姓名（除非是与结论直接相关的公众人物）
- 去除具体金额、账号、ID
- 去除具体公司名（除非是公开案例）
- 去除家人朋友引用
- 去除可追溯的日期+地点组合
- 若过滤后结论失去意义 → 丢弃（它本就不是可复用的，只是穿着知识外衣的个人笔记）

---

## 用户事后介入

用户不预先批准 wiki 条目，而是事后调整：

- 删除 `wiki/{domain}/{topic}.md` → 退役条目
- 在会话中说 "undo recent wiki" → archiver（下次调用时）回滚最近一次自动写入
- 手动编辑置信度以抑制（设为 0 或 <0.3）→ 条目保留但不被引用

---

## 条目格式

每个 wiki 条目是独立的 markdown 文件：

```yaml
---
domain: "[domain 名]"       # finance / startup / health / legal / tech / 项目名...
topic: "[短标识]"
confidence: 0.0               # 0-1，自动计算
evidence_count: 0             # 支持的决策/经验数
challenges: 0                 # 相反的经验数
source: dream                 # dream / session / user
created: YYYY-MM-DD
last_validated: YYYY-MM-DD
---
```

### Conclusion
[一句话——可复用的要点]

### Reasoning
[支持这个结论的证据和逻辑]

### Applicable When
[什么场景下应该想起这个条目]

### Source
[产生这份知识的具体决策、会话或经验]

---

## 标题约定

标题必须是结论，而不是话题：

- ✅ "NPO lending in Japan has no 貸金業法 exemption"
- ❌ "NPO 貸金業法 research"
- ✅ "MVP validates demand, not product quality"
- ❌ "MVP methodology notes"
- ✅ "16:8 intermittent fasting works well for me"
- ❌ "Intermittent fasting research"

打开文件就直接告诉你答案——不需要把正文全部读完。

---

## 文件路径约定

```
wiki/{domain}/{topic}.md
```

示例：
- `wiki/finance/lending-law-npo.md`
- `wiki/startup/mvp-validation.md`
- `wiki/health/intermittent-fasting.md`
- `wiki/startup/biz-plan-versions.md`

---

## 置信度计算

与 SOUL.md 公式相同：

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| 置信度 | 含义 | 系统行为 |
|--------|------|---------|
| < 0.3 | 暂定，数据少 | INDEX 中可见但不在路由时引用 |
| 0.3 – 0.6 | 证据中等 | REVIEWER 在一致性检查时引用 |
| 0.6 – 0.8 | 已确立 | ROUTER 告知用户"已有相关知识" |
| > 0.8 | 深度验证 | 全系统引用——可加速决策路由 |

---

## 条目生命周期

```
1. ✅ 自动写入——archiver（Phase 2）或 DREAM（N3）通过全部 6 条标准 → 直接写入 wiki/{domain}/{topic}.md
2. 📈 加强——累积更多证据（evidence_count 上升，置信度提高）
3. ⚠️ 被质疑——检测到相反经验（challenges 上升，置信度下降）
4. 🔄 修订——用户基于新证据更新结论
5. 🗑️ 被调整出——用户手动删除文件（= 退役）或在会话中说 "undo recent wiki"（archiver 回滚最近的自动写入）
6. 🗄️ 退役——移入 wiki/_archive/（低置信 + 90+ 天无活动，或用户删除）
```

---

## Wiki INDEX

`wiki/INDEX.md` 是所有 wiki 条目的编译摘要。RETROSPECTIVE 在每次 Start Court 时从实际 wiki/ 文件编译。

### 格式

```markdown
# Wiki Index
compiled: YYYY-MM-DD

## Finance
- NPO lending has no 貸金業法 exemption (0.95) → wiki/finance/lending-law-npo.md
- NPO tax deduction conditions (0.82) → wiki/finance/npo-tax-deduction.md

## Startup
- MVP validates demand, not product (0.88) → wiki/startup/mvp-validation.md
- Business plan: internal vs external versions differ fundamentally (0.72) → wiki/startup/biz-plan-versions.md

## Health
- 16:8 intermittent fasting works for me (0.80) → wiki/health/intermittent-fasting.md
```

每行 ≤ 80 字符。整个 INDEX 通常是 20-100 行——加载成本极低。

**INDEX.md 是编译产物**——从不手工编辑。它从 wiki/ 文件重新生成。

---

## 四种来源

| 来源 | 如何产生 | 时机 |
|------|---------|------|
| **DREAM** | N3 阶段从 3 天活动中发现可复用结论 | 每次 Adjourn Court 后 |
| **会话** | 在 Draft-Review-Execute 工作流中，某个部门产生可复用发现 | 标记 `wiki_candidate: true` 的日志条目 |
| **用户** | 任意时刻直接输入 | "记住这个事实：X" |

---

## Wiki 候选格式

当 archiver 或 DREAM 发现值得记录的知识**且**通过全部 6 条自动写入标准时，条目直接写入（无需候选确认）。内部评估使用的候选结构：

```
📚 Wiki Auto-Write (internal):
- Domain: [domain 名]
- Topic: [短标识]
- Conclusion: [一句话——可复用的要点]
- Evidence:
  - [日期] [决策/行为] — [描述]
  - [日期] [决策/行为] — [描述]
- Applicable when: [什么场景下想起它]
- Criteria check: [6/6 通过 或 X/6 → 丢弃原因]
- Privacy filter: [去除了什么，或 "nothing to strip"]
```

通过 6/6 → 直接写入 `wiki/{domain}/{topic}.md`。否则 → 丢弃，理由记入 Completion Checklist。

---

## 各角色如何使用 Wiki

所有角色在引用 wiki/INDEX.md 前都先检查它是否存在。如果不存在或为空，角色正常运行，不使用 wiki 输入。

| 角色 | 读取内容 | 使用方式 |
|------|---------|---------|
| **ROUTER** | wiki/INDEX.md（完整索引） | 扫描 domain 匹配——若存在高置信条目，告知用户"我们已经知道 X"并提议跳过冗余研究 |
| **DISPATCHER** | 相关 wiki 条目（ROUTER 传入） | 在派遣上下文中包含"已知前提——从这里开始" |
| **六领域** | dispatch 上下文中的 wiki 条目 | 从既有结论开始分析，而非从零 |
| **REVIEWER** | wiki/INDEX.md | 一致性检查——标记新结论与既有高置信 wiki 条目的冲突 |
| **AUDITOR** | wiki/ 目录（巡检时） | wiki 健康审计——过期条目、矛盾、知识缺口 |
| **DREAM** | wiki/INDEX.md + wiki/ 条目 | N3：提议新候选 + 更新既有条目的证据/矛盾计数。REM：用 wiki 作素材做跨域关联 |
| **RETROSPECTIVE** | wiki/ 目录 | 在 Start Court 编译 INDEX.md。若上次会话用户说过 "undo recent wiki"，在简报中提示 |

---

## Wiki 在 second-brain 中的位置

```
second-brain/
├── SOUL.md              ← 你是谁（人格）
├── user-patterns.md     ← 你做什么（行为）
├── wiki/                ← 你知道什么（知识）
│   ├── INDEX.md         ← 编译摘要（自动生成）
│   ├── finance/
│   │   ├── lending-law-npo.md
│   │   └── npo-tax-deduction.md
│   ├── startup/
│   │   └── mvp-validation.md
│   ├── health/
│   │   └── intermittent-fasting.md
│   └── _archive/        ← 退役条目
├── inbox/
├── _meta/
├── projects/
├── areas/
└── archive/
```

---

## 首次初始化

当 RETROSPECTIVE 检测到 wiki/ 为空或缺少 INDEX.md：

1. 在简报中报告："📚 Wiki is not yet initialized. Would you like to bootstrap from existing decisions?"
2. 若用户同意：
   a. 扫描 `decisions/` 和 `_meta/journal/` 寻找可提取结论（同 DREAM N3 Q2 逻辑）
   b. 对每个候选应用 6 条自动写入标准 + 隐私过滤器
   c. 所有通过的候选自动写入 `wiki/{domain}/{topic}.md` 并附正确 frontmatter
   d. 编译 `wiki/INDEX.md`
   e. 报告："Auto-wrote N entries, discarded M (reasons: ...). Delete any file you disagree with."
3. 若用户拒绝 → 跳过，下次 Start Court 再提醒

**只触发一次**。INDEX.md 存在后就交由正常 wiki 流程接管。

---

## 遗留迁移

当 wiki/ 中有不符合当前规范格式的文件（无 frontmatter、无 domain 子目录、标题≠结论）时：

1. 在简报中报告："📚 Found N legacy wiki files not matching current spec. Migrate?"
2. 若用户同意：
   a. 读取每个遗留文件
   b. 每个文件抽取 1-3 条可复用结论
   c. 对每条抽取的结论应用 6 条标准 + 隐私过滤器
   d. 通过的结论自动写入 `wiki/{domain}/{topic}.md`
   e. 原文件移至 `wiki/_archive/`（保留，不删除）
   f. 重新编译 INDEX.md
   g. 报告："Migrated N entries, discarded M (reasons: ...). Delete any file you disagree with."
3. 若用户拒绝 → 保持原样，不阻塞正常流程

wiki/ 根目录下没有 frontmatter 的遗留文件会被 INDEX.md 编译忽略。

---

## 约束清单

- **仅当 6 条标准全部通过时自动写入**——低于此的候选丢弃，不写入低置信度条目
- **每次写入前应用隐私过滤器**——姓名、金额、ID、特定公司、家人朋友引用、可追溯的日期+地点组合要被去除；若去除后失去意义则丢弃
- **用户事后介入，不预先批准**——删除文件退役；说 "undo recent wiki" 回滚；将置信度设为 <0.3 抑制但不删除
- **INDEX.md 是编译产物，不是手工编辑**——在每次 Start Court 从 wiki/ 文件重新生成
- **一个文件一个结论**——不做"话题合辑"文件
- **标题 = 结论**——打开文件就看到答案
- **wiki 内部无交叉引用**——每条条目自成一体
- **简洁**——wiki 条目应是 10-30 行，不是研究报告
