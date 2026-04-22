---
translated_from: references/method-library-spec.md
translator_note: 自動翻訳 2026-04-22、人間校正待ち
---

# Method Library 仕様書(Method Library Specification)

Method Library は Life OS の procedural memory(手続き記憶)です — 「あなたが最もうまく働く方法」のレイヤーです。second-brain の `_meta/methods/` ディレクトリに存在し、セッションをまたいで再発する再利用可能なワークフローを格納します。

## 1. 目的(Purpose)

Life OS は 3 つの異なる記憶レイヤーを保持します:

| レイヤー | 答える問い | 例 |
|-------|--------------------|---------|
| Wiki | 「世界について何が真か?」 | 「日本の NPO 貸付には貸金業法の免除がない」 |
| SOUL | 「あなたは誰か?」 | 「リスク選好度: 中〜高」 |
| Methods | 「あなたが最もうまく働く方法は?」 | 「文書を 5 段階のエスカレートする品質ラウンドで洗練する: 構造 → 内容 → 精度 → 仕上げ → リリース監査」 |

Methods は **再利用可能なワークフロー** です — 意思決定をまたいで適用される手続き的パターンです。wiki に隣接しています(両者ともクロスプロジェクトの知識)が、形が異なります: wiki は事実的な問いに答え、methods は行動のシーケンスを記述します。

Hermes Skills にインスパイアされています(`devdocs/research/2026-04-19-hermes-analysis.md` 参照)が、Life OS の decision-engine コンテキストに合わせて調整されています。Hermes skills はツール使用の手続きをエンコードし、Life OS methods は意思決定の手続きをエンコードします。

---

## 2. 何が Method として適格か(What Qualifies as a Method)

**Yes**:
- 「5 段階のエスカレートする品質ラウンドによる反復的な文書洗練」
- 「スタートアップの資金調達タイミング: 12 ヶ月のランウェイがトリガー」
- 「チームへの委譲: 責任 × 権限マトリックス」
- 「料金引き上げ交渉: データでアンカーし、3 つの選択肢を提案する」

**No**(これらは他の場所へ):
- 特定の事実 → `wiki/`
- 個人的な好みや価値観 → `SOUL.md`
- プロジェクト固有の計画 → `projects/{name}/`
- 一度限りのヒント → `inbox/` または `user-patterns.md`

**基準**: method は、異なるプロジェクトの異なる意思決定をまたいで適用できる再利用可能なワークフローです。パターンが 1 つのプロジェクトの中でのみ意味をなす場合、それはそのプロジェクトの下に属し、method library には属しません。

---

## 3. ファイルの場所(File Location)

ユーザー決定 #11 に従う(v1.7 で method library が導入されました):

```
_meta/methods/
├── INDEX.md                        # コンパイル済みサマリー(自動生成)
├── _tentative/                     # ユーザー確認待ちの候補 method
│   └── {method_id}.md
├── _archive/                       # dormant method(12 ヶ月以上未使用)
│   └── {method_id}.md
└── {domain}/
    └── {method_id}.md
```

Methods は `wiki/` の下にはありません。別の概念、別のルートです。`wiki/` との並列は意図的です: 両者ともクロスプロジェクトの知識であり、両者とも INDEX に自動コンパイルされ、両者ともユーザーによって事後にナッジされます。

Domain ディレクトリはシステム全体の domain リストをミラーします(`references/concept-spec.md §Domain partitions` と `references/wiki-spec.md §Positioning` に整合): `finance`、`startup`、`personal`、`technical`、`method`、`relationship`、`health`、`legal`、加えてユーザー定義の domain。

---

## 4. YAML Frontmatter スキーマ(YAML Frontmatter Schema)

すべての method ファイルはこの frontmatter ブロックで始まります:

```yaml
---
method_id: string                     # lowercase、ハイフン、ユニーク(例: iterative-document-refinement)
name: string                          # 表示名(例: "Iterative Document Refinement")
description: string                   # INDEX 用の 1 行
domain: string                        # finance | startup | personal | technical | method | relationship | ...
status: enum                          # tentative | confirmed | canonical
confidence: float                     # 0-1、SOUL/wiki と同じ式
times_used: integer                   # method を適用するたびにインクリメント
last_used: string                     # ISO 8601 タイムスタンプ
applicable_when:
  - condition: string                 # 自然言語の条件
    signal: string                    # この条件をトリガーする具体的なシグナル
not_applicable_when:
  - condition: string                 # method が失敗する反条件
source_sessions: [string]             # この method に寄与した session_ids
evidence_count: integer               # method がうまく働いたセッション数
challenges: integer                   # method が失敗したセッション数
related_concepts: [string]            # concept-spec の concept_ids
related_methods: [string]             # method_ids — composition を可能にする(セクション 16)
---
```

`confidence` は SOUL と wiki が使う式と同じ式で導出されます:

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

下限: 0。上限: 1。式は記憶レイヤー間で一貫しており、エージェントがスケール間で翻訳する必要はありません。

---

## 5. 本文フォーマット(Body Format)

frontmatter の後、すべての method は次の形に従います:

```markdown
# Method Name

## Summary
method が何をして、なぜうまく働くかを 1 段落で記述。

## Steps
1. Step 1 — 何をするか、なぜ重要か
2. Step 2 — 何をするか、なぜ重要か
3. ...

## When to Use
- この method が適用されることを示す条件
- 現在の subject で探すシグナル

## When NOT to Use
- method が失敗または誤誘導する反条件
- 既知のカウンターケース

## Evolution Log
- 2026-04-15: 4 ラウンドの文書洗練フローで最初に観察
- 2026-04-19: 5 ラウンドフローから confirmed、step 5(release audit)を追加

## Warnings
- よくある落とし穴と失敗モード

## Related
- [[concept-link]] — この method によって参照または洗練される concept
- [[other-method-id]] — 関連する method(兄弟または composed)
```

長さの目標: method あたり 30〜80 行。これより長い場合、通常は分割すべき method またはプロジェクト計画に偽装している method のシグナルです。

---

## 6. 自動作成(archiver による)(Auto-Creation by archiver)

Method の候補は `archiver` Phase 2(`pro/agents/archiver.md` 参照)で検出され、wiki と SOUL の候補を生成するのと同じインフラを使います。

**トリガー条件**: 現在のセッションで観察された反復可能なワークフローパターンが、既存の method シグネチャに一致 OR ヒューリスティックを満たす新規パターン。

**新規候補のヒューリスティック**:
- セッションのワークフロー内の 5 つ以上の連続したアクションが一貫した手続きを形成する
- 同じパターンが過去 2 つ以上のセッションで観察されている(hippocampus / session index 経由で参照)
- ユーザーが「approach」「pattern」「framework」「process」「流れ」「やり方」のような言葉で記述した

**反ヒューリスティック**(候補を失格させる):
- パターンが 1 つのセッションだけに現れ、クロスセッションのエコーがない
- パターンが 1 つのプロジェクトのコンテキストに固有
- パターンが既存の canonical method と重複

**候補が検出されたとき**:

1. 次を持つ method ドラフトを生成:
   - `status: tentative`
   - `confidence: 0.3`
   - `times_used: 1`
   - `source_sessions: [current_session_id]`
   - `evidence_count: 1`
2. 既存の methods と照合(`method_id` の完全一致、次に INDEX に対して description の類似度 ≥ 0.7)
3. 重複の場合 → 既存 method の `evidence_count` をインクリメント、`last_used` を更新、evolution log に書き込み — 新規候補は作成しない
4. 新規の場合 → `_meta/methods/_tentative/{method_id}.md` に書き込み
5. セッションの Completion Checklist に記録し、次の Start Session で RETROSPECTIVE が surface できるようにする

archiver は独自の判断で候補を `tentative` から昇格させません。昇格にはユーザー入力(セクション 7)または証拠の蓄積(セクション 8)が必要です。

---

## 7. ユーザー確認ワークフロー(User Confirmation Workflow)

次の Start Session で、RETROSPECTIVE は朝のブリーフィングに method 候補ブロックを含めます:

```
Method candidates detected:
"Iterative Document Refinement" (observed in 2 sessions)
  Summary: 5-round escalating quality process
  (c) Confirm — move to confirmed, start applying
  (r) Reject — delete
  (e) Edit — open for user editing
  (s) Skip — decide later
```

ユーザーの応答:
- `c` または "confirm X" → ファイルを `_meta/methods/_tentative/` から `_meta/methods/{domain}/` へ移動、`status: tentative` → `confirmed` にフリップ、confidence を 0.5(すでに 3 つ以上の source_sessions がある場合は 0.6)まで引き上げる
- `r` または "reject X" → ファイルを削除
- `e` または "edit X" → ファイルパスを表示、ユーザーが編集、状態変化なし
- `s` または "skip" → `_tentative/` に残す、次の Start Session で再度 surface

候補が 5 回連続の Start Session でユーザー応答なしに `_tentative/` に残る場合、archiver が自動アーカイブします。沈黙 ≠ 同意ですが、無限の pending 状態は手放すより悪い。

---

## 8. 昇格ラダー(Promotion Ladder)

Methods は 3 つの成熟度 tier を通過します。昇格は時間ではなく証拠に従います。

| Status | 要件 | Confidence 範囲 | システム挙動 |
|--------|-------------|------------------|-----------------|
| tentative | 1 セッションの観察 | 0.3 | dispatcher から隠される。`_tentative/` に存在。 |
| confirmed | ≥2 セッション + ユーザー confirm | 0.5–0.6 | 該当する場合、dispatcher によって注入される。 |
| canonical | ≥5 使用 + confidence ≥ 0.7 | 0.7–1.0 | 完全な dispatcher 注入 + Summary Report で名前で参照されることもある。 |

**自動昇格**:
- tentative → confirmed: ユーザー入力が必要(セクション 7)。決して自動ではない。
- confirmed → canonical: `times_used ≥ 5` AND `confidence ≥ 0.7` AND 直近 3 回の使用で challenge なしの場合、自動。

**降格**:
- 蓄積された challenges により confidence が 0.3 を下回った method は、自動降格ではなくユーザーレビュー用にフラグされる。
- ユーザーはいつでも frontmatter で status を手動設定できる。

---

## 9. DISPATCHER による使用(Use by DISPATCHER)

Draft-Review-Execute ワークフローが Step 4(DISPATCHER Dispatch)に達すると、dispatcher は method ルックアップを実行します:

```
1. _meta/methods/INDEX.md を読む
2. 各 confirmed/canonical method について、現在の subject に対して applicable_when 条件を評価
3. method がマッチする場合 → 関連する domain の dispatch コンテキストに "Known Method" としてその完全な本文を含める
4. 明確にラベル付け: "Known Method '{name}' applies — here is the established approach, use it unless the subject contradicts."
```

例: ビジネスプランを洗練するセッションが dispatcher に到達。`iterative-document-refinement` method がマッチ。DISPATCHER は実行 domain のブリーフに本文を注入する。実行 domain は、ユーザーがすでに検証済みの 5 ラウンド洗練パターンを持っていることを知って分析を開始する — アプローチを再発明するのではなく、既知の method を適用し、報告する。

これは、domain エージェントが、ユーザーがすでに経験を通じて得たワークフローを再導出するのを防ぎます。

**複数マッチ**: 2 つ以上の method が適用される場合、DISPATCHER は次のノートと共にすべてを渡します: "Multiple known methods apply — use in sequence or as alternatives, domain to judge fit."

**マッチなし**: DISPATCHER は通常通り進行 — domain はアプローチを新規に導出する。

---

## 10. 進化 / 更新(Evolution / Updates)

method を適用するすべてのセッションはその状態を更新します:

- `times_used += 1`
- `last_used` = セッションタイムスタンプ
- Evolution Log に 1 行追加: `{date}: {one-line outcome — worked, failed, revised}`
- セッションが method がうまく働いたことを示す場合(AUDITOR がプロセス問題をフラグせず、REVIEWER が初回パスで承認): `evidence_count += 1`
- セッションが method が失敗したことを示す場合(ユーザーがオーバーライド、REVIEWER が method 関連の理由で拒否権、AUDITOR がミスマッチをフラグ): `challenges += 1`
- `confidence` は標準式で再計算

**マイナーな改訂**(文言の明確化、warning の追加)は archiver Phase 2 がユーザー確認なしで適用します。

**メジャーな改訂**(step の追加、step の削除、条件変更)は次の Start Session でユーザー確認が必要です。archiver は提案された変更を `_meta/methods/_tentative/_revisions/{method_id}-{date}.md` に書き込み、新規候補と並べて surface します。

---

## 11. 減衰(Decay)

Methods は `permanence: skill` の decay を使います — フロアまでの対数的減衰であり、完全な蒸発ではありません。獲得された手続き的知識は忘れにくいべきです。

| last_used からの経過時間 | 状態 | アクション |
|--------------------------|-------|--------|
| ≤ 6 ヶ月 | Active | アクションなし |
| 6–12 ヶ月 | Dormant | RETROSPECTIVE がブリーフィングでフラグ: "Method '{name}' has been dormant for N months." |
| ≥ 12 ヶ月 | Archived | archiver がファイルを `_meta/methods/_archive/{method_id}.md` へ移動。 |
| Archived + ユーザーが明示的に削除 | Retired | ファイル消滅。パターンが再浮上しても自動再作成なし。 |

Methods は決して自動削除されません。Methods は獲得されたもの; アーカイブはシステムが取る最も強力な自動アクションです。最終削除には常にユーザーが必要です。

---

## 12. スコープガード(プライバシー)(Scope Guards (Privacy))

wiki エントリに適用されるのと同じプライバシーフィルター(`references/wiki-spec.md` セクション "Privacy Filter" 参照)が method 本文に適用されます:

- method テキストに個人名を含めない — 書き込み前に除去
- method 本文に特定のプロジェクトを参照しない — プロジェクト参照は `source_sessions` の中にのみ現れてよい
- 特定の金額、口座番号、ID 番号を含めない — すべての数値例を汎用に保つ("~12 months runway" であり "¥8,400,000" ではない)
- 追跡可能な日付+場所の組み合わせを含めない
- method が真にその会社についてである場合を除き、特定の会社名を含めない(まれ)

これらの参照を除去すると method が意味をなさなくなる場合 → パターンは実際には再利用可能ではなかった、候補を破棄する。

Methods はローカルのみに保存されます。決して Notion に同期されません(ユーザー決定 #12)。

---

## 13. INDEX.md フォーマット(INDEX.md Format)

`_meta/methods/INDEX.md` は RETROSPECTIVE が Start Session ごとに実際の method ファイルからコンパイルします。決して手動編集しないでください。

```markdown
# Method Library Index
compiled: YYYY-MM-DD

## canonical (5)
- iterative-document-refinement | Refine documents in 5 escalating quality rounds | used 12 times | 0.85
- runway-fundraise-trigger | Start fundraising when runway drops below 12 months | used 7 times | 0.78
- ...

## confirmed (8)
- responsibility-authority-matrix | Delegate by mapping responsibility × authority | used 3 times | 0.55
- ...

## tentative (3)  [awaiting user confirmation in _tentative/]
- weekly-review-reset | Reset every Friday by listing completions and drops | observed 2 sessions | 0.30
- ...

## dormant (1)  [≥6 months since last use]
- quarterly-strategic-review | Quarterly strategic reset framework | last used 2025-10-14 | 0.62
```

各行 ≤ 100 文字。INDEX 全体は通常 30〜120 行。ロードが安く、スキャンが容易。

---

## 14. Hermes Skills との相互作用(Interaction with Hermes Skills)

Hermes Skills はツール使用のための procedural memory(API の呼び出し方、シェルコマンドのフォーマット方法)。Life OS methods は意思決定のための procedural memory(選択肢の評価方法、文書の洗練方法、資金調達のタイミング)。

| 次元 | Hermes Skill | Life OS Method |
|-----------|--------------|----------------|
| スコープ | ツール操作 | 意思決定ワークフロー |
| アクティベーション | 明示的構文(`@skill:name`) | dispatcher 条件マッチ経由で自動 |
| セキュリティスキャン | 必須(コードを実行できる) | 不要(ユーザー確認済みテキストのみ) |
| ライフサイクル | Skills は明示的にバージョニング | Methods は Evolution Log 経由で進化 |

method library は Hermes の YAML + markdown + evolution log パターンを借りていますが、Hermes がツール使用コンテキストに必要とするもの(アクティベーション構文、セキュリティスキャン、バージョンロック)を落としています。

---

## 15. v1.6.x からのマイグレーション(Migration from v1.6.x)

v1.6.2a には method library がありません。`tools/migrate.py` は既存のセッション履歴からバックフィルします:

1. `_meta/journal/*.md` とバックフィルされた decision をスキャンし、approach を記述する言葉を探す: "approach"、"pattern"、"framework"、"process"、"流れ"、"やり方"、"手順"。
2. (クロスセッション言及数で)最も参照されている上位 5 パターンを抽出。
3. 各々を `status: tentative` かつ `confidence: 0.3` で `_meta/methods/_tentative/{method_id}.md` に候補として書き込む。
4. 次の Start Session でユーザーレビュー用にフラグ。

マイグレーションは一度限りです。さらなるパターン検出はライブセッションでの archiver Phase 2 を通じて発生します。

マイグレーションスクリプトは tentative を超えて昇格させません。ユーザーは、バックフィルされたパターンのいずれかが実際に confirmed method になるかを決定します。

---

## 16. v1.7 の Out of Scope(Out of Scope for v1.7)

v1.7 で明示的に out of scope:

- **Parameterized methods** — 「N ラウンドの反復的洗練」を 1 つのパラメトリック method として、または N 個の method として? v1.7 は atomic method のみを使用。
- **Versioned history** — methods はバージョン文字列を持たない。Evolution Log が変更履歴を十分にキャプチャ。
- **Composition** — hard composition(自動連鎖実行)は v1.7 の out of scope。`related_methods` 経由の soft composition が v1.7 の答え。
- **Cross-language bodies** — v1.7 はすべての method 本文を英語で書く; theme は Summary Report レベルでのみ表示に影響する。

---

## 17. Anti-patterns

- 明示的なユーザー入力なしに `confirmed` を超えて自動昇格してはならない
- 1 つのセッション観察から method を作成してはならない
- プロジェクト固有の戦術を methods として格納してはならない — それらは `projects/{name}/` に属する
- Methods を Notion に同期してはならない — ローカルのみ
- tentative キューを無制限に成長させてはならない — 5 回の沈黙 Start Session = 自動アーカイブ
- 特定の名前、金額、ID、会社、または場所を参照する method を書いてはならない
- Major Revision ワークフローなしに archiver に confirmed/canonical methods を編集させてはならない
- INDEX.md を手動でコンパイルしてはならない — 生成されたアーティファクトである
- `permanence: skill` を permanence として扱ってはならない — dormant methods も年を取る、ただしゆっくりと

---

## 18. 各ロールが Method Library をどう使うか(How Each Role Uses the Method Library)

すべてのロールは `_meta/methods/INDEX.md` が存在するかを参照前にチェックします。存在しないまたは空の場合、ロールは method 入力なしで動作します。

| ロール | 読むもの | 使い方 |
|------|---------------|-----------------|
| RETROSPECTIVE | `_meta/methods/INDEX.md` + `_tentative/` | Start Session で INDEX をコンパイル。候補を confirmation 用に surface。dormant method をフラグ。 |
| ROUTER | INDEX(ヘッダー) | triage 中に domain 関連 method をスキャン。ユーザーに「you have a known approach for this」と伝えることもある。 |
| PLANNER | INDEX(完全) | 計画文書を起草する前にどの methods が適用可能かをレビュー。名前で参照することもある。 |
| DISPATCHER | 関連する method 本文 | "Known Method" として domain のブリーフに注入(セクション 9)。 |
| Six Domains | dispatch コンテキストの method 本文 | ワークフローを再導出する代わりに既知の method を適用。準拠または逸脱を報告。 |
| REVIEWER | INDEX | 一貫性チェック — 計画文書が適用可能な method を無視した場合、フラグ。 |
| AUDITOR | `_meta/methods/` ディレクトリ | Patrol 点検 — 古い methods、矛盾、長く座っている候補。 |
| ARCHIVER | INDEX + すべての method ファイル | Phase 2: 候補を検出、evolution log を更新、改訂を提案。 |
| DREAM | INDEX | REM stage がクロスドメイン洞察のための結合組織として method パターンを使用。 |

---

## 19. 関連仕様(Related Specs)

- `references/wiki-spec.md` — 隣接する知識レイヤー(宣言的 vs 手続き的)
- `references/soul-spec.md` — アイデンティティレイヤー
- `references/dream-spec.md` — REM stage が method パターンを検出
- `references/concept-spec.md` — methods は `related_concepts` 経由で concept にリンク
- `references/hippocampus-spec.md` — クロスセッションエコーのヒューリスティックに供給する過去セッション検索
- `pro/agents/archiver.md` — method 候補を書き込む(Phase 2)
- `pro/agents/dispatcher.md` — method を domain のブリーフに注入
- `devdocs/research/2026-04-19-hermes-analysis.md` — Hermes インスピレーションの源

---

## 20. 制約サマリー(Constraints Summary)

- archiver によって候補ヒューリスティックが通過した場合のみ自動作成
- `_tentative/` を離れるにはユーザー確認が必要; canonical への昇格は 5 使用 + 0.7 confidence で自動、confirmed への昇格はそうではない
- 書き込みごとにプライバシーフィルターが適用される; methods はローカルのみ(Notion に同期しない)
- INDEX.md はコンパイルされる、著者がつくものではない
- ファイルごとに 1 つのワークフロー — method コレクションを作成しない
- Methods は決して自動削除されない — 12 ヶ月 dormant 後に自動アーカイブのみ
- メジャーな改訂にはユーザー確認が必要
- Methods は SOUL と wiki と同じ confidence 式を使用

---

*本文は英語版 2026-04-22 スナップショットの翻訳。英語版が権威源。*
