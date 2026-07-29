# Life OS 評価システム

固定シナリオを使用して Draft-Review-Execute と Six Domains ワークフローの出力品質をテストし、一貫性とコンプライアンスを定量化します。

## 使い方

### 手動テスト

Life OS スキルを Claude Code にインストールした後、各シナリオのユーザーメッセージを直接入力し、ワークフロー全体の出力を観察します。

### 自動テスト

Claude Code で `/run-eval` slash コマンドを実行します（退役した `evals/run-eval.sh` を置き換え —— v1.8.5 hook 層退役 + md-only 存在論的制約の一部）：

```
/run-eval                 # 全シナリオを実行
/run-eval resign-startup  # 名前 glob で単一シナリオを実行
```

`/run-eval` は `claude -p` バッチモードでシナリオを一つずつ実行し、出力を `evals/outputs/` に保存します。完全な手順は `.claude/commands/run-eval.md` を参照。

## ディレクトリ構成

```
evals/
├── README.md              # 本ファイル
├── scenarios/             # 固定テストシナリオ（*.md —— ルーティング、コンプライアンス、バージョン専用）
├── regression-fixtures/   # 回帰ケース fixture（*.md）
├── rubrics/               # 採点基準
│   ├── agent-output-quality.md    # エージェント出力品質
│   └── orchestrator-compliance.md # ワークフローコンプライアンス
└── outputs/               # テスト出力（gitignore対象）
```

## 評価の軸

1. **フォーマット準拠**: 各エージェントが指定された出力フォーマットに従っているか
2. **スコア分布**: すべてのスコアが7〜8点（忖度スコア検出）になっていないか
3. **Reviewer の実質性**: 常に承認していないか（ゴム印検出）
4. **情報隔離**: エージェントの出力にアクセスすべきでない内容が含まれていないか
5. **実行可能性**: アクション提案が実行可能なほど具体的か
6. **一貫性**: 同一シナリオを複数回実行した際にコア結論が一貫しているか
7. **快車道ルーティング**: 非意思決定リクエストが完全な朝議ではなく快車道を正しくトリガーするか
8. **ドメイン選択の正確性**: Router/Planner がシナリオに対して正しいドメインを選択しているか
9. **Wiki抽出品質**: Archiver が End Session 時に再利用可能な結論をwikiに抽出しているか
