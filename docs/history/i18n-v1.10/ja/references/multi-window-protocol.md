---
spec_id: multi-window-protocol.v1
description: 1 つの vault を共有する複数の並行ターミナルウィンドウのためのプロトコル —— outbox クレーム規律（未決のまま 2 回の session 開始を生き延びる項目はない）、session ごとのコミットスコープ宣言（共有 vault でリポジトリ全体の git add -A は決して行わない）、pre-session 表示におけるクロスウィンドウ認識行。暗黙の「1 つの session が vault を所有する」前提を閉じる（issue #3 C2）。
status: active
authoritative: true
introduced_in: v1.10.0
referenced_by:
  - agents/retrospective.md (Mode 0 step 7 outbox merge + pre-session display)
  - agents/archiver.md (Phase 4 commit scoping)
  - references/data-model.md (§Constraints, outbox pattern)
---

# Multi-Window Protocol v1

実際の利用では、複数のターミナルウィンドウが同じ vault に対して並行に走る。outbox パターン（`references/data-model.md` §Constraints）は共有ファイル上の書き込み競合を既に防いでいるが、本番はそれがカバーしていなかった 3 つの障害モードを露呈した：outbox パッケージが複数の session 開始をまたいで未クレームのまま放置される（「どこか他の session の仕事」扱い）、クロスウィンドウのハンドオフが完全に失われる、そして 1 つのウィンドウのコミットが別のウィンドウの作業中ファイルを巻き込む。この spec は 3 つすべてを閉じる。

## Rule 1 · Outbox クレーム規律

すべての session 開始時（retrospective Mode 0 step 7）、通常のマージパスの後：

1. この boot でマージされ**なかった** outbox ディレクトリ（merge-lock を別ウィンドウが保持、manifest 不完全、またはマージエラー）は**未クレーム項目**である。その `<sid>` と経過時間（manifest の `adjourned` タイムスタンプから、manifest が読めない場合はディレクトリの mtime から）を記録する。
2. **4 時間**より古い未クレーム項目は briefing で提示しなければならない（MUST）：

   ```
   📮 Unclaimed outbox: <sid> (age 26h) — adopt (merge now) or archive (move to meta/outbox/.archived/)? [awaiting your decision]
   ```

3. **HARD RULE —— 明示的な決定なしに 2 回連続の session 開始を生き延びる項目はない。** 生存回数は、その項目の manifest に `seen_by: <this-session-start-date>` 行を追記して追跡する。2 回目の目撃時、briefing はその項目を `## 4. Today's Focus / decisions needed` にエスカレートする —— session はそれを 2 度目も「誰か他の人の仕事」として扱わない。
4. `adopt` = そのディレクトリの通常マージを今実行する。`archive` = `meta/outbox/.archived/<sid>/` へ移動する（保持であり削除ではない —— Security Boundary #1）。どちらの結果も決定である；スキップは決定ではない。

## Rule 2 · コミットスコープ宣言

1. session 開始時、各 session は自身の**書き込みパス**を宣言する —— `meta/runtime/<sid>/scope.md` に 1 行を書き込む：

   ```
   write_scope: [meta/outbox/<sid>/, projects/<bound-project>/, meta/runtime/<sid>/]
   ```

   デフォルトスコープは、outbox パターンが既に含意しているパスそのもの（自身の outbox + バインドされたプロジェクト + 自身の runtime ディレクトリ）である；宣言によって他のウィンドウから grep 可能になる。
2. **コミットは宣言されたパスのみをステージする。** 共有 vault での `git add -A` / `git add .` は session フロー（archiver Phase 4、/save、outbox-merge コミット）において禁止（FORBIDDEN）である。明示的なパスをステージする：`git add meta/outbox/<sid>/ meta/methods/...`。
   - 唯一の例外：session 開始時の **outbox マージコミット**（retrospective step 7）は、マージ自身が移動した特定のファイルをステージする —— 列挙であり、`-A` ではない。
3. session の宣言スコープ外のファイルをステージすることになるコミット → 停止し、スコープ外パスを列挙し、ユーザーに尋ねる。別のウィンドウの作業中の成果物が、無関係なコミットに相乗りすることは決してあってはならない。

## Rule 3 · クロスウィンドウ認識行

pre-session 表示（retrospective Mode 0 / Mode 1 の出力）は、作業ツリーにこの session の宣言スコープ外の未コミット変更が含まれるとき、1 行を含める：

```
🪟 Other work areas: N uncommitted path groups not in this session's scope (projects/other-proj/, meta/runtime/claude-.../) — not yours, do not stage.
```

機械的に計算される：`git status --porcelain` → 自身の `write_scope` 内のパスを除去 → 残りをトップレベルディレクトリでグループ化。残りがゼロ → 行なし（健全パスでは沈黙）。

## この spec がやらないこと

- 既存の 5 分間 `meta/.merge-lock` を超えるロックはなし —— git が並行性のバックストップであり続ける。
- クロスウィンドウのメッセージングバスはなし —— ハンドオフは outbox（永続的）を通す。`git stash` は決して使わない（本番の証拠：ウィンドウ間の stash/patch ハンドオフは完全に失われた；stash はクローンごとの working-tree 状態であり、他のウィンドウのフローにも同期にも不可視である）。
- Session Binding ルール（`hosts/CLAUDE.md`）の変更はなし —— 議論のスコープは無制限のまま；この spec が制約するのはデータ書き込みとステージングのみである。

## Eval アンカー

`evals/scenarios/v1.10-multi-window.md` —— dirty ツリーが重なる 2 つのシミュレート session → クロスステージングなし；未クレーム outbox は初回開始時に提示され、2 回目に決定を強制される。
