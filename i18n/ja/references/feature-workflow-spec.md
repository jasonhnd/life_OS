---
spec_id: feature-workflow-spec.v1
description: lifeos の機能設計ワークフロー —— Specify → Evals scenarios 定義 → Implement → Verify（4 段階）。"Evals scenarios 定義" 段階は HARD —— planner は複雑さに関わらず実装開始前に evals scenarios を planning frontmatter にリスト必須、そうでなければ dispatcher が受け付けない。tinyhumansai/openhuman AGENTS.md §"Feature design workflow" の planning rule から借用。
status: active
authoritative: true
source_attribution: tinyhumansai/openhuman @ b7b8ba6, AGENTS.md:507-521 (Feature design workflow + 計画ルール "E2E scenarios up front")
introduced_in: v1.8.7
referenced_by:
  - pro/agents/planner.md (evals_scenarios 必須フィールド)
  - pro/agents/dispatcher.md (ディスパッチ前検証)
  - pro/agents/reviewer.md (承認前 scenarios 完備性検証)
---

# 機能ワークフロー仕様 v1

lifeos の機能/変更設計は 4 段階ワークフローに従う。硬性要件：**scenarios は実装開始前に定義される**、後付けではない。scenarios のない計画文書は不完全；dispatcher が拒否する。

## 背景

以前 lifeos の計画規約は：planner が計画文書を書く → reviewer が承認 → dispatcher が domains に派遣 → reviewer final → archiver。eval-first 原則は暗黙：planner は**テスト scenarios を定義すべき**、しかし frontmatter フィールドで強制されなかった。

結果：複雑な計画文書が時に evals なしで ship；lifeos の eval-first 哲学は願望のままだった。v1.8.7 はそれを契約にする。

## 4 つの段階

```
1. Specify          → Subject + 背景 + スコープ含む計画文書を書く
2. Evals 定義       → frontmatter evals_scenarios: [...] 非空（HARD）
3. Implement        → dispatcher の順序で 6 domains が実行
4. Verify           → reviewer final + AUDITOR Mode 3 が scenarios に対して相互検査
```

段階 2 が新しい HARD 要件。

## evals_scenarios frontmatter フィールド（HARD）

すべての計画文書（dispatcher → domains → reviewer-final を通る文書）の frontmatter に必須：

```yaml
---
subject: <one-line>
background: |
  <multi-line context>
scope: [...]
evals_scenarios:
  - <path or N/A: reason>
  - <path or N/A: reason>
---
```

**各 scenario エントリで許容される値**：

1. **既存 fixture へのパス**：`evals/scenarios/<name>.md` —— fixture ファイルが存在し、この計画文書を逆参照していること必須
2. **N/A 理由付き**：`N/A: docs-only` / `N/A: pure-translation` / `N/A: i18n-mirror-update` —— 本当にランタイムテストが不要な変更用（理由は許容列挙の 1 つ必須；任意の "N/A: 後述参照" は拒否される）
3. **将来コミットメント**：`TBD: evals/scenarios/<name>.md (commit-by: <PR/issue/date>)` —— 期限付きエスケープハッチ；dispatcher は受諾するが reviewer-final は TBD 解決まで常に拒否

**許容されない値**：

- 空リスト `[]` —— テスト定義なしで実装は進められない
- `evals_scenarios:` キーが全く欠落 —— 空と同じ
- `N/A: see below` / `N/A: TBD` 列挙理由なし
- 存在しない fixture へのパス（dispatcher がパス存在を検証）

## 許容される N/A 理由列挙

```yaml
N/A: docs-only           # 純粋ドキュメント、挙動変化なし
N/A: pure-translation    # 既存 EN コンテンツの i18n/zh または i18n/ja 翻訳
N/A: i18n-mirror-update  # ドリフトしたミラーを EN コンテンツに復元（新挙動なし）
N/A: typo-fix            # 単語/単行修正、意味変化なし
N/A: cleanup-only        # デッドコード/未使用参照の削除、挙動変化なし
```

列挙外の理由 → dispatcher 拒否 `F4 SCOPE_FAILURE: invalid N/A reason；列挙から選ぶか scenario を書く`。

## 適用範囲（適用外）

### 適用（HARD 強制）

- ROUTER が PLANNER にエスカレートする計画文書（full deliberation パス）
- agent 挙動または spec セマンティクスに触れる `_meta/rfc/v<X.Y>-*.md` 下の RFC
- 新 agent（`pro/agents/<new>.md`）—— agent の主要挙動を検証する fixture が少なくとも 1 つ必要
- SKILL.md または pro/CLAUDE.md に導入される新 HARD RULE

### 適用外（範囲外）

- ROUTER "Handle Directly" パス —— 短い会話応答
- Express Analysis パス —— domains は走るが PLANNER ステップなし（ROUTER の簡潔レポートでカバー）
- ノート / ジャーナルエントリ / SOUL スナップショット / sessions
- 既存テストパスのバグ修正（既存 fixture がカバー；planner は既存パス参照だけで十分）

## Dispatcher 検証

Dispatcher が下流実行のために計画文書を受け付ける前：

1. 計画文書 frontmatter を読む
2. `evals_scenarios:` キーを探す
3. 上記ルールで検証：
   - 非空リスト
   - 各エントリは path-existing OR 許容-N/A OR TBD-with-deadline
4. 検証失敗時：
   - `F4 SCOPE_FAILURE: planning doc <path> missing or invalid evals_scenarios` 出力
   - dispatch を停止
   - 特定失敗と共に planner に戻す（planner が再試行；ユーザエスカレーション前最大 3 サイクル）

## Reviewer-final 検証

6 domains 完了し reviewer-final 実行後：

1. 計画文書 frontmatter `evals_scenarios:` を読む
2. 各 `evals/scenarios/<name>.md` エントリ：fixture 存在を検証し、その期待挙動がこのセッションの実行で実証されたことを検証
3. `TBD:` エントリ：拒否 `F10 RESPONSIBILITY_FAILURE: TBD scenarios がリリース前に解決されていない；このセッションで fixture を着地させるか follow-up issue に分割`
4. `N/A:` エントリ：受諾するが AUDITOR Mode 3 レビュー用に audit trail に記録

## アンチパターン

正しく見えるが実は回避策の：

### アンチパターン 1：キャッチオール "smoke" fixture

```yaml
evals_scenarios:
  - evals/scenarios/smoke-test.md   # 実際は空 / "TODO" と書いてある
```

Dispatcher は fixture ファイルが非自明な内容（≥30 行または ≥1 受諾基準）を持つことを必ずチェック —— そうでなければ空として扱う。

### アンチパターン 2：無関係な fixture 流用

```yaml
evals_scenarios:
  - evals/scenarios/start-session-compliance.md   # しかし本 PR は archiver about、start session ではない
```

Reviewer-final は fixture の `applies_to:` frontmatter を PR スコープと対比し不一致を検出すべき。不一致 → 拒否。

### アンチパターン 3：曖昧な N/A

```yaml
evals_scenarios:
  - N/A: trust me
```

許容列挙にない → dispatcher 拒否。

### アンチパターン 4：フィールド全欠落

```yaml
subject: ...
background: ...
# evals_scenarios 未存在
```

フィールド欠落 = eval 欠落。Dispatcher は空リストとして扱う → 拒否。

## 例（正しい）

### 例 1：新 fixture 付き新機能

```yaml
subject: v1.8.7 C6 — gotchas + memory-keeper
evals_scenarios:
  - evals/scenarios/v1.8.7-c6-memory-keeper-seed.md
  - evals/scenarios/v1.8.7-c6-archiver-phase5.md
```

### 例 2：純粋ドキュメント変更

```yaml
subject: references/concept-spec.md の typo 修正
evals_scenarios:
  - N/A: typo-fix
```

### 例 3：i18n ミラー更新

```yaml
subject: セクション並び替え後 i18n/zh/references/agent-spec.md を EN に復元
evals_scenarios:
  - N/A: i18n-mirror-update
```

### 例 4：scenarios コミットされたが fixture は同セッションで着地

```yaml
subject: v1.8.7 F11 — i18n diff parity
evals_scenarios:
  - evals/scenarios/v1.8.7-f11-check-9-pass.md
  - evals/scenarios/v1.8.7-f11-check-9-warn-drift.md
  - evals/scenarios/v1.8.7-f11-check-9-block-future.md (TBD: 本リリースは WARN のみ追加、BLOCK ケースは v1.8.8 で着地)
```

TBD エントリは明示的締切（v1.8.8）。Dispatcher は受諾；reviewer-final は v1.8.8 follow-up 用に TBD をフラグ付け。

## 参照

- `_meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.5 B5
- パターン源：`tinyhumansai/openhuman` AGENTS.md:507-521（Feature design workflow + 計画ルール）
- 連携：`pro/agents/planner.md`（テンプレート定義）、`pro/agents/dispatcher.md`（検証ロジック）
- 関連：`references/agent-spec.md`（agent 定義もこの規律から恩恵を受ける）
