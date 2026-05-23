---
spec_id: risk-domains.v1
description: 自動エスカレーションを要する 8 つの高リスク領域。ROUTER triage または REVIEWER 否決がいずれかの領域で対象を検出した場合、完全な 5 要件エスカレーションプロトコルが適用される（人類承認者、証拠監査、決定記録、cannot_delegate、trace 必須）。
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/governance.yml lines 67-82
introduced_in: v1.8.5
---

# 高リスク領域

> 8 領域 — 表面の依頼がどれほど平凡に見えても、いかなる決定も完全エスカレーションをトリガーする。ROUTER triage はこれらを自動 full-deliberation フラグとして使用。REVIEWER は 5 エスカレーション要件すべてが満たされない限り、これらの領域で "approved" 判定を出せない。

## 8 つの高リスク領域

| ID | 領域 | トリガー条件 |
|---|---|---|
| **R1** | **finance（金融）** | 投資決定、大型購入（>月収 20%）、借入、税務構造変更、企業株式決定 |
| **R2** | **health（健康）** | 医療処置選択、薬物変更、メンタルヘルス決定、慢性疾患管理、不妊治療決定 |
| **R3** | **legal（法律）** | 契約締結/解除、訴訟検討、規制遵守選択、IP 譲渡、結婚/離婚、親権 |
| **R4** | **safety（安全）** | 身体的安全に影響する決定（高リスク地域への旅行、危険な活動、武器所有、セキュリティセットアップ）|
| **R5** | **children（子供）** | 未成年子供の人生軌跡、教育、親権、リスク暴露に影響するあらゆる決定 |
| **R6** | **public claims（公的主張）** | 公的声明（ソーシャルメディア、報道、法廷証言、専門的評判の主張）— 虚偽主張のリスク |
| **R7** | **publication（公開）** | 取り消せないコンテンツ/コード/データの公開（プライベート repo のオープンソース化、ブログ、書籍、学術論文）|
| **R8** | **governance（ガバナンス）** | life_OS 自身の変更（HARD RULES、agent 定義、schema バージョン、防御レイヤー、バージョンピボット）|

## 5 つの自動エスカレーション要件

ROUTER がユーザーメッセージで R1-R8 のいずれかを検出した場合、または REVIEWER の判定がこれらの領域のいずれかに関わる場合、以下の 5 要件**すべて**が適用される：

### Req 1 — 人類承認者
- AI は最終承認を与えられない。これらの領域では ROUTER と REVIEWER は "suggest_only + write_inactive"。
- 最終的な go/no-go 決定**必ず**チャットインターフェースでユーザーから来る。
- 「ユーザーが 2 メッセージ前に yes と言った」は不十分 — 現在の決定には現在の確認が必要。

### Req 2 — 証拠監査
- 決定を支持するすべての主張は引用可能でなければならない。
- ROUTER は事実主張について `gh` / `Bash` / `Read` のリテラル出力を貼り付けなければならない（要約は許可されない）。
- REVIEWER は具体的な SOUL 次元を `id` で参照しなければならない（パラフレーズは許可されない）。
- 捏造されたものはすべて = F17 VALUE_HALLUCINATION + B 捏造パス違反。

### Req 3 — 決定記録
- 結果は `_meta/decisions/<id>.md` に書かなければならない、以下を含む：
  - subject
  - alternatives_considered（≥2 拒否されたオプション + 理由）
  - 決定の根拠
  - 呼び出された SOUL 次元（優先度付き）
  - reviewer 名
  - reviewed_at
  - reversal_condition（再考慮する価値のある条件）
- 決定が "no_change" / "not now" の場合 → Stage 7 `no_change_record` 形式（`_meta/incidents/` 内 7 フィールド YAML）。

### Req 4 — Cannot_delegate
- 決定は subagent または将来の ROUTER session に委任**できない**。
- subagent レポートは入力; 最終決定は orchestrator 主コンテキストでユーザー在席のもとで行われる。

### Req 5 — Trace 必須
- 完全な監査 trail が R12 spec に従って `_meta/runtime/<sid>/` に存在しなければならない：
  - 各 subagent 呼び出し: `<subagent>-<step>.json`
  - REVIEWER 判定: `reviewer-final-verdict.json`、`value_invocations[]` 入力済み
  - ユーザー確認メッセージのタイムスタンプ + リテラルテキスト

## ROUTER が triage で高リスク領域を検出する方法

ROUTER は以下のヒューリスティックパターンを使用する。**いずれかが一致 → 他の triage 決定に関わらずフルディリベレーションにエスカレーション。**

### キーワードベース検出

| 領域 | トリガーキーワード（中/英/日 例）|
|---|---|
| finance | 投资 / 买房 / 借钱 / 贷款 / IPO / 持仓 / 期权 / 信用卡分期 / invest / buy house / loan / mortgage / stock / option / equity / 投資 / ローン |
| health | 手术 / 吃药 / 抗生素 / 精神科 / 备孕 / 流产 / 化疗 / 透析 / surgery / medication / psychiatric / fertility / chemo / 手術 / 抗生物質 |
| legal | 签合同 / 离婚 / 起诉 / 仲裁 / 反诉 / 商标 / 专利 / 移民申请 / contract / divorce / lawsuit / arbitration / patent / immigration / 契約 / 離婚 |
| safety | 出差 / 高危地区 / 自驾游 / 极限运动 / 配枪 / 跟踪狂 / travel to / dangerous activity / firearm / stalker / 出張 / 危険 |
| children | 孩子 / 育儿 / 学校选择 / 监护权 / 未成年 / kid / child / school choice / custody / minor / 子供 / 学校 |
| public claims | 发帖 / 公开声明 / 上电视 / 证词 / 简历 / 推特 / blog / press / testify / public statement / resume claim / 公開 |
| publication | 开源 / 出书 / 投稿 / 论文 / 上线 / 公开 repo / open source / publish / submit / release / launch / 公開 |
| governance | 改 SOUL / 改 agent / 新加 HARD RULE / refactor / pivot / breaking change / 退役 hook / SOUL を変更 / pivot |

### コンテキストベース検出

明示的キーワードがなくても、ROUTER は以下の状況でエスカレーションをトリガーしなければならない：
- 対象に $1000 を超える金額が含まれる（finance）
- 対象に任意の指名された人物の医療状態が含まれる（health）
- 対象に 6 ヶ月以上の時間制限のあるコミットメントが含まれる（legal/governance）
- 対象に `pro/agents/` または `references/` 下のファイル変更が含まれる（governance）

### 「エスカレーション」の実際の意味

- ROUTER は R1-R8 対象に対して "Handle Directly" または "Express Analysis" パスを**使用してはならない**。
- 完全な Draft-Review-Execute（PLANNER → REVIEWER → DISPATCHER → 6 Domains → REVIEWER Final → AUDITOR → ADVISOR → ARCHIVER）を通らなければならない。
- COUNCIL トリガー閾値を低下: score diff ≥ 2（デフォルト 3）が自動的に COUNCIL を起動。

## 使用シーン

- **ROUTER triage**（`pro/agents/router.md` Stage 6 v2 frontmatter）: `context_manifest.source_of_truth` にこのファイル含む。Triage ステップはユーザーメッセージを R1-R8 と照合しなければならない。
- **REVIEWER 否決**（`pro/agents/reviewer.md`）: 判定は適用されるリスク領域を引用しなければならない; ある場合、5 要件を確認しなければならない。
- **AUDITOR Mode 3**（Stage 7 Day 21）: scenario は各決定クラスのインシデントをチェック — 対象が R1-R8 にあり、5 要件のいずれかが欠落 → F10 RESPONSIBILITY_FAILURE。

## ソース出典

eou-foundry @ e4b12ce — `engine/governance.yml` 67-82 行（8 domains + 5 automatic_requirements）。life_OS 個人使用コンテキスト用に適応: 例は企業ガバナンスではなく個人決定（finance/health/family）に根ざす。
