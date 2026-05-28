---
spec_id: wiki.v2
description: Wiki entry schema v2。eou-foundry から 6 facets classification + operating_hypothesis + context_manifest 三層 + reference_set 5 role slots（outlier 含む）+ failure_modes + arguments_against を借用。v1 free-form prose schema を置換。v1 エントリは v2 と 12 ヶ月共存（D3 に従う）。
status: active
authoritative: true
source_attribution: xiaolai/eou-foundry @ e4b12ce, schemas/eou.schema.yml + captured-workflow.schema.yml + engine/eou-contract.md
introduced_in: v1.8.5
supersedes: wiki.v1 (v1.8.4 以前；v1 エントリは 2027-05-23 に自動 deprecated D3 に従う)
---

# Wiki 仕様書 v2

Wiki はシステムのナレッジアーカイブ —— 世界に関する再利用可能な結論の生きたコレクション。second-brain の `wiki/` ディレクトリに格納される。

> **v1.8.5 wiki v2 ピボット —— eou-foundry より借用**: Wiki エントリはもはや confidence/evidence metadata を持つ自由形式の散文ではない。v2 エントリは構造化された frontmatter（6 facets classification + operating_hypothesis + context_manifest + reference_set + failure_modes + arguments_against）を持つ。RFC `meta/rfc/v1.8.5-cleanup-and-hardening.md` Stage 5 に従う。

> **v2.0 将来の方向（v1.8.7 A1 仕様提案）**：`references/memory-tree-spec.md`（status: proposal）が wiki + sessions の L0 → L1 → L2 → L3 cascade seal アーキテクチャを定義、`tinyhumansai/openhuman` Memory Tree から借用。v1.8.7 では未実装 —— 将来の方向と根拠は当該仕様参照。

## 位置づけ（v1 保持）

| 保存場所 | 記録 | 例 |
|---------|------|-----|
| `decisions/` | 何を決めたか（具体的、タイムスタンプ）| "2026-04-01: 信託構造を使うと決定" |
| `meta/user-patterns.md` | 何をするか（行動パターン）| "金融次元を回避する傾向" |
| `SOUL.md` | 誰であるか（価値観、人格）—— **v2 schema は `references/soul-spec.md` 参照** | "Truth over comfort"（priority 1）|
| `wiki/` | 何を知っているか —— 宣言的知識 —— **v2 schema 本ドキュメント** | "日本の NPO 融資には貸金業法の免除なし" |
| `meta/concepts/` | シナプスグラフ —— アイデアがどう繋がるか | "company-a-holding" ノードに重み付きエッジ |
| `meta/methods/` | 手続き的記憶 —— 再利用可能なワークフロー | "5 段階品質ドキュメント改善" |

**wiki マテリアルでない**（別の場所へ）：
- アイデンティティ / 価値 / 個人的好み → `SOUL.md` v2
- 行動パターン → `meta/user-patterns.md`
- 手続き的ワークフロー → `meta/methods/`
- 概念レベル関連 → `meta/concepts/`

## 原則（v1 保持）

1. **ゼロから成長** — wiki/ は空で始まる。
2. **証拠ベース** —— 各エントリは支持する決定/経験にリンク。
3. **厳格基準下での自動書き込み** —— archiver と DREAM が基準通過時に自動作成。ユーザーは削除で調整。
4. **タイトル = 結論** —— 各エントリのタイトルは結論そのもの、トピックではない。
5. **1 ファイル 1 結論** —— マルチトピック編集なし。

## v2 Entry Frontmatter（HARD schema）

v1.8.5 以降のすべての新 wiki エントリは以下に準拠する YAML frontmatter を**必ず持たなければならない**：

```yaml
---
# アイデンティティ
id: wn-{slug}                       # canonical、例 wn-japan-npo-lending-no-exemption
name: "<人類可読名>"
version: "0.1.0"                    # semver；実質変更で bump

# v2 新規: 6 facets classification（eou-foundry eou.schema.yml より借用）
classification:
  function: generate|specify|validate|diagnose|promote|refactor|audit|propose|activate|implement|retire
  target_object: "<このエントリは何について>"
  automation_mode: deterministic|LLM_assisted|human_executed|hybrid
  authority_level: suggest_only|draft_only|write_candidate|write_inactive|mutate_active|approve|publish
  risk_level: low|medium|high|critical
  lifecycle_stage: candidate|draft|simulated|pilot|active|monitored|stable|deprecated|retired

# v2 新規: operating_hypothesis（Given/can/within 形式）
operating_hypothesis: |
  Given <input/トリガー>, under context <c>, this knowledge entry should
  produce <output/効果> within risk <r>.

# v2 新規: context_manifest（eou eou-contract.md §context_manifest）
context_manifest:
  source_of_truth: []   # このエントリが読む/引用する正典工件
  supporting: []        # 二次的 context
  forbidden: []         # context として使えないもの（明示的除外）

# v2 新規: reference_set 5 role slots（eou captured-workflow.schema.yml）
reference_set:
  aspirational: []         # ref + why; エントリが憧れる作品/人
  anti_reference: []       # ref + why; 明示的アンチ例
  boundary_case: []        # ref + why; エッジケース
  mainstream_baseline: []  # ref + why; 典型例（対比用）
  outlier: []              # active+ 必須: "私は嫌いだが成功する"；反 confirmation-bias

# v2 新規: failure_modes（eou eou-contract.md §failure_modes）
failure_modes:
  known: []          # この知識が誤用される方法
  warning_signs: []  # 知識が誤りまたは drift している観察可能シグナル
  repair_actions: [] # 知識が誤発火したときの修復

# v2 新規: arguments_against（eou generating_eou_candidate_required）
arguments_against: |
  This entry might be wrong because <理由>. Counter-evidence to watch for:
  <観察可能シグナル>.

# 既存 v1 metadata（保持）
confidence: 0.5
evidence_count: 3
challenges: 0
created: YYYY-MM-DD
last_validated: YYYY-MM-DD
source: archiver|dream|user
---

# <エントリタイトル = 結論>

<本文：宣言的知識 1-3 段落>

## Evidence

- [YYYY-MM-DD] [decision/case] — [link]

## Challenges（あれば）

- [YYYY-MM-DD] [contradicting case] — [link]
```

## v2 HARD Schema 制約

### 1. Frontmatter 7 必須フィールド群

- `id`（canonical wn-* slug）
- `classification`（6 facets すべて入力；`target_object` 非空文字列）
- `operating_hypothesis`（Given/can/within 形式；≥30 文字）
- `context_manifest`（ブロック存在；active+ エントリの `source_of_truth` 非空）
- `reference_set`（5 キー存在；candidate/draft では初期空 list 可）
- `failure_modes`（ブロック存在；初期空 list 可）
- `arguments_against`（非空文字列；≥20 文字；非自明）

**AUDITOR Mode 5 により強制**（Stage 5 Day 13 で追加）。

### 2. Reference_set `outlier` は active+ エントリで必須

`lifecycle_stage: active | monitored | stable` のエントリ：
- `outlier` list は **必ず** ≥1 エントリを含む
- 各 outlier エントリ: `ref`（工件/人/作品）+ `why`（ユーザーが嫌う理由 + それでも成功する理由）

`candidate | draft | pilot`：
- `outlier` は初期空 可
- outlier がまだ空なら `active` への昇格はブロック（`references/lifecycle-gates.md` 遷移 4 に従う）

### 3. `arguments_against` は自明であってはならない

- ✅ "このエントリは日本の税法が 2024 に変わり post-change を検証していないため誤りかもしれない。Counter-evidence: 法 17 を引用する 2024+ 判決のいずれか。"
- ❌ "誤りかも" / "Counter-evidence なし" / "<TBD>"

LLM 啟發式チェック: 具体的失敗モード + 具体的観察可能反シグナルを必ず言及。

## ライフサイクル（v2 は `references/lifecycle-gates.md` と整合）

```
1. 🌱 candidate — archiver Phase 2 / DREAM N3 が提案
2. 📝 draft — frontmatter 入力済；本文編集済
3. 🧪 simulated — 実際の決定で ≥1 回参照される
4. ✈️ pilot — 2+ 独立した決定で参照；矛盾なし
5. ✅ active — outlier slot 非空；レビュー済
6. 📊 monitored — 定期的に参照、前サイクルで挑戦なし
7. 💎 stable — 長期検証済、変更可能性低い
8. 🗄️ deprecated — 取って代わられたか矛盾；理由文書化済
9. 📦 retired — 消費者がいない
```

## Archiver Phase 2 candidate gate（v2 強化）

archiver Phase 2 は wiki candidate を書く前に**必ず**検証：

### 既存 6 criteria（v1 保持）
1. 跨プロジェクト再利用可能
2. 世界について、あなたについてではない
3. 個人プライバシーゼロ
4. 事実的または方法論的
5. ≥2 独立した証拠
6. 既存 wiki と矛盾しない（さもなければ challenges 増分）

### v2 新規 4 つのゲート

7. **operating hypothesis を起草可能**: archiver が Given/can/within 形式 ≥30 文字を試みる。曖昧すぎる場合 → 廃棄（印象であり知識ではない）。
8. **≥1 outlier を識別可能**: archiver が「私は嫌いだが成功する」例を試みる。できない場合 → candidate を書くが outlier-warn フラグ。
9. **arguments_against を書ける**: archiver はこのエントリを反証する内容を明確化。できない場合（「明らかに正しく失敗モードなし」）→ 廃棄または journal に降格（epistemic-hygiene fail）。
10. **6 facets 分類可能**: archiver が 6 facets を割り当てる。いずれかが曖昧 → ユーザー曖昧化解決のためフラグ。

## Legacy v1 エントリ（12 ヶ月共存 D3 に従う）

v1.8.5 以前の v1 wiki エントリ：
- すべての役割で読める
- DREAM N3 で自動フラグ: "🔄 v1 wiki エントリ: '<title>' —— /migrate-wiki-v2 を検討"
- デフォルト `lifecycle_stage` = `active`
- デフォルト `arguments_against` = 空（v2 ゲートを**通過しない** —— フラグされるが許容）
- デフォルト `outlier` = 空（フラグされるが許容）
- **2027-05-23** 以降、残りの v1 エントリは自動的に `lifecycle_stage: deprecated` マーク

## `/migrate-wiki-v2` 経由で移行

`.claude/commands/migrate-wiki-v2.md` 参照。Slash command:
1. 各 v1 wiki エントリを読む
2. ユーザーに入力を依頼: 6 facets、operating_hypothesis、outlier reference、arguments_against
3. v1 本文の上に v2 frontmatter を書く（本文保持）
4. AUDITOR Mode 5 で検証後 commit

ユーザーは都合の良いときに実行。強制移行なし。

## Confidence 計算（v1 保持）

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| Confidence | 状態 | 誰が使う |
|------------|------|---------|
| < 0.3 | candidate、少ない証拠 | archiver / DREAM のみ |
| 0.3 – 0.5 | draft から pilot | + REVIEWER 参照 |
| 0.5 – 0.7 | pilot から active | + PLANNER 参照 |
| > 0.7 | active+、低 challenge | 全システム参照（ROUTER 含む）|

**注意**: v2 では confidence は lifecycle_stage と独立。高 confidence の candidate はまだ candidate；昇格には `references/lifecycle-gates.md` ゲートが必要、confidence 単独では不可。

## 役割がどう wiki v2 を使うか

| 役割 | 読む | 使う |
|------|-----|-----|
| **ROUTER** | INDEX.md + 関連エントリタイトル | 現在のトピックに既存知識があれば言及 |
| **PLANNER** | 主題に一致する active+ エントリ + outlier slot | 「既知前提」入力；outlier を敵対的チェックとして |
| **REVIEWER** | エントリ `operating_hypothesis` + `arguments_against` | 矛盾するエントリを引用；矛盾時否決 |
| **ADVISOR** | エントリ使用パターン + challenges 数 | 6 ヶ月参照されないエントリをフラグ（→ dormant 候補）|
| **STRATEGIST** | エントリ本文 + reference_set | boundary_case + outlier を会話プロンプトとして使用 |
| **ARCHIVER** | すべてのエントリ（INDEX 再構築）| Phase 2 candidate gate（10 基準）；矛盾時 challenges 更新 |
| **AUDITOR Mode 5（新）** | すべてのエントリ frontmatter | Schema 監査（4 つの v2 hard チェック）|

## ソース出典

eou-foundry @ e4b12ce。借用:
- 6 facets classification: `schemas/eou.schema.yml` 22-76 行
- operating_hypothesis: `engine/eou-contract.md` 34 行
- context_manifest 三層: `engine/eou-contract.md` 39-42 行
- reference_set 5 role slots: `schemas/captured-workflow.schema.yml`
- failure_modes 三件套: `engine/eou-contract.md` 60-63 行
- arguments_against: `schemas/eou.schema.yml` 143 行

life_OS 向けに適応: wiki エントリは知識工件（EOU ではない）；v1 prose は v2 frontmatter と 12 ヶ月共存。
