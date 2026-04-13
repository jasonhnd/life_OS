# Wiki 仕様書

Wiki はシステムのナレッジアーカイブであり、世界に関する再利用可能な結論の生きたコレクションです。second-brain の `wiki/` ディレクトリに格納されます。

## 位置づけ

| ストレージ | 記録する内容 | 例 |
|---------|----------------|---------|
| `decisions/` | 何を決定したか（具体的、タイムスタンプ付き） | "2026-04-01: 信託構造の採用を決定" |
| `user-patterns.md` | 何をするか（行動パターン） | "財務面の検討を避ける傾向がある" |
| `SOUL.md` | 自分は誰か（価値観、性格） | "リスク許容度: 中〜高" |
| `wiki/` | 何を知っているか（再利用可能な結論） | "日本のNPO融資に貸金業法の免除はない" |

SOUL は人格を管理します。Wiki は知識を管理します。両者を混同してはなりません。

---

## 原則

1. **ゼロから成長する** — wiki/ は空の状態から始まります。初期化は不要です。
2. **エビデンスベース** — すべてのエントリは、裏付けとなる decisions/experiences にリンクします。
3. **ユーザー確認制** — システムが候補を提案し、ユーザーが確認します。自動書き込みはありません。
4. **タイトル＝結論** — すべてのエントリのタイトルは、トピックではなく結論そのものでなければなりません。
5. **1ファイル1結論** — 複数トピックのまとめファイルは作成しません。

---

## エントリフォーマット

各 Wiki エントリは独立した Markdown ファイルです：

```yaml
---
domain: "[ドメイン名]"       # finance / startup / health / legal / tech / project-name...
topic: "[短い識別子]"
confidence: 0.0               # 0-1, 自動計算
evidence_count: 0             # 裏付けとなる decisions/experiences
challenges: 0                 # 矛盾する experiences
source: dream                 # dream / session / user
created: YYYY-MM-DD
last_validated: YYYY-MM-DD
---
```

### 結論
[一文 — 再利用可能な要点]

### 推論
[この結論を裏付けるエビデンスとロジック]

### 適用場面
[どのようなシナリオでこのエントリを想起すべきか]

### ソース
[どの決定、セッション、または経験がこの知識を生み出したか]

---

## タイトル規約

タイトルはトピックではなく結論でなければなりません：

- ✅ "日本のNPO融資に貸金業法の免除はない"
- ❌ "NPO 貸金業法の調査"
- ✅ "MVPは製品の品質ではなく需要を検証する"
- ❌ "MVP方法論メモ"
- ✅ "16:8 間欠断食は自分に合っている"
- ❌ "間欠断食の調査"

ファイルを開けばすぐに答えがわかります — 全文を読む必要はありません。

---

## ファイルパス規約

```
wiki/{domain}/{topic}.md
```

例：
- `wiki/finance/lending-law-npo.md`
- `wiki/startup/mvp-validation.md`
- `wiki/health/intermittent-fasting.md`
- `wiki/gcsb/biz-plan-versions.md`

---

## 確信度の計算

SOUL.md と同じ計算式：

```
confidence = evidence_count / (evidence_count + challenges × 2)
```

| 確信度 | 意味 | システムの動作 |
|------------|---------|-----------------|
| < 0.3 | 暫定的、データポイントが少ない | INDEX に表示されるが、ルーティング時には参照されない |
| 0.3 – 0.6 | 中程度のエビデンス | 門下省が整合性チェック時に参照 |
| 0.6 – 0.8 | 十分に確立 | 丞相がユーザーに既存の知識を通知 |
| > 0.8 | 深く検証済み | システム全体で参照 — 意思決定ルーティングを加速可能 |

---

## エントリのライフサイクル

```
1. 🌱 候補 — DREAM が N3 ステージで提案、またはセッション中に抽出
2. ✅ 確認済み — ユーザーが早朝（Start Court）で承認（文言の編集可）
3. 📈 強化 — エビデンスが蓄積（evidence_count が増加、confidence が上昇）
4. ⚠️ 異議あり — 矛盾する経験を検出（challenges が増加、confidence が低下）
5. 🔄 改訂 — ユーザーが新しいエビデンスに基づいて結論を更新
6. 🗄️ 退役 — wiki/_archive/ に移動（低確信度 + 90日以上活動なし）
```

---

## Wiki INDEX

`wiki/INDEX.md` は全 Wiki エントリのコンパイル済みサマリーです。早朝官が毎回の Start Court で実際の wiki/ ファイルからコンパイルします。

### フォーマット

```markdown
# Wiki Index
compiled: YYYY-MM-DD

## Finance
- NPO lending has no 貸金業法 exemption (0.95) → wiki/finance/lending-law-npo.md
- NPO tax deduction conditions (0.82) → wiki/finance/npo-tax-deduction.md

## Startup
- MVP validates demand, not product (0.88) → wiki/startup/mvp-validation.md
- Business plan: internal vs external versions differ fundamentally (0.72) → wiki/gcsb/biz-plan-versions.md

## Health
- 16:8 intermittent fasting works for me (0.80) → wiki/health/intermittent-fasting.md
```

各行80文字以下。INDEX 全体は通常20〜100行 — ロードコストは非常に低いです。

**INDEX.md はコンパイル済みの成果物です** — 手動編集しないでください。wiki/ ファイルから再生成されます。

---

## 4つのソース

| ソース | 方法 | タイミング |
|--------|-----|------|
| **DREAM** | N3 ステージが3日間の活動から再利用可能な結論を発見 | 毎回の退朝（Adjourn Court）後 |
| **セッション** | 三省ワークフロー中に六部が再利用可能な知見を生成 | `wiki_candidate: true` とマークされたジャーナルエントリ |
| **ユーザー** | いつでも直接入力 | "この事実を記憶して: X" |

---

## Wiki 候補フォーマット

DREAM が記録に値する知識を発見した場合：

```
📚 Wiki 候補:
- Domain: [ドメイン名]
- Topic: [短い識別子]
- Conclusion: [一文 — 再利用可能な要点]
- Evidence:
  - [日付] [決定/行動] — [説明]
  - [日付] [決定/行動] — [説明]
- Applicable when: [どのようなシナリオで想起すべきか]
```

ユーザーが次の Start Court で確認、編集、または却下します。

---

## 各ロールの Wiki 活用方法

すべてのロールは wiki/INDEX.md が存在するか確認してから参照します。存在しないか空の場合、ロールは Wiki 入力なしで通常どおり動作します。

| ロール | 参照する内容 | 活用方法 |
|------|---------------|-----------------|
| **丞相** | wiki/INDEX.md（全インデックス） | ドメインマッチをスキャン — 高確信度エントリが存在する場合、ユーザーに「既知の知識 X があります」と通知し、冗長な調査のスキップを提案 |
| **尚書省** | 関連する Wiki エントリ（丞相から渡される） | ディスパッチコンテキストに「既知の前提 — ここから開始」として含める |
| **六部** | ディスパッチコンテキスト内の Wiki エントリ | ゼロからではなく、確立された結論から分析を開始 |
| **門下省** | wiki/INDEX.md | 整合性チェック — 新しい結論が既存の高確信度 Wiki エントリと矛盾する場合にフラグ |
| **御史台** | wiki/ ディレクトリ（パトロール中） | Wiki 健全性監査 — 古いエントリ、矛盾、知識のギャップ |
| **DREAM** | wiki/INDEX.md + wiki/ エントリ | N3: 新しい候補を提案 + 既存エントリの evidence/challenges を更新。REM: Wiki を素材として使ったクロスドメイン接続 |
| **早朝官** | wiki/ ディレクトリ | Start Court で INDEX.md をコンパイルし、Wiki 候補をユーザー確認のために提示 |

---

## Second-Brain 内の Wiki

```
second-brain/
├── SOUL.md              ← 自分は誰か（性格）
├── user-patterns.md     ← 何をするか（行動）
├── wiki/                ← 何を知っているか（知識）
│   ├── INDEX.md         ← コンパイル済みサマリー（自動生成）
│   ├── finance/
│   │   ├── lending-law-npo.md
│   │   └── npo-tax-deduction.md
│   ├── startup/
│   │   └── mvp-validation.md
│   ├── health/
│   │   └── intermittent-fasting.md
│   └── _archive/        ← 退役済みエントリ
├── inbox/
├── _meta/
├── projects/
├── areas/
└── archive/
```

---

## 初回初期化

早朝官が wiki/ が空または INDEX.md がないことを検出した場合：

1. ブリーフィングで報告：「📚 Wiki がまだ初期化されていません。セットアップしますか？」
2. ユーザーが同意した場合：
   a. `decisions/` と `_meta/journal/` から抽出可能な結論をスキャン（DREAM N3 Q2 と同じロジック）
   b. 上位 5 件の候補を wiki エントリとしてユーザーに確認提示
   c. 確認された各エントリ：適切なフロントマター付きで `wiki/{domain}/{topic}.md` を作成
   d. `wiki/INDEX.md` を編纂
3. ユーザーが拒否 → スキップし、次回の上朝で再度通知

このフローは一度だけトリガーされる。INDEX.md が存在した後は、通常の wiki フローが引き継ぐ。

---

## レガシー移行

wiki/ に仕様フォーマットに一致しないファイルがある場合（フロントマターなし、ドメインサブディレクトリなし、タイトル≠結論）：

1. ブリーフィングで報告：「📚 現在の仕様に一致しない N 件のレガシー wiki ファイルを発見。移行しますか？」
2. ユーザーが同意した場合：
   a. 各レガシーファイルを読み取り
   b. ファイルごとに 1-3 の再利用可能な結論を抽出 → 新しい wiki エントリとして提案
   c. ユーザーが各エントリを確認 → `wiki/{domain}/{topic}.md` に書き込み
   d. 元のファイルを `wiki/_archive/` に移動（保存、削除しない）
   e. INDEX.md を再編纂
3. ユーザーが拒否 → そのまま、通常フローをブロックしない

wiki/ ルートにあるレガシーファイル（フロントマターなし）は INDEX.md 編纂時に無視される。

---

## 制約

- **ユーザーがすべての書き込みを確認** — Wiki エントリは自動作成されません
- **INDEX.md はコンパイル済み、手動作成不可** — 毎回の Start Court で wiki/ ファイルから再生成
- **1ファイル1結論** — 「トピックまとめ」ファイルは作成しない
- **タイトル＝結論** — ファイルを開けば答えがわかる
- **Wiki 内の相互参照なし** — 各エントリは自己完結
- **簡潔さ** — Wiki エントリは10〜30行、論文ではない
