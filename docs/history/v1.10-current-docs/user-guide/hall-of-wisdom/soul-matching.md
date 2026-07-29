# SOUL 匹配 · 个性档案如何引导思想家推荐

## 什么是 SOUL.md

SOUL.md 是你 second-brain 里的**个性档案**——记录你的价值观、矛盾、英雄、倾向、人生故事。它由 ADVISOR 在每次决策后自动增量更新（不是一次填完）。

如果 SOUL.md 存在，STRATEGIST 在推荐思想家时会**读它**，并用两种匹配策略调整推荐。

> 如果你还没有 SOUL.md，STRATEGIST 就基于你当下说的话推荐。有 SOUL.md 会让推荐更精准。

## 两种匹配策略

STRATEGIST 不是只给你"和你想法一样的人"。那样是**回声房**，毫无意义。

它会在两种模式之间做平衡：

### 策略 A · 一致匹配（Resonance Match）

**目的**：让你看到"我不孤独——历史上有大人物和我一样这样想"。

适合场景：
- 你在一条不被理解的路上
- 你需要**语言**——别人已经为你的直觉说过的话
- 你在动摇，需要底气

例子：
- SOUL 记录"我对权威本能反感" → 推荐**尼采**（他已经用他的语言说完了你想说的）
- SOUL 记录"我讨厌无意义的重复" → 推荐**马斯克**或**达芬奇**（同类）
- SOUL 记录"我在关系中重承诺" → 推荐**孔子**或**亚里士多德**（友爱 Philia）

这时你听到的是：**你的思想的谱系**。

### 策略 B · 有益挑战匹配（Productive Challenge Match）

**目的**：让你看到"你忽略的那一面——而且是最强的那一版对立面"。

适合场景：
- 你过度偏向某一面，想校准
- 你 SOUL 里有"未解决的矛盾"
- 你怀疑自己是不是路走偏了

例子：
- SOUL 记录"过度理性、压抑情感" → 推荐**陀思妥耶夫斯基**（他最懂情感的深度）
- SOUL 记录"只讲效率" → 推荐**庄子**（让你看见效率之外的东西）
- SOUL 记录"不信任制度" → 推荐**汉谟拉比**或**孟德斯鸠**（看见制度的价值）

这时你听到的是：**你忽略的半张脸**。

### 推荐组合：一半一致，一半挑战

圆桌推荐时，STRATEGIST 常常这样配：
- 2 位一致派（让你有共鸣）+ 1 位挑战派（让你看到盲点）

例子（SOUL 记录你是"理性派 + 讨厌关系束缚"）：
- 一致：**马斯克**（第一性原理）
- 一致：**尼采**（打破价值束缚）
- 挑战：**孔子**（关系是人的本质）

三方对话会形成真实张力，而不是三个人说同样的话。

## SOUL 的哪些字段被读

STRATEGIST 关注 SOUL 里这几类字段：

### 1. 价值观维度（Values）

例子：
```yaml
values:
  - name: autonomy
    importance: high
    evidence_count: 12
  - name: family_responsibility
    importance: medium
    evidence_count: 5
```

STRATEGIST 看：哪些 importance 最高 + evidence_count 多（经常被你自己的行为证实）。

### 2. 未解决的矛盾（Tensions）

例子：
```yaml
tensions:
  - axis: freedom_vs_stability
    status: unresolved
    last_surfaced: 2026-04-10
```

**未解决的矛盾就是思想家的黄金议题。** STRATEGIST 会优先推荐曾经专门处理过这种张力的人物。

常见矛盾 → 推荐对照：

| 矛盾 | 谁擅长处理 |
|------|-----------|
| 自由 vs 稳定 | 塞涅卡（约束中的自由）、老子（无为的松动） |
| 个人 vs 家庭 | 孔子、陀思妥耶夫斯基 |
| 理性 vs 情感 | 荣格（整合阴影）、陀思妥耶夫斯基（深入情感） |
| 速度 vs 深度 | 马斯克（速度）+ 费曼（深度）→ 辩论 |
| 出世 vs 入世 | 庄子（出世）+ 王阳明（心学即入世） → 圆桌 |
| 重精英 vs 重大众 | 李光耀（精英） vs 墨子（兼爱）→ 辩论 |

### 3. 英雄清单（Heroes）

例子：
```yaml
heroes:
  - name: Steve Jobs
    source: user_mentioned
    reason: "I admire his ability to say no"
```

如果你的英雄在 93 位里 → STRATEGIST 会考虑直接召唤他。
如果你的英雄不在 93 位里 → STRATEGIST 会问"要不要召唤他？" 并按"列表外人物"处理。

### 4. 人生故事片段（Story Fragments）

例子：
```yaml
story:
  - moment: "父亲早逝，我 15 岁开始养家"
    theme: premature_responsibility
```

STRATEGIST 看得到这种背景，会避免推荐"不适配"的思想家。比如：
- 如果你从 15 岁就承担家庭 → 不会首推讲"绝对自由"的萨特做一对一（会刺伤）
- 会优先考虑**弗兰克尔**（逆境中的意义）或**爱比克泰德**（奴隶到哲人）这类"背负过重量"的人物

### 5. 倾向偏差（Biases）

例子：
```yaml
biases:
  - type: overthinking
    confidence: 0.7
  - type: risk_aversion
    confidence: 0.4
```

如果你有明显 overthinking 倾向 → STRATEGIST 会在模式推荐上加**辩论**（强制取舍、打破无限推演）。
如果你有风险厌恶 → 可能推荐**塔勒布**（反脆弱）来挑战你。

## 用 STRATEGIST 解决 SOUL 矛盾

这是一个**特殊应用**——专门用 STRATEGIST 处理 SOUL 里标记的矛盾。

### 触发方式

你可以主动说：
```
你：我想处理一下 SOUL 里那个"自由 vs 稳定"的矛盾
```

或 ROUTER 在某次对话中检测到 SOUL 里的矛盾被反复触发 → 会主动建议：
```
ROUTER：你最近几次决策都卡在"自由 vs 稳定"上。要不要召开翰林院，
       专门把这个矛盾放到台面上？
```

### 会话设计

针对 SOUL 矛盾的 STRATEGIST 会话有一个**固定结构**：

**步骤 1 · 圆桌开场（2 位一致 + 1 位挑战）**

双方各派代表，第三位做"跨界观察者"。

例子（自由 vs 稳定）：
- 自由派：尼采（摧毁所有束缚）
- 稳定派：孔子（秩序是人的需要）
- 观察者：塞涅卡（在约束中活出自由的人）

**步骤 2 · 你陈述矛盾**

你说："我既想 …又想 …"。三位听着。

**步骤 3 · 每人发言 10 分钟，点评你这个人**

不是空谈理论，是点评你——"你说的这种不安，我当年也…"

**步骤 4 · 转辩论**

你挑两位对立最强的，转辩论模式。命题是你的具体处境，不是抽象哲学。
例："30 岁辞掉稳定工作去开咖啡馆，是自由还是逃避？"

**步骤 5 · 辩论后你判决**

**不是思想家判。你判。** 你判完，SOUL.md 的 `tensions` 里会更新——

```yaml
tensions:
  - axis: freedom_vs_stability
    status: resolved_in_context  # 从 unresolved 变了
    resolution: "freedom with bounded commitments"
    resolved_at: 2026-04-20
    resolution_source: strategist_session
```

下次 STRATEGIST 就知道这个矛盾已经在这个语境下被你处理过。

### 警告：不要强行"解决"矛盾

有些矛盾**不能解决**，只能**理解**。比如"爱一个人的同时保留自我"——这可能永远是活的张力。

STRATEGIST 不会强迫你给出一个 resolution。如果你聊完仍然没有定论，SOUL 会记录：

```yaml
tensions:
  - axis: love_vs_autonomy
    status: acknowledged_as_permanent
    last_explored: 2026-04-20
    learning: "this is a tension I live with, not solve"
```

**承认永远矛盾**本身就是一种成熟，STRATEGIST 不会阻止你这样收尾。

## 实战例子

### 例子 1：一致匹配

```
SOUL 片段：
  values: [autonomy: high, authenticity: high]
  heroes: [Steve Jobs]
  biases: [contempt_for_conformity]

你：我不想参加公司的团建

STRATEGIST：你用"不想"两个字是值得注意的——不是"不能"是"不想"。
    这和你整体的价值观（自主、真实）一致。
    
    推荐一对一：尼采。
    他比任何人更擅长处理"不想符合"的困惑。他会问你：
    你是真的不想，还是只是反射性地反抗？
    
    同意？
```

### 例子 2：挑战匹配

```
SOUL 片段：
  values: [efficiency: high, logic: high]
  tensions: [rationality_vs_emotion: unresolved]
  biases: [overthinking: 0.8, emotional_avoidance: 0.6]

你：我女朋友说我冷漠，我不理解——我都对她这么好了

STRATEGIST：你用"都"和"这么好"，像是在用事件清单证明什么。
    但你女朋友说的是一种感觉。
    
    我推荐一次挑战匹配：
    - 陀思妥耶夫斯基（一对一）
    他最懂"理性外壳包裹的情感荒漠"。他会让你感到不舒服——这是好事。
    
    同意？
```

### 例子 3：矛盾专场

```
SOUL 片段：
  tensions:
    - axis: ambition_vs_peace
      status: unresolved
      last_surfaced: 2026-04-15
      evidence_count: 8

你：我又在想辞职了

ROUTER：你 SOUL 里"野心 vs 平静"已经 8 次触发还没解决。
       要不要这次专门处理它？

你：好

STRATEGIST 开会话：
  圆桌三人：马斯克（野心）+ 庄子（平静）+ 稻盛和夫（平静的野心——做大事但内心澄明）
  
  ...讨论...
  
  辩论转场：马斯克 vs 庄子，命题"30 岁辞掉高薪去画画"
  
  ...辩论...
  
  你：听完了。我想清楚了——我不是要选野心或平静，我是要学稻盛那种。
  
→ SOUL.md 更新：
  tensions:
    - axis: ambition_vs_peace
      status: resolved_as_synthesis
      resolution: "inamori-style: big ambition with inner clarity"
```

## 没有 SOUL.md 怎么办

如果你是新用户 / SOUL.md 还没生成 / 你选择不用 SOUL：

STRATEGIST 就**只基于你当下说的话**推荐。效果仍然可以，只是：
- 推荐可能不够精准（不了解你过去的矛盾）
- 多次会话之间没有连续性（第二次来，不知道第一次聊过什么）

**建议**：哪怕你不主动写 SOUL，让 ADVISOR 在每次决策后自动增量更新。时间长了 SOUL 自然丰富。

## 反模式 · 不要做的事

### ❌ 用 SOUL 做"算命"
SOUL 不是命盘。它是你行为证据的沉淀。不要把它当成"AI 告诉我我是谁"——它只是**你自己**已经表露过的你。

### ❌ 用一致匹配安慰自己
只听和你观点一样的人会加固偏见。健康的做法是**至少一场会话全是挑战匹配**——定期检查盲点。

### ❌ 让 STRATEGIST 替你解决矛盾
思想家不替你做选择。矛盾的 resolution 必须是**你**的。STRATEGIST 只负责把对立面说清楚，判决权在你。

### ❌ 改 SOUL 掩盖你的矛盾
你可以删改 SOUL（它在你的 second-brain 里，完全归你）。但**掩盖矛盾 ≠ 解决矛盾**。删掉它下次还会浮现。

## 相关文档

- [STRATEGIST 概览](strategist-overview.md) — 总体定位
- [三种对话模式](three-dialogue-modes.md) — 模式选择
- [93 位思想家索引](93-thinkers-index.md) — 挑人参考
- `references/soul-spec.md`（项目根） — SOUL.md 完整规范
