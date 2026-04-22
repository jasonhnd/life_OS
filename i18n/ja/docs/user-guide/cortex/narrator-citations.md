---
translator_note: 自動翻訳 2026-04-22、人間校正待ち
---

# Narrator 引用と Trace · 捏造防止メカニズム / Narrator Citations & Trace

> パンくず: [← Cortex 総覧](./overview.md) · [← 製品入口:ユーザーガイド索引](../index.md)

> v1.7 へのアップグレード後、奏折には `[S:claude-20260419-1238]` や `[SOUL:risk-tolerance-v3]` のような角括弧注記が出現します。これは装飾でも、読むことの強制でもありません。システムが自身に課した**誠実さの約束**です:すべての実質的な主張は追跡可能なシグナルを指し示し、空から捏造するのではない。いつでも「この文を trace して」と言えば、システムは元の session / SOUL 次元 / concept ファイルの具体的内容を見せます。この層を **Narrator** と呼びます。

## 一文概説 / One-Line Overview

Narrator は ROUTER の**出力段階**です——内部シグナルをユーザー可読な Summary Report に翻訳し、同時に**各実質的主張に citation を付与**。Narrator 生成後、独立した **narrator-validator subagent** が逐句チェック:各 substantive claim は本当に signal registry のレコードを指しているか?引用内容は主張を支持しているか?不合格なら Narrator に書き直させる。最大 3 回、超えたら「無引用版」に退化。

このメカニズムが存在する唯一の目的: **AI が尤もらしい歴史を捏造するのを防ぐ**。

---

## なぜこの層を追加するのか / Why Add This Layer

### 発見された問題: Gazzaniga 左脳解釈器 (Left-Brain Interpreter)

神経科学者 **Michael Gazzaniga** の有名な実験:てんかん患者の脳梁を切断(左右脳を分離)、右脳に一枚の絵(「雪地」)、左脳に別の絵(「鶏の足」)を見せる。患者に左手(右脳制御)と右手(左脳制御)でそれぞれペア画像を選ばせる。

結果: 右手が「鶏」、左手が「シャベル」——見た 2 枚に対応。しかし「なぜシャベルを選んだ?」と尋ねると、**左脳の言語野がその場で完璧に合理的な物語を捏造**:「鶏の糞をかき集めるため。」

患者は自分が雪地を見ていないことを**知らない**。見えた情報(鶏)から合理的説明を**逆算**し、**本気でそれを信じる**。

**これは AI の核心的失敗モード**です。言語モデルは「知っている」と「捏造」を区別せず、流暢で自信のある物語が完全に捏造である可能性があります。Life OS の意思決定エンジンの文脈で、システムが以下のように言うなら:

> 「前回類似の決定をした際、このリスクを考慮し、最終的に保守路線を選択しました。」

しかし実際には:
- 前回の決定が存在しない
- または存在するが考慮したのはそのリスクではない
- または考慮したが選んだのは保守路線ではない

**あなたは信じて**、この「偽歴史」を基に新しい決定を下す。これがシステミックな汚染です。

### Narrator の構造的回答

**解法は「AI により努力して捏造するなと要求する」ではありません**——信頼できません。解法は Narrator の出力段階を分割することです:

1. **Narrator 書く**——各 substantive claim は `[signal_id]` 引用を必ず付ける
2. **Validator 審査**——独立した subagent(`Read` 権限のみ)が signal registry を確認:この ID は存在するか?引用内容は主張を支持するか?
3. **不合格なら書き直し**——最大 3 回。超えたら「無引用の元 Summary Report」にフォールバックし、AUDITOR に記録

**Narrator は Validator をバイパス不可**——「trust me モード」なし、Validator を切るユーザーフラグなし。これは Cortex の構造的防衛線で、ソフトコンベンションではありません。

---

## ユーザー側に見えるもの / What the User Sees

### シナリオ A: 奏折の引用

ROUTER が Step 7 で Summary Report を書き、Step 7.5 で Narrator が citation を追加して書き直します。最終的に見えるもの:

```markdown
## 推奨方向

あなたの過去の "passpay-v06-refinement" session [S:claude-20260419-1238] に基づき、
今回の決定は類似の 5 ラウンドイテレーションパターンを示し、GOVERNANCE は当時 5/10
[D:passpay-governance-score] をつけました。

この方向性はあなたの「リスク許容度」次元(confidence 0.72)[SOUL:risk-tolerance-v3]
と一致しますが、「家庭優先よりもキャリア」(core, confidence 0.82)
[SOUL:family-over-career-v2] に挑戦——REVIEWER は tier_1_conflict と標記済み。

Finance と Execution の分差は 4 点 [D:finance-score-6][D:execution-score-2]、
COUNCIL 討論をトリガーしました。
```

各角括弧が citation です。プレフィックスの意味:

| プレフィックス | 意味 | 例 |
|------|------|------|
| `S:` | session_id(単回 session) | `S:claude-20260419-1238` |
| `D:` | 具体的 domain スコアまたはフィールド | `D:passpay-governance-score` |
| `SOUL:` | SOUL 次元 | `SOUL:risk-tolerance-v3` |
| `C:` | 概念ノード | `C:method:iterative-document-refinement` |
| `W:` | Wiki エントリ | `W:finance/compound-interest` |
| `P:` | user-patterns.md パターン | `P:avoids-family-topic-on-weekends` |

**プレフィックスは固定**——Narrator は新しいプレフィックスを発明不可。あるシグナル源がこの 6 つのいずれにもマッピングできない場合、それは**引用不可**、したがってこの substantive claim も**言ってはならない**。

### シナリオ B: Trace UX · 文を疑う

以下を見たとします:

> 「あなたの過去の 'passpay-v06-refinement' session [S:claude-20260419-1238] に基づき、今回の決定は類似の 5 ラウンドイテレーションパターンを示し」

確認したい。直接言う:

> trace [S:claude-20260419-1238]

または自然言語で:

> この文はどこから来た?

または

> 根拠は?

システム応答:

```
📎 Trace for: "Your past passpay-v06-refinement session shows a similar 5-round iteration pattern"

Cited signals:
1. S:claude-20260419-1238
   Source: _meta/sessions/claude-20260419-1238.md
   Content match: "Session ran 5 revision rounds on payment gateway spec.
     Each round tightened governance controls. Final GOVERNANCE score
     5/10 due to incomplete fraud-response plan."
   Produced by: hippocampus (Step 0.5 Wave 1)

2. D:passpay-governance-score
   Source: session D-scores extracted by ROUTER at Step 7
   Value: 5 (threshold for flag: < 6)
   Produced by: governance_agent

Confidence: groundedness_score = 1.0 (both citations resolve, content supports claim)
```

**Trace に LLM 再生成なし**——「literal excerpt + metadata」のみ。さもなくば「trace が trace を解釈、trace が trace 解釈 trace を解釈……」の再帰 confabulation loop になります。

### シナリオ C: カテゴリ概要 Trace

**あるカテゴリのシグナルが本決定でどう機能しているか**の全貌を知りたい:

> この Summary Report が引用した SOUL 次元は?

システム応答:

```
📎 Category trace: SOUL dimensions that influenced this Summary Report

1. SOUL:risk-tolerance-v3 (core, confidence 0.82)
   Referenced by: narrator (×2), governance_agent (×1)
   Source text: SOUL.md § Risk attitude

2. SOUL:family-over-career-v2 (core, confidence 0.82)
   Referenced by: narrator (×1), reviewer (×1)
   Source text: SOUL.md § Family priority

3. SOUL:evidence-discipline (secondary, confidence 0.61)
   Referenced by: narrator (×1), execution_agent (×1)
   Source text: SOUL.md § Evidence discipline
```

### シナリオ D: connective tissue の trace を尋ねる

一部の文は**接続組織** (discourse glue)——転換、冒頭、フレーミング的記述——事実的内容を持たず、Validator はスキップします(§3 §Substantive vs Connective 参照)。これらの文を trace すると:

> trace "Let me walk through this"

システム応答:

```
That sentence is connective tissue (a transition / framing / rephrasing),
not a grounded claim. No signal stands behind it. If you want to trace a
substantive claim in the same report, let me know which one.
```

これは「システムが trace リクエストに応じるため、本来事実的内容のない文を支えるためにシグナルを逆向きに捏造する」——それこそが真の Gazzaniga ループ——を防ぎます。

---

## Substantive vs Connective · 何が引用を要するか / What Needs a Citation

Narrator 出力の各文は分類されます:

### Substantive(引用必須)—— この文を削除すると事実情報が失われる

- 歴史的記述: 「前回あなたは X を……」
- パターン的記述: 「あなたは……の傾向がある」
- SOUL: 「これはあなたの Y 価値観と一致」
- 決定含意: 「GOVERNANCE の懸念は……」
- 跨 session 関連: 「これはあなたの Z プロジェクトの決定と関連」
- 数値またはスコア主張: 「Finance は 6/10 をつけた」
- 役割帰属: 「ADVISOR は感情重みを標記した」

### Connective(引用不要)—— 単なる discourse glue

- 過渡: 「一歩ずつ説明しましょう……」
- フレーミング: 「分析からすると……」
- メタコメント: 「簡単にまとめると……」
- 冒頭/結末: 「では、この件を見てみましょう……」
- 純粋な言い換え: 「言い換えれば……」

**判定ルール**: この文を削除して、残りの文が事実的内容を失うか?失う → substantive、citation 必須。失わない → connective、スキップ。

---

## Validator はどう動くか / How the Validator Works

narrator-validator は独立した Claude Code subagent(**Anthropic Haiku 外部 API ではない**)、`Read` 権限のみ、sonnet モデル。

### 入力
- Narrator 出力の完全 markdown
- Signal source registry(本 session 蓄積の全 signal)

### 逐句フロー

各文について:
1. **分類**: substantive か connective?§3 ルール使用
2. connective → skip
3. substantive:
   1. すべての `[signal_id]` を抽出
   2. 各 citation について:
      - プレフィックスは 6 つの合法プレフィックス内か?否 → `format_error`
      - `signal_id` は registry 内か?否 → `missing_signal`
      - 引用対象のファイル/フィールドを読み、**主張が内容に支持されるか**検証?否 → `unsupported_claim`
   3. substantive だが**ゼロ citation** → `missing_signal` (tagged "no citation")

### 出力 · スコアリング

```yaml
validation:
  total_citations: 12
  valid: 11
  invalid:
    - position: 842
      citation: "[SOUL:something-else]"
      reason: unsupported_claim
      claim_text: "This aligns with your value of X"
  groundedness_score: 0.92
```

### 閾値

**`groundedness_score ≥ 0.9`** で合格。0.9 未満 → narrator が書き直し(**最大 3 回**)、validator のエラーフィードバックと推奨引用を付けて。

### 3 回書き直して合格しない場合?

**un-cited Summary Report** にフォールバック(Step 7 の元出力、Narrator 書き直し層を通らない)、AUDITOR が `narrator_failed_after_3_attempts` flag を eval-history に記録。**ユーザーは依然として奏折を受け取る**——引用なしで。

---

## Signal Source Registry

Narrator と Validator が共同依存する「真実の源」:本 session のすべてのシグナルの id と指向。

**registry は ROUTER が Step 7.5 前に組み立てる**:

| タイミング | 追加されるシグナル |
|------|------------|
| Step 0.5 | hippocampus / SOUL check / concept lookup のシグナル |
| Step 5(6 領域並列) | 各領域報告が生成する domain score |
| Step 6(COUNCIL トリガー時) | COUNCIL 討論のシグナル |
| Step 4 (DISPATCHER) | 「既知前提」として注入される wiki / pattern 引用 |

**registry は append-only**——session 途中でシグナルを削除しない。

形式例:

```yaml
signal_sources:
  - id: S:claude-20260419-1238
    type: session
    file: _meta/sessions/claude-20260419-1238.md
    producer: hippocampus
  - id: SOUL:risk-tolerance-v3
    type: soul_dimension
    ref: SOUL.md#risk-tolerance
    producer: soul_check
  - id: C:method:iterative-document-refinement
    type: concept
    file: _meta/concepts/method/iterative-document-refinement.md
    producer: concept_lookup
  - id: D:GOVERNANCE-score-5
    type: domain_score
    value: 5
    producer: governance_agent
  - id: W:finance/compound-interest
    type: wiki
    file: wiki/finance/compound-interest.md
    producer: wiki_index
  - id: P:avoids-family-topic-on-weekends
    type: pattern
    ref: _meta/user-patterns.md#avoids-family-topic-on-weekends
    producer: retrospective
```

---

## Narrator が介入しない場面 / When Narrator Doesn't Engage

3 つのシナリオ、**Narrator は完全にスキップ**:

| シナリオ | Narrator の挙動 |
|------|-------------|
| **ROUTER 直接処理**(雑談、翻訳、簡単なクエリ) | **介入せず**——signal registry 空、ROUTER が直接応答 |
| **Express 快速レーン**(領域分析、意思決定なし) | **hippocampus / SOUL / concept 引用のみ検証**、registry に domain score がないため |
| **STRATEGIST 群賢堂**(哲学的対話、意思決定なし) | **介入せず**——STRATEGIST の出力は思想家の独立叙述、書き直し・引用追加なし |

理由: これらのシナリオでは検証可能な「事実的主張」が生まれない——雑談はシグナルなし、Express は完全な domain 分析なし、STRATEGIST は開放的対話。強引に citation を付けてもノイズになるだけ。

---

## ユーザーアクション · 介入方法 / User Actions

### 1. 任意の角括弧引用を Trace

```
trace [S:claude-20260419-1238]
この文はどこから来た?
根拠は?
```

システムは元の引用と内容断片を返します、**LLM 解釈なし**——trace は「反捏造」の最後の防線、根拠必須。

### 2. 引用に同意しない?直接反論

trace 後、システムが引用した session summary が実は**誤読**(GOVERNANCE が 5/10 をつけた理由は別の問題、fraud-response ではない)と判明:

> この trace は間違い。S:claude-20260419-1238 の GOVERNANCE の 5/10 は X が理由、fraud-response ではない

ROUTER は:
- あなたの反論を本 session の Summary Report 修正段に記録
- session 終了時の archiver Phase 2 で、「ユーザーが引用に反論」イベントを AUDITOR の `citation_groundedness` 次元に入れる
- 同一シグナルが複数回反論されると、AUDITOR は eval-history で flag:「この session summary は書き直しが必要かも」

### 3. 無引用版を要求

まれに角括弧注記が五月蝿く、クリーンな叙述が欲しい場合:

> 引用なしの奏折をくれ

ROUTER は Step 7 の元 Summary Report を出力(Narrator 書き直しを経ず)。ただし注意: **これは一回性のリクエストで永続設定ではない**。次回の決定では Narrator は依然動作します——Narrator のコア価値は構造的な捏造防止にあり、オプショナルな美化ではないからです。

### 4. Validator をバイパス不可

Narrator と Validator の間には**ユーザーフラグで閉じる手段はない**。理由:

- セキュリティモデル: Validator を切りたい動機の 99% は「角括弧を見たくない」——Cortex の事実ゲートキーピングを脅かすべきではない
- 本当に角括弧が嫌なら、解法は前条(一回性で un-cited 版を取得)、Validator を永続的に切ることではない

**唯一の永続閉鎖**: `_meta/cortex/config.md` を編集し `narrator_validator_enabled: false`。Narrator 出力の citation が**検証されない**——角括弧は見えますが、間違っている可能性あり。**推奨しません**。

---

## よくある質問 / Common Questions

### Citation 失敗率は何%が正常?

- **`citation_groundedness ≥ 9/10`**:安定状態の目標
- **`regeneration_count = 0`**: 全朝議 session の 80% 超が一発通過すべき
- 任意の session で `citation_groundedness < 7/10`: AUDITOR が品質イベントと標記
- 毎週 `regeneration_count > 1` のトレンド: AUDITOR が "narrator drift" と標記

これらの指標は `_meta/eval-history/{date}-{project}.md` に記録され、RETROSPECTIVE Mode 0 がスキャンします([auditor-eval-history.md](./auditor-eval-history.md) 参照)。

### Validator になぜ haiku でなく sonnet?

ユーザー決定 #9 の明確な結論:**Claude Code subagent を使用、外部 Anthropic Haiku API は使わない**。

理由:
- **外部コストゼロ**——subagent は既に支払い済みの Claude プラン枠内で実行、別の Haiku API アカウント不要
- **API key 管理なし**——外部キー、rotation、予算なし
- **Life OS の立場と合致**——すべての知性は session 内、外部依存を導入しない
- **sonnet で十分**——citation 検証には Opus は不要、Haiku の安さも不要。latency 予算内(validator 1 ラウンド 1–3 秒)

### Validator 自身はチートできるか?

Validator は `Read` 権限のみ、signal registry を改変不可。失敗モードは「valid な claim を invalid と判定」(過剰警戒)または「invalid な claim を valid と判定」(見逃し)のみ。両者とも痕跡が残る:

- 過剰警戒 → Narrator が書き直しループに強制、最終 3 回全滅なら AUDITOR が `narrator_failed_after_3_attempts` を標記
- 見逃し → ユーザー trace 時「⚠️ signal no longer resolvable」や内容が明らかに主張を支持しない trace を見て、ユーザーが反論 → AUDITOR が `citation_groundedness` 低を標記

長期的に、AUDITOR は Validator 自身に二階監視をもつ——これが eval-history の価値です([auditor-eval-history.md](./auditor-eval-history.md) 参照)。

### システムがあることを言いたいがシグナルがない場合は?

**言わない**。

Narrator の invariant は:「シグナルがない → substantive claim なし」。ソフトコンベンションではない——Validator は「ゼロ citation の substantive 文」を直接 `missing_signal` と標記、Narrator は書き直しを強制、**その文を削除**するか、**支持する signal を見つけて引用**する。

本当に支持 signal が見つからないなら、そもそも言うべきではない——それは AI が知らない領域を埋めている。

### Narrator は Validator を通すためだけに関係ない signal を適当に貼らないか?

Validator は **「signal 存在」**だけでなく、**「content が claim を支持」**も確認。支持しない場合 `unsupported_claim` エラーを返し、Narrator が書き直しを続行。

偽 signal を貼るのは楽な道ではなく、**より重い罰**です。

### この層はどれくらい latency を追加する?

| 段階 | 予算 |
|------|------|
| Narrator 生成(ROUTER 内部の書き直し段階) | 2–5 秒 |
| Validator スキャン(1 回) | 1–3 秒 |
| 書き直し + 再検証ループ | 1 ラウンド +2–5 秒 |
| **最悪の 3 回リトライ合計** | **15 秒** |

全朝議 1 決定は元々 6 領域 + 監査 + アーカイブを走るので、15 秒増はノイズの範囲。Express と direct-handle は Narrator を通らず影響なし。

### Citation 密度が高すぎて奏折が法律文書のように読めるときは?

**v1.7 Phase 2** は per-substantive-claim 粒度——各 substantive 文に少なくとも 1 つの citation が必要。実使用で **「スタンプを押されたように感じる」** 場合、ユーザー決定は調整路径を予約: 粒度を **per-paragraph に粗粒化**(段落ごとに 1 引用)——**捏造防止保証は弱まらない、registry は依然完全**。

この調整は v1.7 稼働後 3 ヶ月程度で実ユーザーフィードバックに基づき決定。Spec では open question で、固定契約ではありません。

---

## トラブルシューティング / Troubleshooting

### 「Trace で '⚠️ signal no longer resolvable' と表示」

ある `signal_id` が指すファイルが削除または改名されました。一般的原因:

- `_meta/sessions/` 内のある歴史 session ファイルを手動削除
- Git ブランチ切り替え後のインデックス不整合
- 概念が `_meta/concepts/_archive/` に retire
- SOUL 次元が改名または削除

**trace の元 citation は保持**——**元々どこを指していたか**を知っている、ただそのファイルが一時/永続的にない。誤削除の場合は git 履歴から復元、アーカイブなら `_archive/` 内で手動確認。

### 「Narrator が頻繁に書き直しをトリガー、session が遅く感じる」

eval-history を確認:

```bash
grep -r "regeneration_count" _meta/eval-history/ | tail -20
```

`regeneration_count > 1` の比率が高い(30% 超)場合、可能な原因:

1. **Signal registry 過小**——session に十分な hippocampus / concept / SOUL シグナルがなく、Narrator が言いたいことが signal 支持を超える。解決: hippocampus を先に良く動かす(migration が完全に実行されていない、INDEX が古い可能性)
2. **Narrator prompt の調整が必要**——連続 2 週間 `regeneration_count` トレンド > 1、AUDITOR が "narrator drift" を標記([auditor-eval-history.md](./auditor-eval-history.md) §7.3 参照)
3. **Validator 過厳**——引用 signal は registry に存在するが Validator が claim 支持不十分と判定。これらのケースは eval-history に `unsupported_claim` violation type として残り、後続の調整に役立つ

### 「角括弧を見たくない、クリーンな叙述が欲しい」

- **一回性**: `引用なしの奏折をくれ` → ROUTER が Step 7 元出力を返す
- **引用表示の永続閉鎖、検証保持**: v1.7 はサポートなし(角括弧は citation の物理担体、なくては trace 不可)
- **メカニズム全体の永続閉鎖**: `_meta/cortex/config.md` で `narrator_validator_enabled: false`。**推奨しません**——捏造防止の構造的保証を外すことに相当

### 「Citation に `SOUL:X` が表示されるが SOUL.md にその次元がない」

trace 結果で出てきた場合、確認:

1. **バージョン不一致**: `SOUL:risk-tolerance-v3` の `-v3` サフィックスは dimension の版改訂番号。SOUL 次元を書き直したが version を更新していない場合、引用は**旧版本**を指す。解決: 次元書き直し時に version 番号を手動 bump、または SOUL の自動書き込み機構で v4 を生成
2. **registry stale**: signal registry は session-scoped、ある session の registry がディスクに書かれた後 SOUL 自体が後続で改変されると、trace 時に「⚠️ signal no longer resolvable」と表示——これは正常挙動
3. **プレフィックスエラー**: Narrator は新プレフィックスを発明しないべきだが、非標準プレフィックス(`SOULS:` や `soul:`)が出現した場合、Validator が `format_error` と標記し書き直しトリガー。それでも見える場合、Validator がバイパスされた可能性——`_meta/cortex/config.md` で切られていないか確認

---

## 深堀りの読書 / Further Reading

同ディレクトリ ユーザードキュメント:

- [overview.md](./overview.md) — Cortex 総覧
- [hippocampus-recall.md](./hippocampus-recall.md) — `S:` プレフィックスが指す session summary の出所
- [concept-graph-and-methods.md](./concept-graph-and-methods.md) — `C:` プレフィックスが指す concept ノード
- [gwt-arbitration.md](./gwt-arbitration.md) — signal registry が Step 0.5 で hippocampus/concept/SOUL シグナルをどう蓄積するか
- [auditor-eval-history.md](./auditor-eval-history.md) — `citation_groundedness` 次元の長期モニタリング

Spec 層(英語):

- `references/narrator-spec.md` — 完全 spec: substantive/connective ルール、validator アルゴリズム、trace UX
- `references/eval-history-spec.md` §5.10 — `citation_groundedness` 採点基準
- `references/cortex-spec.md` §Grounded Generation — なぜ Gazzaniga が Cortex 設計の中核的隠患か
- `pro/agents/narrator-validator.md` — validator subagent 定義

その他:

- `pro/agents/router.md` — Narrator の挙動は ROUTER に住む(独立 agent ではない)
- `devdocs/architecture/cortex-integration.md` — Step 7.5 挿入の位置

---

**前ページ**: [concept-graph-and-methods.md — 概念グラフとメソッドライブラリ](./concept-graph-and-methods.md)
**次ページ**: [gwt-arbitration.md — 顕著性競争](./gwt-arbitration.md)

---

### 訳者注 / Translator's Note

本ドキュメントは中国語版 (`docs/user-guide/cortex/narrator-citations.md`) からの自動翻訳版です(2026-04-22 作成)。技術用語(Narrator, Validator, substantive/connective, signal registry, citation, trace, groundedness, confabulation, Gazzaniga Left-Brain Interpreter, ROUTER, COUNCIL, AUDITOR, RETROSPECTIVE 等)は原文の英語表記を保持しています。Gazzaniga の左脳解釈器の説明は神経科学領域の標準用語ですが、日本語文脈での理解を優先し読解可能な表現としました。人間校正待ち。
