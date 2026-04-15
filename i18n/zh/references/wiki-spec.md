# Wiki 规范

Wiki 是系统的知识档案 -- 一个关于世界的可复用结论的活跃集合。它位于 second-brain 的 `wiki/` 目录下。

## 定位

| 存储 | 记录什么 | 示例 |
|---------|----------------|---------|
| `decisions/` | 你决定了什么（具体的、带时间戳的） | "2026-04-01: 决定使用信托结构" |
| `user-patterns.md` | 你做了什么（行为模式） | "倾向于回避财务维度" |
| `SOUL.md` | 你是谁（价值观、性格） | "风险偏好：中高" |
| `wiki/` | 你知道什么（可复用结论） | "日本NPO融资不享有貸金業法豁免" |

SOUL 管理人格。Wiki 管理知识。两者不可混淆。

---

## 原则

1. **从零开始增长** -- wiki/ 初始为空。无需初始化。
2. **基于证据** -- 每条记录链接到支持它的决策/经历。
3. **用户确认** -- 系统提出候选，用户确认。不会自动写入。
4. **标题 = 结论** -- 每条记录的标题必须是结论本身，而非话题。
5. **每文件一条结论** -- 不做多主题汇编。

---

## 条目格式

每条 wiki 条目是一个独立的 markdown 文件：

```yaml
---
domain: "[领域名称]"       # finance / startup / health / legal / tech / project-name...
topic: "[简短标识符]"
confidence: 0.0               # 0-1，自动计算
evidence_count: 0             # 支持性决策/经历数量
challenges: 0                 # 矛盾经历数量
source: dream                 # dream / session / user
created: YYYY-MM-DD
last_validated: YYYY-MM-DD
---
```

### Conclusion
[一句话 -- 可复用的结论]

### Reasoning
[支持此结论的证据与逻辑]

### Applicable When
[在什么场景下应调用此条目]

### Source
[哪个决策、会话或经历产生了此知识]

---

## 标题规范

标题必须是结论，而非话题：

- ✅ "日本NPO融资不享有貸金業法豁免"
- ❌ "NPO 貸金業法 调研"
- ✅ "MVP 验证的是需求，不是产品质量"
- ❌ "MVP 方法论笔记"
- ✅ "16:8 间歇性断食适合我"
- ❌ "间歇性断食研究"

打开文件即可立即获得答案 -- 无需阅读全文。

---

## 文件路径规范

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

与 SOUL.md 使用相同的公式：

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| 置信度 | 含义 | 系统行为 |
|------------|---------|-----------------|
| < 0.3 | 初步，数据点较少 | 在 INDEX 中可见，但路由时不被引用 |
| 0.3 – 0.6 | 中等证据 | REVIEWER在一致性检查时引用 |
| 0.6 – 0.8 | 已充分建立 | ROUTER告知用户已有的知识 |
| > 0.8 | 深度验证 | 全系统引用 -- 可加速决策路由 |

---

## 条目生命周期

```
1. 🌱 候选 -- DREAM 在 N3 阶段提出，或在会话中提取
2. ✅ 确认 -- 用户在早朝时批准（可编辑措辞）
3. 📈 强化 -- 更多证据积累（evidence_count 上升，confidence 增加）
4. ⚠️ 受到挑战 -- 检测到矛盾经历（challenges 增加，confidence 下降）
5. 🔄 修订 -- 用户根据新证据更新结论
6. 🗄️ 退役 -- 移至 wiki/_archive/（低置信度 + 90天以上无活动）
```

---

## Wiki INDEX

`wiki/INDEX.md` 是所有 wiki 条目的编译摘要。RETROSPECTIVE在每次早朝时从实际的 wiki/ 文件编译生成。

### 格式

```markdown
# Wiki Index
compiled: YYYY-MM-DD

## Finance
- 日本NPO融资不享有貸金業法豁免 (0.95) → wiki/finance/lending-law-npo.md
- NPO税收减免条件 (0.82) → wiki/finance/npo-tax-deduction.md

## Startup
- MVP验证的是需求，不是产品 (0.88) → wiki/startup/mvp-validation.md
- 商业计划：内部版与外部版本质不同 (0.72) → wiki/startup/biz-plan-versions.md

## Health
- 16:8间歇性断食适合我 (0.80) → wiki/health/intermittent-fasting.md
```

每行不超过 80 字符。整个 INDEX 通常 20-100 行 -- 加载成本极低。

**INDEX.md 是编译产物** -- 永远不要手动编辑它。它从 wiki/ 文件重新生成。

---

## 四个来源

| 来源 | 方式 | 时机 |
|--------|-----|------|
| **DREAM** | N3 阶段从 3 天活动中发现可复用结论 | 每次散朝之后 |
| **会话** | 在Draft-Review-Execute工作流中，某部产出了可复用的发现 | 日志条目标记 `wiki_candidate: true` |
| **用户** | 任何时候的直接输入 | "记住这个事实：X" |

---

## Wiki 候选格式

当 DREAM 发现值得记录的知识时：

```
📚 Wiki 候选：
- Domain: [领域名称]
- Topic: [简短标识符]
- Conclusion: [一句话 -- 可复用的结论]
- Evidence:
  - [日期] [决策/行为] -- [描述]
  - [日期] [决策/行为] -- [描述]
- Applicable when: [在什么场景下调用此条目]
```

用户在下一次早朝时确认、编辑或拒绝。

---

## 各角色如何使用 Wiki

所有角色在引用前都会检查 wiki/INDEX.md 是否存在。如果不存在或为空，角色在没有 wiki 输入的情况下正常运作。

| 角色 | 读取内容 | 使用方式 |
|------|---------------|-----------------|
| **ROUTER** | wiki/INDEX.md（完整索引） | 扫描领域匹配 -- 若存在高置信度条目，告知用户"我们已知道 X"并提议跳过冗余调研 |
| **DISPATCHER** | 相关 wiki 条目（由ROUTER传递） | 作为"已知前提 -- 从此处开始"纳入批文上下文 |
| **六领域** | 批文上下文中的 wiki 条目 | 从已建立的结论开始分析，而非从零开始 |
| **REVIEWER** | wiki/INDEX.md | 一致性检查 -- 当新结论与现有高置信度 wiki 条目矛盾时标记 |
| **AUDITOR** | wiki/ 目录（巡查期间） | Wiki 健康审计 -- 过期条目、矛盾、知识空白 |
| **DREAM** | wiki/INDEX.md + wiki/ 条目 | N3：提出新候选 + 更新现有条目的 evidence/challenges。REM：利用 wiki 作为素材进行跨领域关联 |
| **RETROSPECTIVE** | wiki/ 目录 | 在早朝时编译 INDEX.md，向用户呈报 wiki 候选供确认 |

---

## Wiki 在 Second-Brain 中的位置

```
second-brain/
├── SOUL.md              ← 你是谁（人格）
├── user-patterns.md     ← 你做了什么（行为）
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

当RETROSPECTIVE检测到 wiki/ 为空或没有 INDEX.md 时：

1. 在晨报中报告："📚 Wiki 尚未初始化。是否要进行设置？"
2. 如果用户同意：
   a. 扫描 `decisions/` 和 `_meta/journal/` 中可提取的结论（与 DREAM N3 Q2 相同逻辑）
   b. 呈现前 5 个候选 wiki 条目供用户确认
   c. 每个确认的条目：创建 `wiki/{domain}/{topic}.md`，包含正确的 front matter
   d. 编译 `wiki/INDEX.md`
3. 如果用户拒绝 → 跳过，下次上朝再提醒

此流程只触发一次。INDEX.md 存在后，正常 wiki 流程接管。

---

## 旧格式迁移

当 wiki/ 包含不符合 spec 格式的文件（无 front matter、无领域子目录、标题≠结论）时：

1. 在晨报中报告："📚 发现 N 个不符合当前规范的旧格式 wiki 文件。是否迁移？"
2. 如果用户同意：
   a. 逐个读取旧文件
   b. 每个文件提取 1-3 个可复用结论 → 作为新 wiki 条目候选
   c. 用户逐一确认 → 写入 `wiki/{domain}/{topic}.md`
   d. 将原始文件移至 `wiki/_archive/`（保留，不删除）
   e. 重新编译 INDEX.md
3. 如果用户拒绝 → 保持原样，不阻塞正常流程

wiki/ 根目录中的旧格式文件（无 front matter）会被 INDEX.md 编译忽略。

---

## 约束

- **用户确认所有写入** -- wiki 条目永远不会自动创建
- **INDEX.md 是编译产物，非手写** -- 每次早朝从 wiki/ 文件重新生成
- **每文件一条结论** -- 不创建"主题汇编"文件
- **标题 = 结论** -- 打开文件即可获得答案
- **wiki 内部不交叉引用** -- 每条记录自成一体
- **简洁** -- wiki 条目应为 10-30 行，而非研究论文
