---
translator_note: 自動翻訳 2026-04-22、人間校正待ち
---

# 概念グラフ + メソッドライブラリ · システムはどう「知恵を蓄える」か / Concept Graph & Method Library

> パンくず: [← Cortex 総覧](./overview.md) · [← 製品入口:ユーザーガイド索引](../index.md)

> adjourn のたびに、システムは session をアーカイブするだけではありません——今回の対話をスキャンし、**候補概念 (concept candidates)** と**候補メソッド (method candidates)** を抽出します。次回 Start Session では、retrospective がブリーフィング内で尋ねます:「この 2 つの候補は妥当に見えますか?確認、却下、それとも編集?」使えば使うほど、これらのノードの**辺の重み (edge weight) が強化されます**(ヘブ型強化);長期間使用されなければ、permanence 等級に従って徐々に減衰します。これが Cortex の「長期記憶」次元です。

## 一文概説 / One-Line Overview

**概念グラフ** (`_meta/concepts/`) は Cortex のニューロンネットワークです——各 concept は一つの `.md` ファイルであり、**辺 (synapse)** は concept 自身の YAML frontmatter に直接保存されます。**メソッドライブラリ** (`_meta/methods/`) は「あなたがどう働くか」の手続き的記憶です——再利用可能な多段階ワークフロー。両ディレクトリとも `tentative → confirmed → canonical` の成熟度ラダーに従い、archiver が候補を自動抽出し、ユーザーが確認して昇格させます。

---

## なぜこの 2 つを追加するのか / Why Add These Two

### 痛点 1: 毎回「これは何か」を説明する

あなたが言う:「前回議論したあの MVP 検証プロセス——覚えている?」

v1.6.2a のシステム: 覚えていない(あるいは wiki から「MVP Validation」という静的エントリを引っ張り出しますが、**あなたの具体的プロジェクトとの関連は知りません**)。

毎回冒頭でこのプロセスを 2 分かけて繰り返さざるを得ない。

### 痛点 2: 同じ決定プロセスを何度も踏む

「新しいパートナーを受け入れるかどうか」の決定のたびに:
1. 要件次元を列挙(×5 回)
2. スコア重み付けを設定(×5 回、毎回重みが微妙に違う)
3. デューデリジェンスチェックリストを一周(毎回自分で模索)
4. 事後「次回は何を最初に聞くべきか」を振り返る(振り返っても書き留める場所がない)

6 回目にようやく気づく:「**固定**のパートナー評価メソッドがあるべきではないか?」——しかし v1.6.2a にはこのメソッドを保存する場所がなく、ある journal に自由テキストで書くしかなく、次回使用時にまた自分で探すことに。

### 概念グラフの約束 / Promise

Cortex は対話をスキャンし、「MVP 検証」という概念が繰り返し出現 + 複数の独立した証拠があると判断 → `_meta/concepts/method/mvp-validation.md` に **tentative** ノードを自動作成。次回類似トピックについて話せば、hippocampus Wave 2 がこの concept の強い辺に沿って拡散 → 関連する過去 session も引き出されます。

**使用回数が増えるほど、activation_count +1、関連辺の weight +1**。10 回使用すると **canonical** に昇格。将来いつでも ROUTER の `[COGNITIVE CONTEXT]` で自動的に含まれます。

### メソッドライブラリの約束

同様に、Cortex は対話をスキャンし、以下を発見した場合:
- **5+ ステップ**の連続したワークフロー
- **2+ の独立 session** で同じパターンが出現
- 「approach / pattern / framework / 流れ / やり方 / 手順」という表現

archiver Phase 2 が `_meta/methods/_tentative/{method_id}.md` に **tentative method** を自動書き込み、次回 Start Session で尋ねます:「新しいメソッド 'Iterative Document Refinement' を検出しました。確認しますか?」

あなたが確認すると、**DISPATCHER は今後の関連決定でこのメソッドの完全な body を 6 領域に自動注入**——6 領域はゼロからやり直すのではなく、あなたが磨き上げたメソッドを基に始めます。

---

## ユーザー側に見えるもの / What the User Sees

### シナリオ A: adjourn 後の候補検出

「プロダクトドキュメント再構築」に関する決定を終えたばかり。archiver Phase 2 が対話をスキャンし:

- "iterative-refinement" という概念が今回の対話で 3 回活性化 (Wave 1 検出)
- 対話で **5 ラウンドのエスカレート式品質磨き** を記述(新メソッド候補)

archiver が session の Completion Checklist に記録:

```
## Cortex artefacts this session
- Concept candidates (2): iterative-refinement, quality-escalation
- Method candidate (1): Iterative Document Refinement (5-round)
- Activated concepts: [iterative-refinement, passpay-white-paper]
- Hebbian updates: 8 edges reinforced, 2 new edges
```

その後 session は正常に終了し、Cortex artefacts は `_meta/concepts/_tentative/` および `_meta/methods/_tentative/` に残り、次回確認を待ちます。

### シナリオ B: 次回 Start Session の候補確認ブロック

次回 session を開くと、RETROSPECTIVE がブリーフィングに以下のブロックを追加:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧬 Concept & Method Candidates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Method candidates detected (1):
  "Iterative Document Refinement"(2 回の session で観察)
  Summary: 5 ラウンドのエスカレート式品質磨き (structure → content → precision → polish → release audit)
  (c) Confirm — confirmed に移動、適用開始
  (r) Reject — 削除
  (e) Edit — ファイルを開いて編集
  (s) Skip — 次回に決定を延期

Concept candidates (tentative, silently promoted):
  · iterative-refinement (activation 3, 辺重み 2)
  · quality-escalation (activation 2, 辺重み 1)
```

### シナリオ C: ユーザー応答

あなたが応答:**"c"** または **"confirm Iterative Document Refinement"**。

システム:
- `_meta/methods/_tentative/iterative-document-refinement.md` を `_meta/methods/method/iterative-document-refinement.md` に移動
- `status: tentative → confirmed` を反転、`confidence` は 0.3 から 0.5 に跳ね上がる(すでに 3+ の source_sessions があれば 0.6)
- 次回 DISPATCHER は関連トピックの dispatch でこのメソッドを**自動注入**

### シナリオ D: メソッドが DISPATCHER により自動適用

数日後、session を開いて尋ねる:「この商業白書を再構築してほしい。」

DISPATCHER は Step 4 で method lookup を実行し、`iterative-document-refinement` の `applicable_when` 条件がマッチすることを検出(「document refinement」+ 「多段階磨きのニーズ」)。growth / execution 2 領域の brief に注入:

```
Known Method 'Iterative Document Refinement' applies — here is the
established approach, use it unless the subject contradicts:

[メソッド完全 body]
```

6 領域分析では**プロセスを再発明しない**——5 ラウンドメソッドを直接適用し、各ラウンドの出力を報告し、「このラウンドは step 3 (precision pass) に該当」と注釈。ROUTER の奏折には「既定メソッドに基づき、今回の refinement の提案は……」と記されます。

---

## 概念ファイルはどんな形か / What a Concept File Looks Like

各 concept は独立したファイル(strict: 1 concept = 1 ファイル、組み合わせ不可)、形式:

```yaml
---
concept_id: iterative-document-refinement
canonical_name: "Iterative Document Refinement"
aliases: ["5-round refinement", "升级打磨", "品質4段階"]
domain: method
status: canonical                 # tentative → confirmed → canonical
permanence: skill                 # identity / skill / fact / transient
activation_count: 14
last_activated: 2026-04-20T10:32:00+09:00
created: 2026-03-12T14:20:00+09:00
outgoing_edges:
  - to: mvp-validation
    weight: 8
    via: [cross-project-method]
    last_reinforced: 2026-04-20
  - to: passpay-white-paper
    weight: 5
    via: [applied-in-project]
    last_reinforced: 2026-04-18
provenance:
  source_sessions:
    - claude-20260312-1420
    - claude-20260321-0945
    - claude-20260412-1830
  extracted_by: archiver
decay_policy: skill               # permanence に対応、ミスマッチ不可
---

# Iterative Document Refinement

5 ラウンドのエスカレート式品質磨きプロセス:
1. Structure — 骨格
2. Content — 肉付け
3. Precision — 用語、データ、引用
4. Polish — 言語、リズム
5. Release audit — 最終の法務/コンプライアンス/ブランドチェック

## Evidence / Examples
- [[claude-20260312-1420]] 商業白書 v0.6
- [[claude-20260321-0945]] 技術白書 v0.4

## Related Concepts
- [[mvp-validation]]
- [[passpay-white-paper]]
```

**要点**:

- **1 概念 1 ファイル**——同一ファイルに複数 concept を書くことは不可(anti-pattern、archiver は書き込みを拒否)
- **outgoing_edges はこのノード自身の frontmatter に属する**——独立したグラフデータベースではありません。逆インデックスを見たい?`_meta/concepts/SYNAPSES-INDEX.md`(archiver が自動再構築、**手動編集不可**)
- **activation_count は単調増加**——活性化のたびに +1(アクティブなライフサイクル内)
- **weight 上限 100**——runaway 強化を防止
- **permanence と decay_policy は一致必須**——identity は不衰退、skill は対数衰退、fact は指数衰退、transient は cliff

---

## メソッドファイルはどんな形か / What a Method File Looks Like

メソッド (`_meta/methods/{domain}/{method_id}.md`) は**手続き的記憶**——再利用可能な意思決定ワークフローであり、wiki(事実的結論)と並列。

```yaml
---
method_id: iterative-document-refinement
name: "Iterative Document Refinement"
description: "5 ラウンドのエスカレート式品質磨き"
domain: method
status: canonical
confidence: 0.82
times_used: 7
last_used: 2026-04-20T10:32:00+09:00
applicable_when:
  - condition: "ドキュメント品質を公開レベルまで磨く必要がある"
    signal: "ユーザーが 'refine / 打磨 / 推敲' と言及、かつ目的が外部公開"
  - condition: "複数ラウンドのフィードバックサイクルが許容される"
    signal: "タイムライン ≥ 3 日"
not_applicable_when:
  - condition: "一回限りの迅速な産出"
    signal: "ユーザーが 'quick draft / 快速版本' と明言"
source_sessions:
  - claude-20260312-1420
  - claude-20260321-0945
evidence_count: 5
challenges: 1
related_concepts:
  - iterative-refinement
  - quality-escalation
related_methods:
  - mvp-validation-methodology
---

# Iterative Document Refinement

## Summary
5 ラウンドのエスカレート式品質磨き:各ラウンドは一つの焦点に絞り、レイヤーをまたぐ修正は許可されない。
作用:「毎回下層レイヤーで悩み、上層レイヤーには到達せず」の反復横跳びを防ぐ。

## Steps
1. Structure — 骨格と段落順序のみ修正。表現には触れない。
2. Content — コンテンツ追加のみ。構造には触れない。
3. Precision — 用語、データ、引用の校正のみ。
4. Polish — 表現、リズム、冗長性のみ修正。
5. Release audit — 最後に法務/コンプライアンス/ブランドを一周、大きな変更はもうしない。

## When to Use
- ドキュメントが外部公開予定(白書、PR、提案)
- 複数ラウンドのフィードバックサイクルが許容される
- 多角度チェックが必要(法務、技術、ビジネス)

## When NOT to Use
- 時間が逼迫、一回限りの起草
- ドキュメント定位自体が未明確(先に定位、さもなくば step 1 の骨格が繰り返し作り直し)

## Evolution Log
- 2026-03-12: 4 ラウンドプロセスを初観察
- 2026-03-21: 第 5 ステップ (release audit) 追加
- 2026-04-20: 「各ラウンドはレイヤーをまたがない」の anti-pattern ルール追加

## Warnings
- step 3 と step 4 は混同しやすい——厳密に区別:3 は事実的エラーの校正、4 は美感
- step 5 をスキップすると公開後にブランドトーンの不統一が発覚することが多い
```

**要点**:

- メソッドは **tentative から開始**、ユーザーが confirm しないと confirmed に進めない、canonical は自動(`times_used ≥ 5 AND confidence ≥ 0.7 AND 直近 3 回に challenge なし` で達成)
- **evidence_count は「メソッドが使用され、効果があった」**、challenges は「使用されたが REVIEWER が却下、または AUDITOR が不一致と標記」
- メソッドは **Notion 同期に入らない**——メソッドライブラリはローカル `_meta/` 下の内省資産
- メソッドは**具体的プロジェクト名、人名、金額を直接参照できない**——プライバシーフィルターが body から剥ぎ取る、さもなくば「メソッドは再利用可能ではなく、ただのメモ」

---

## ヘブ型強化 (Hebbian) / Hebbian Reinforcement

**"Neurons that fire together, wire together."** — 脳科学のヘブ則。Cortex の synapse 強化ルールは厳密にこれに対応:

### 各 session 内:

- concept A と concept B が**同一 frame 内で**同時活性化 → 辺 A→B の weight +1(上限 100)
- 新しい辺の場合、初期 weight = 1
- `last_reinforced = today`

### 各 Adjourn 終了時の decay パス:

permanence 等級ごと:

| Permanence | Decay 形態 | 適用 |
|-----------|-----------|------|
| `identity` | **不衰退** | SOUL コア価値、長期関係 |
| `skill` | **対数衰退**、下限まで(永遠に ≠ 0) | 「Python が書ける」のような習得スキル |
| `fact` | **指数衰退** | 「Q2 のあのプロジェクト予算は X」のような時効的事実 |
| `transient` | **cliff 衰退**、期限で 0 | 一回性のイベント、臨時参照 |

辺の重みも concept の dormancy と共に衰退。`weight ≤ 0` になると次回 Adjourn でこの辺は**剪定**されます。

### 昇格パス

**concept:**
| From → To | トリガー |
|---------|------|
| `tentative → confirmed` | ≥ 3 の独立 session で活性化、ファイルは `_tentative/` から `{domain}/` へ移動 |
| `confirmed → canonical` | ユーザーが pin、または ≥ 10 の独立 session で活性化 |

**method:**
| From → To | トリガー |
|---------|------|
| `tentative → confirmed` | **ユーザーが c / confirm しなければならない**(**決して**自動化しない) |
| `confirmed → canonical` | **自動**:`times_used ≥ 5 AND confidence ≥ 0.7 AND 直近 3 回に challenge なし` |

### なぜメソッドの昇格はユーザー要求、概念は不要?

- **概念**は記述的(entity / 理念 / パターン)——システムが繰り返し出現を検出すれば自動成立可
- **メソッド**は規定的(システムに**積極的にこのプロセスを適用**させる)——あなたに聞かずに DISPATCHER に注入してはいけない。だから tentative → confirmed は決して自動化しない

---

## ユーザーアクション · 介入方法 / User Actions

### 1. 候補確認ブロックへの応答 (c/r/e/s)

前述「シナリオ B/C」を参照。4 つの応答:

| 入力 | 挙動 |
|------|------|
| `c` / "confirm X" | confirmed に移動、適用開始 |
| `r` / "reject X" | 候補ファイル削除 |
| `e` / "edit X" | ファイルパスを出力、手動編集、状態遷移はトリガーしない |
| `s` / "skip" | `_tentative/` に残留、次回 Start Session で再出現 |

連続 **5 回 Start Session で無応答** → archiver が自動 archive(沈黙 ≠ 同意、しかし無限 pending はより悪い)。

### 2. 手動で概念/メソッドを新規作成

`_meta/concepts/{domain}/{concept_id}.md` に直接ファイル作成、frontmatter に `status: canonical` + `permanence: identity`(または適切なもの)——archiver が次回実行時にグラフに取り込みます。

メソッドも同様:`_meta/methods/{domain}/{method_id}.md`。

### 3. 手動で canonical に pin

frontmatter を編集、`status: canonical` に変更。archiver はユーザー書き込みを尊重します。

### 4. 最近の concept / method 自動書き込みを取り消す

session で言う:

> 撤销最近的 concept

または

> 撤销最近的 method

archiver が次回に最近一括の自動書き込みを roll back(wiki undo と同機構)。

### 5. concept / method を削除

ファイルを直接削除。次回 archiver は SYNAPSES-INDEX.md を再構築し、すべての dangling edge を剪定します。**outgoing_edges を手動編集しないでください**——archiver は次回 Adjourn であなたの変更を上書きします。

### 6. permanence 調整(昇格または降格)

frontmatter `permanence` フィールドを編集。注意:

- `permanence` と `decay_policy` は一致必須——不一致時 archiver は次回 AUDITOR 巡査で赤標記
- 昇格 (fact → skill)——合理的な時、例えばある物が一回性の事実ではなく真のスキルだと気づいた
- 降格 (skill → fact)——ある物が思ったほど安定していないと発見した

### 7. グラフの健康状態を確認

`_meta/concepts/INDEX.md` を開く——毎回 Start Session で RETROSPECTIVE がコンパイル、1 行 1 concept の summary + status + activation + confidence。

健康的なシグナル:
- Canonical 数が着実に増加(一回性の急増ではない)
- Dormant (>30 日非活性化) concept が少なく明確
- `_archive/` に retire された concept がある(decay 機構が働いている証)

不健康なシグナル:
- Canonical 数が毎週 5+ 急増(archiver の過剰抽出可能性)
- 一つの「hub」concept が 40+ の outgoing_edges(過剰接続の可能性)
- `_tentative/` に数十の候補が複数 Start Session を経てもクリアされていない(ずっと skip で confirm/reject なし)

---

## よくある質問 / Common Questions

### 私の「彼女」は concept になり得るか?

**なり得ない**。個人(具体的な人物)は**明確に禁止**されています。それは SOUL の領地です(SOUL 内に「パートナーとの関係」のような **dimension** はあり得ますが、dimension は concept ではない)。

`relationship/` という domain は concepts 下で**組織と非個人関係エンティティ用に保留**——例えば「ベンチャー界隈」、「某グループ」、「日本の NPO 界」。

このルールは archiver Phase 2 のプライバシーフィルターにハードコードされており、「人名類」concept 候補を直接破棄します。

### outgoing_edges を手動編集するとどうなる?

次回 Adjourn で archiver に上書きされます。**archiver が edge の書き込み権限を所有し、ユーザーは所有しない**。

接続を断ちたい場合の正しい方法:
- どちらかの concept ファイルを削除
- またはその 2 つの concept を長期間 co-activate させない(辺の重みは自然に 0 まで衰退し剪定される)

### concept の edge weight 上限がなぜ 100?

runaway 強化を防止するため。ある concept ペアが毎日同時に活性化すると、30 日で weight ≥ 30、1 年で ≥ 300——上限がなければ、この辺は hippocampus Wave 2 の全拡散予算を「独占」し、他の隣接が全て押し下げられます。100 は経験値で、「区別性」と「独占しない」のバランスです。

### メソッドは組み合わせ可能?例えば「メソッド A を使ってからメソッド B」?

v1.7 は**ソフト組み合わせのみサポート**——メソッドファイルの `related_methods` フィールドで他の method ID を指し示せ、DISPATCHER は複数 method マッチ時にすべて注入し「複数メソッドが利用可能、domain が適用性を判断」と注釈します。

**ハード組み合わせ**(A → B のチェーン自動実行)は **v1.7 out-of-scope**。想像してみてください:archiver は「メソッド A の出力」と「メソッド B の入力」が今回の session で構造的に互換であることを保証できません——このチェーン保証には独立した実行フレームワークが必要で、v1.7 のスコープ外。

### メソッドは Wiki と衝突する?

衝突しません——異なる質問に答えます:

| | Wiki | Method |
|---|------|--------|
| 答え | 「世界はどうなっているか?」 | 「あなたはどう働くのが最善か?」 |
| 例 | 「日本の NPO は貸金業法の免除を受けない」 | 「5 ラウンド磨き:構造 → コンテンツ → 精度 → 磨き → リリース監査」 |
| 形状 | **declarative**(事実陳述) | **sequential**(ステップ順列) |

archiver Phase 2 には専用の **routing decision tree** があります(`references/cortex-spec.md` §Archiver Candidate Routing 参照)、順序判定:SOUL → user-patterns → method → concept → wiki → discard。1 候補は**1 つの主 destination layer のみに入る**、二重書き込み不可。

曖昧なシナリオ(例えば「ベストプラクティス」と読める場合):
- **ユーザーの一連のアクション**を記述 → method
- **世界の属性**を記述 → wiki
- 本当に曖昧な場合、**デフォルト wiki**(method にはより強い証拠が必要:5+ ステップ + 2+ session の跨境エコー)

### Concept が dormant になるとどうなる?

**30 日超非活性化** → RETROSPECTIVE が Start Session ブリーフィングで dormant (💤) フラグ。

**canonical 概念の activation_count が長期 dormancy で 0 に下がる** → `_meta/concepts/_archive/{domain}/{concept_id}.md` にアーカイブ。アーカイブ後:
- git 履歴に残る(データ損失なし)
- hippocampus は活性化時に `_archive/` 下の concept を**無視**
- AUDITOR は巡査時に依然として見える

**完全削除**は常に手動必須——最強の自動アクションはアーカイブです。

### メソッドもアーカイブされる?

される、ただしタイムラインはより長い:

| last_used からの距離 | 状態 | アクション |
|------------|------|------|
| ≤ 6 ヶ月 | Active | 無動作 |
| 6–12 ヶ月 | Dormant | RETROSPECTIVE がブリーフィングで「メソッド 'X' は N ヶ月未使用」とフラグ |
| ≥ 12 ヶ月 | Archived | archiver が自動で `_meta/methods/_archive/` に移動 |
| Archived + ユーザー削除 | Retired | ファイル削除、パターン再出現しても自動再構築なし |

**メソッドは勝ち取るもの——アーカイブはシステムの最強の自動アクション。最終削除は常にユーザー**。

---

## トラブルシューティング / Troubleshooting

### 「システムが明らかに使っているメソッドを検出しない」

3 つの一般的原因:

1. **跨 session エコー不足**——メソッド候補の anti-heuristic は「1 session だけ出現したパターン」を明確に除外。解決: 2–3 session の自然蓄積を待つ、または手動でメソッドファイル作成
2. **記述言語が断片的**——このプロセスを毎回完全に異なる言葉で記述(「5 ラウンド」、「イテレーション」、「段階的磨き」)、archiver が 3 つの独立パターンと判定する可能性。解決: 言語を一致させる、または手動 alias
3. **パターンが 5 ステップ未満**——heuristic は少なくとも 5 つの sequential actions を要求。4 ステップ以内は method に抽出されない。解決: 本当に 3-4 ステップなら wiki の「best practice」、または concept としての方が適切

### 「候補メソッドが `_tentative/` に沈んだまま、確認を忘れた」

連続 5 回 Start Session 無応答 → `_meta/methods/_archive/` に自動 archive。**失われない**、しかし自動的に確認キューに戻ることもない。

復旧フロー:
```bash
mv _meta/methods/_archive/{method_id}.md _meta/methods/_tentative/{method_id}.md
```
次回 Start Session で確認ブロックに再出現します。

### 「ある concept の辺重みが突然急騰、ほぼすべての検索がそれを中心に回る」

Hub 問題。診断:

```bash
# ある concept の outgoing_edges 数を確認
grep -c '^  - to:' _meta/concepts/method/{concept_id}.md
```

20 本超の outgoing edges は hub の兆候。対処:

1. **分割**——この concept は実は 2-3 つの概念が誤って統合された可能性。元ファイルを削除、より細かい concept を手動で数個作成、archiver に次回 session で自動再接続させる
2. **permanence 昇格**——それが真にコアで辺が多いべき("user-core-workflow" のようなメタメソッド)なら、`permanence` を `identity` に昇格、不衰退に
3. **migration 再起動**——極端な場合、`uv run tools/migrate.py` で再スキャン。冪等、重複なし

### 「AUDITOR 巡査で '孤立辺' が赤標記された」

Orphan edge = `outgoing_edges` の `to:` が存在しない concept ファイルを指す(目標 concept を手動削除したが源 concept を同期更新しなかった可能性)。

**通常** archiver Phase 2 は SYNAPSES-INDEX 再構築時にこれらの辺を自動剪定します。AUDITOR が依然 flag する場合、archiver がそのステップまで実行していないことを意味——adjourn_completeness スコアを確認([auditor-eval-history.md](./auditor-eval-history.md) 参照)。

---

## 深堀りの読書 / Further Reading

プロダクト入口:

- [What is Life OS](../../getting-started/what-is-life-os.md) — Life OS 全体の位置付け
- [Quickstart](../../getting-started/quickstart.md) — 初回上朝フロー

同ディレクトリ ユーザードキュメント:

- [overview.md](./overview.md) — Cortex 総覧
- [hippocampus-recall.md](./hippocampus-recall.md) — Wave 2/3 はここの辺重みに沿って拡散
- [gwt-arbitration.md](./gwt-arbitration.md) — concept シグナルはどう salience 競争に参加するか
- [narrator-citations.md](./narrator-citations.md) — 奏折が concept をどう引用するか(`C:domain:concept_id` プレフィックス)
- [auditor-eval-history.md](./auditor-eval-history.md) — archiver Phase 2 の品質モニタリング

Spec 層(英語):

- `references/concept-spec.md` — schema、ヘブ型アルゴリズム、spreading activation ルール
- `references/method-library-spec.md` — method schema、promotion ladder、DISPATCHER 統合
- `references/cortex-spec.md` §Archiver Candidate Routing — 候補がどの layer に入るかの決定木
- `references/hippocampus-spec.md` §Wave 2/3 — 辺重みに沿った拡散方法
- `pro/agents/archiver.md` — Phase 2 の実際の書き込みフロー

---

**前ページ**: [hippocampus-recall.md — 跨 session 記憶検索](./hippocampus-recall.md)
**次ページ**: [narrator-citations.md — Narrator 引用と trace](./narrator-citations.md)

---

### 訳者注 / Translator's Note

本ドキュメントは中国語版 (`docs/user-guide/cortex/concept-graph-and-methods.md`) からの自動翻訳版です(2026-04-22 作成)。技術用語(concept, method, synapse, Hebbian, canonical, tentative, permanence, decay, activation, frame, hippocampus, archiver, DISPATCHER, ROUTER, SOUL, AUDITOR, RETROSPECTIVE, COGNITIVE CONTEXT 等)は原文の英語表記を保持しています。ヘブ型 (Hebbian) や脳科学由来の用語は専門用語として可能な限り英語併記とし、日本語文脈での可読性を優先しました。人間校正待ち。
