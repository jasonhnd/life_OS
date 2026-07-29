---
spec_id: lifecycle-gates.v1
description: あらゆる一級 life_OS オブジェクト（SOUL dim、wiki entry、agent、spec、skill、decision）の 8 つの昇格遷移。各遷移は昇格に必要な証拠を列挙。ARCHIVER Phase 2 / DREAM N3 / ADVISOR drift detection で使用。
status: active
source_attribution: xiaolai/eou-foundry @ e4b12ce, engine/governance.yml lines 16-66
introduced_in: v1.8.5
---

# ライフサイクルゲート

> `references/agent-spec.md v2` / `references/wiki-spec.md v2`（および EOU 6 facets 語彙）の 9 つのライフサイクル段階は: `candidate → draft → simulated → pilot → active → monitored → stable → deprecated → retired`。（SOUL 次元は独自の 4 状態 `lifecycle_stage` —— `tentative / confirmed / dormant / deprecated`、`references/soul-spec.md` 参照 —— であり、この 9 段階セットではない。）
>
> 段階間の昇格には証拠が必要。このファイルは 8 つの遷移 + 各遷移の証拠 checklist を列挙。ARCHIVER Phase 2 昇格提案は、昇格推奨前にどの証拠項目が満たされたかを引用**しなければならない**。

## 8 つの遷移

### 1. candidate → draft

必要な証拠:
- ✅ Frontmatter が存在し、すべての required_top_level フィールドが入力（関連する `*-spec.md` v2 schema に従う）
- ✅ `purpose.statement` が具体的（プロセス記述ではなく、防止される失敗または改善される決定を命名）
- ✅ `operating_hypothesis` が Given/can/within 形式で述べられる
- ✅ 少なくとも 1 つの `stop_condition` が宣言される
- ✅ `blast_radius.allowed_scope` と `blast_radius.forbidden_scope` が宣言される
- ✅ `responsibility.{executor, reviewer, approver}` がすべて命名される

life_OS 例:
- SOUL dim が信頼度 0.3 で自動作成 → draft 昇格前に実際の evidence count ≥ 2 が必要（`evidence_count >= 2 AND challenges == 0`）。
- archiver Phase 2 が書く wiki entry → 6 strict criteria + outlier reference slot が入力済みでパスしなければならない。

### 2. draft → simulated

必要な証拠:
- ✅ すべての必須 schema フィールドが入力（宣言された `open_questions` を除き TBD placeholder なし）
- ✅ `evals/regression-fixtures/` に既知の失敗モードをカバーする少なくとも 1 つの回帰ケース
- ✅ `validation.deterministic` セクションが非空（slash command、AUDITOR scenario など機械的に実行可能なチェックを列挙）
- ✅ `/check-spec-drift` がこの artifact に対して CLEAN を返す
- ✅ 人類 reviewer が読んで確認

### 3. simulated → pilot

必要な証拠:
- ✅ シミュレーション run が記録（`meta/runtime/<sid>/simulation-<artifact>.md`）
- ✅ シミュレーションから critical findings（F1/F3/F6a/F10/F14/F15/F17）なし
- ✅ シミュレーション結果に人類 reviewer の署名
- ✅ すべての `open_questions` が解決済みまたは理由付きで明示的に延期

### 4. pilot → active

必要な証拠:
- ✅ `meta/runtime/<sid>/` に trace 証拠を持つ少なくとも 1 つの成功した実世界呼び出し
- ✅ 監査合格: AUDITOR Mode 3 がこの artifact に対して PASS 判定
- ✅ 回帰スイート合格（`/run-regression` がクリーン）
- ✅ 命名された人類 owner の承認（`approval.approver` は "user" のような役割ラベルではなく実在の人物識別子）

### 5. active → monitored

必要な証拠:
- ✅ 少なくとも 1 ガバナンスサイクルの間 active かつインシデントなし
- ✅ インシデント履歴がクリーン、またはすべてのインシデントに診断記録 + 修復記録（変更なしの場合 `no_change_record` spec に従う）
- ✅ 回帰スイート合格、新規失敗導入なし

### 6. monitored → stable

必要な証拠:
- ✅ 少なくとも 1 ガバナンスサイクルの間、構造的変更が不要
- ✅ 完全な回帰スイート合格
- ✅ 成熟度証拠が L5 または L6（非公式 — life_OS には eou の L0-L6 hard validator がない）

### 7. any → deprecated

必要な証拠:
- ✅ 廃止理由が文書化（`superseded` / `obsolete` / `net-negative`）
- ✅ 任意の消費者の移行パスが文書化（例: legacy SOUL dim 移行 → `/migrate-soul-v2`）
- ✅ 後継 artifact が命名（該当する場合）
- ✅ 人類 owner の承認

### 8. deprecated → retired

必要な証拠:
- ✅ 既知のすべての消費者が移行済み（`/check-spec-drift` で検証 → broken-path 参照ゼロ）
- ✅ 最終 trace がアーカイブ（`meta/v1.8.4-snapshot/` または同等の場所）
- ✅ Frontmatter 更新済み `status: legacy` + 引退日

## 特別な遷移

### "any → deprecated" はすべての段階に適用

任意の段階（`candidate` 含む）の単位は、不要と判明すれば廃止できる。中間段階をスキップする。

### Legacy 12 ヶ月共存（D3 に従う）

v1.8.5 → v2.0 移行ウィンドウ（2026-05 から 2027-05）の SOUL/wiki v1 entry:
- 古い v1 entry は v1.8.5 前のライフサイクル段階のまま
- 新 entry は作成時から v2 schema を使用しなければならない
- 強制移行なし; ユーザーは都合の良い時に `/migrate-soul-v2` または `/migrate-wiki-v2` を実行できる
- 2027-05-23 以降、残りの v1 entry は自動的に `lifecycle_stage: deprecated` フラグ

## 使用シーン

- **ARCHIVER Phase 2**: wiki 昇格を提案する際、どの遷移 + どの証拠項目が満たされたかを引用しなければならない。
- **DREAM N3 サイクル**: 昇格期限切れの artifact を検出（例: SOUL dim が `tentative` で >90 日 → 確認または廃止を提案）。
- **ADVISOR drift detection**: 後退した artifact をフラグ（例: 最近インシデントがあるが修復記録のない `active` artifact → `pilot` への降格を推奨）。
- **AUDITOR Mode 3 lifecycle scenario**（Stage 7）: 各 artifact の lifecycle_stage が利用可能な証拠と一致するかチェック; 不一致 = F11 LIFECYCLE_FAILURE。

## ソース出典

eou-foundry @ e4b12ce — `engine/governance.yml` 16-66 行（`lifecycle_promotion_gates` 8 遷移）。適応: life_OS LLM-native 検証に適合するよう証拠 checklist を簡略化（vs eou Python validator）; D3 に従い v1.8.5 固有の「legacy 12 ヶ月共存」ルール追加。
