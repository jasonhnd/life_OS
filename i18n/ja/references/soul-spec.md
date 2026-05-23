---
spec_id: soul.v2
description: SOUL.md schema v2。eou-foundry の domain_values + values-over-rules の憲法層設計を借用 —— X-over-Y formulation、優先順位総順 {1..N} タイなし・ギャップなし、3-8 次元数上限、6 質問 inclusion test ゲート、必須 outlier role slot。v1 confidence-band-only schema を置換。v1 エントリは v2 と 12 ヶ月共存（D3 RFC に従う）。
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, dev-docs/06-values-over-rules.md + schemas/captured-workflow.schema.yml
introduced_in: v1.8.5
supersedes: soul.v1 (v1.8.4 以前；v1 エントリは 2027-05-23 に自動 deprecated マーク D3 に従う)
---

# SOUL 仕様書 v2

SOUL.md はユーザーのパーソナリティアーカイブ —— 誰であるか、何を大切にしているか、ルールが衝突したときに価値がどう決断するかを記録する生きた憲法的価値層です。セカンドブレインのルートディレクトリに置かれます。

> **v1.8.5 SOUL v2 ピボット —— eou-foundry より借用**: SOUL はもはや confidence band を持つ自由な dim リストではない。優先順位総順、X-over-Y formulation、outlier role slot を持つ構造化された価値スタックとなった。RFC `_meta/rfc/v1.8.5-cleanup-and-hardening.md` Stage 4 に従う。

## なぜ v2

v1 SOUL には eou-foundry が浮き彫りにした 3 つの問題がある：

1. **衝突解決機構なし**: 2 つの SOUL 次元が反対方向を指したとき（例: "キャリア成長" vs "家族の時間"）、schema にどちらが勝つか書かれていない。解決は暗黙的。
2. **反 confirmation-bias なし**: SOUL は「すでに同意していること」の方向に成長する、なぜなら「私の好みに反するが実際に成功する」ケースを強制するフィールドがないから。
3. **憲法ゲートなし**: 何でも SOUL dim になれる ——「冷たいコーヒーが好き」と「認知的完全性は妥協できない」が同等の地位。フィルタなし。

v2 は eou-foundry から借りた 5 つの schema で修正：
- **優先順位 {1..N}** 総順 —— 厳格なランキング、タイなし、ギャップなし。高優先度が衝突で勝つ。
- **X-over-Y formulation** —— 各 dim は本物のトレードオフ、曖昧な好みではない。Y はストローマンであってはならない。
- **Inclusion test** —— dim が SOUL に入る前の 6 質問ゲート。
- **Outlier role slot** —— ユーザーが嫌うが成功を認める参照ケースを必ず含む。
- **3-8 次元数上限** —— 憲法がウィッシュリストに膨張してはならない。

## 原則（v1 保持）

1. **ゼロから成長** —— SOUL.md は空で始まる。初期化不要。
2. **証拠ベース** —— 各エントリはそれを支持する決定/行動にリンクする。
3. **厳格な基準下での自動書き込み** —— ADVISOR が各決定後に自動更新。≥2 evidence 蓄積時に新次元が低 confidence (0.3) で自動書き込み、v2 inclusion test をパスして昇格しなければならない。
4. **矛盾には価値がある** —— 解消しない；表面化する。

## エントリ形式 v2

各 SOUL 次元は YAML ブロック：

```yaml
- id: dv-{slug}                          # canonical、例 dv-truth-over-comfort
  formulation: "X over Y"                # HARD: 必ず "X over Y" 形式、Y はストローマン不可
  priority: 1                            # int、総順 1..N、タイなしギャップなし
  canonical_or_personal: canonical|personal
  lifecycle_stage: tentative|confirmed|dormant|deprecated  # v1 エントリはデフォルト confirmed だが移行マーク
  source: dream|advisor|strategist|user
  created: YYYY-MM-DD
  last_validated: YYYY-MM-DD

  # v2 新規: Inclusion test (6 質問、少なくとも ≥1 実質的回答)
  inclusion_test:
    failure_prevented: "<この value が防止する失敗は?>"
    rule_conflict_resolved: "<この value が解決するルール衝突は?>"
    hidden_judgment_exposed: "<この value が暴露する隠れた判断は?>"
    false_success_resisted: "<この value が抵抗する偽の成功は?>"
    architectural_invariant: "<この value が保護する life_OS 不変量は?>"
    danger_if_removed: "<この value を削除するとシステムは危険になるか?>"

  # v2 新規: Failure modes
  failure_modes:
    known: []          # この value が誤用される方法
    warning_signs: []  # この value が drift している観察可能なシグナル
    repair_actions: [] # この value が誤発火したときの修復

  # v1 フィールド (後方互換のため保持)
  confidence: 0.0
  evidence_count: 0
  challenges: 0

  # v1 散文フィールド (保持)
  what_is: "<観察された行動パターン>"
  what_should_be: "<ユーザーが述べた願望>"
  gap: "<実然と応然のギャップ>"
  evidence: []
  challenges_log: []
```

## 必須 Schema 制約 (v2 HARD)

### 1. 次元数: 計 3-8

- 最少 3 —— 3 未満は SOUL がまだ価値層ではない
- 最多 8 —— 8 超は SOUL がウィッシュリストに膨張
- tentative + confirmed を含む（dormant/deprecated は除外）
- **AUDITOR Mode 4 により強制**（Stage 4 Day 9）

### 2. 優先順位: 総順 {1..N}、タイなしギャップなし

- 各 dim に整数 priority フィールド
- 優先順位は 1, 2, 3, ..., N（連続、スキップなし）
- 2 つの dim が同じ優先度を共有できない
- 衝突解決: 高優先度（小さい番号）が勝つ
- **AUDITOR Mode 4 により強制**

### 3. Formulation: "X over Y" 形式

- "Truth over comfort" ✅
- "Honesty over fluency" ✅
- "誠実は良い" ❌ (Y なし、トレードオフなし)
- "Speed over slowness" ❌ (Y はストローマン、誰も slowness を好まない)
- Y はユーザーが本当に選びうる別の選択肢でなければならない
- **AUDITOR Mode 4 + `/migrate-soul-v2` により強制**（悪い formulation を拒否）

### 4. Inclusion test: ≥1 実質的回答

- 6 質問、少なくとも 1 つを非自明的に回答
- "Speed"、"elegance"、"output volume"、"fewer warnings" は**通過しない** —— これらはローカル最適化であり、憲法的価値ではない
- **AUDITOR Mode 4 + `/migrate-soul-v2` により強制**

### 5. SOUL.md 上部に必須 reference_set role slots

```yaml
soul_reference_set:
  aspirational: []         # ユーザーが憧れる人/作品
  anti_reference: []       # ユーザーが明確になりたくない人/作品
  boundary_case: []        # 価値体系をテストするエッジケース
  mainstream_baseline: []  # ユーザーの context での「普通」（対比用）
  outlier: []              # 必須: "私は嫌いだが成功する" —— 反 confirmation-bias
```

- 5 つの slot すべて必須（初期は空 list 可だが構造は存在しなければならない）
- `outlier` slot は 30 日以内に**非空であるべき** —— DREAM N3 が空をフラグする
- **AUDITOR Mode 4 + archiver Phase 2 wiki-candidate ゲートにより強制**（Stage 5）

## ライフサイクル (v2)

```
1. 🌱 tentative —— 低 confidence (0.3) で自動作成、inclusion test 待ち
2. ✅ confirmed —— inclusion test 通過 + ≥2 evidence + ユーザー確認
3. 💤 dormant —— 90 日間 evidence 蓄積なし（削除せず、非活性のみ）
4. 🗄️ deprecated —— 別の dim に置換されたかユーザーが明示的に削除
```

昇格ゲートは `references/lifecycle-gates.md` に従う:
- tentative → confirmed: inclusion_test 6Q ゲート通過 + evidence_count ≥ 2 + challenges == 0 + ユーザー確認
- confirmed → dormant: 90 日間 evidence_count 変化なし（DREAM N3 自動検出）
- any → deprecated: ユーザー明示削除または矛盾する dim 間で衝突解決で勝者宣言

## Confidence 計算 (v1 保持)

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| Confidence | 状態 | システム動作 |
|------------|------|-------------|
| < 0.3 | tentative、データポイント少 | ADVISOR のみ参照 |
| 0.3 – 0.6 | 中程度の証拠 | ADVISOR + REVIEWER 参照 |
| 0.6 – 0.8 | 強い証拠 | + PLANNER 参照 |
| > 0.8 | 深く検証、低矛盾 | 全システム参照（ROUTER 含む）|

**注意**: 優先順位フィールドは confidence と独立。priority-1 dim が confidence 0.4 でも priority-3 dim が confidence 0.95 に対して衝突で勝つ —— confidence は**誰が** dim を読むかに影響、priority は**衝突でどれが勝つか**に影響。

## 各役割が SOUL v2 をどう使うか

| 役割 | 読む | 使う |
|------|-----|-----|
| **ROUTER** | priority 1-3 dim + red lines + reference_set | より鋭い意図明確化；リスク領域 triage（`references/risk-domains.md` に従う）|
| **PLANNER** | confidence ≥ 0.6 dim + priority 順 | 関連 dim を計画に自動追加；計画はどの top-3 priority dim を運用するか宣言しなければならない |
| **REVIEWER** | すべての confirmed dim + priority + inclusion_test | 価値一貫性チェック；判定で priority を引用；Stage 7 に従って R12 trail に `value_invocations[]` を入力しなければならない（F14 を回避）|
| **ADVISOR** | すべてのエントリ + evidence/challenge カウント | 行動監査；強化または挑戦；priority 入れ替えを提案 |
| **STRATEGIST** | 未解決の矛盾 + 世界観 | 特定の緊張に対処する思想家を推薦 |
| **ARCHIVER (DREAM)** | すべてのエントリ | DREAM N3 が candidate を発見、カウントを更新、lifecycle 遷移を提案、outlier が 30+ 日空をフラグ |

## 自動書き込みメカニズム v2

ADVISOR が新次元を提案するとき:

1. **Pre-flight**: 現在の dim 数をチェック。すでに 8 → 追加前に低優先度 dim を廃止することを提案。
2. **Auto-formulation**: ADVISOR が `X over Y` 形式を提案。X だけが明確（実際の Y なし）の場合 → 「好みであり価値ではない」とマークしてスキップ。
3. **Inclusion test**: ADVISOR が 6 質問への回答を起草。≥1 実質的回答を生成しなければならない。
4. **Priority slot**: 新 dim はデフォルトで priority N+1（最下位）。ユーザーは次の session で再ランクできる。
5. **tentative で書き込み**: confidence 0.3、lifecycle_stage tentative。
6. **昇格**: ≥2 evidence + ユーザー確認後 → confirmed に変更。

## Legacy v1 エントリ (12 ヶ月共存 D3 に従う)

v1.8.5 は `references/soul-spec.md` v2 を authoritative として ship。既存の v1 SOUL エントリ:

- すべての役割で読める（legacy モード）
- DREAM N3 レポートで自動フラグ: "🔄 v1 エントリ: 'risk attitude' —— /migrate-soul-v2 経由で v2 移行を検討"
- デフォルトの `priority` フィールドは作成順で割り当て（最古 = priority 1）legacy 読み取り用
- デフォルトの `lifecycle_stage` = confirmed（v1 confidence 閾値を通過したため）
- デフォルトの `formulation` フィールド = 空（v2 inclusion test を**通過しない** —— フラグされるが許容）
- **2027-05-23** 後、残りの v1 エントリは自動的に `lifecycle_stage: deprecated` マーク

ユーザーは都合の良いときに `/migrate-soul-v2` slash command 経由で移行できる。強制移行なし。

## `/migrate-soul-v2` 経由で移行

`.claude/commands/migrate-soul-v2.md` 参照。Slash command:
1. 既存の SOUL.md を読む
2. 各 v1 dim に対してユーザーに質問: "X over Y" として formulate；priority を割り当て；inclusion test 質問 1+ に回答
3. v2 YAML ブロックを v1 散文の隣に書く（保持）
4. AUDITOR Mode 4 で検証してから commit

## 使用シーン

- **REVIEWER 否決**: contested case 検出時、SOUL から `domain_value_id` を含む `value_invocations[]` を必ず引用しなければならない。Contested case で value_invocations が空 = F14 silent judgment（`references/failure-taxonomy.md` に従う）。
- **PLANNER トレードオフ**: 2 つのドメインレポートが衝突したとき、PLANNER は SOUL 優先順位を読み、勝った dim の `id` + `priority` を引用する解決を提案。
- **archiver Phase 2 candidate gate**: 価値に触れる新 wiki エントリは ≥1 の top-3 SOUL dim を運用しなければならない（Stage 5 wiki schema 要件）。
- **AUDITOR Mode 4 (v1.8.5 新規)**: SOUL.md schema 準拠を監査 —— カウント 3-8、優先順位総順ギャップなし、formulation X-over-Y、inclusion_test ≥1 回答、reference_set 5 slot 存在。

## ソース出典

eou-foundry @ e4b12ce。借用:
- 3-8 上限 + 優先順位総順: `schemas/captured-workflow.schema.yml` domain_values_minimum_count / maximum_count / priority 制約
- X-over-Y formulation: `schemas/captured-workflow.schema.yml` `formulation_rule`
- Inclusion test 6Q: `dev-docs/06-values-over-rules.md` "Inclusion test" セクション
- Outlier role slot: `schemas/captured-workflow.schema.yml` `reference_set_required_role_slots`（outlier 記述: "I dislike this but it succeeds"）
- Failure modes 三件套: `engine/eou-contract.md` failure_modes.known/warning_signs/repair_actions

life_OS 向けに適応: SOUL は person-scope（captured_workflow のような app-scope ではない）；lifecycle_stage を 4 状態に簡略化（vs eou 9）；confidence band システムは priority と並存。
