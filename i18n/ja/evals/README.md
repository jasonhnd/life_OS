# Life OS 評価システム

固定シナリオを使用して Draft-Review-Execute と Six Domains ワークフローの出力品質をテストし、一貫性とコンプライアンスを定量化します。

## 使い方

### 手動テスト

Life OS スキルを Claude Code にインストールした後、各シナリオのユーザーメッセージを直接入力し、ワークフロー全体の出力を観察します。

### 自動テスト

```bash
# 全シナリオを実行
./evals/run-eval.sh

# 単一シナリオを実行
./evals/run-eval.sh resign-startup
```

スクリプトは `claude -p` を使用してシナリオを一つずつ実行し、出力を `evals/outputs/` ディレクトリに保存します。

## ディレクトリ構成

```
evals/
├── README.md              # 本ファイル
├── run-eval.sh            # 自動テストスクリプト
├── scenarios/             # 固定テストシナリオ
│   ├── resign-startup.md  # 退職して起業（Six Domains 全体）
│   ├── large-purchase.md  # 高額購入（FINANCE + EXECUTION + GOVERNANCE）
│   └── relationship.md    # 対人関係（PEOPLE + INFRA + GOVERNANCE + GROWTH）
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
