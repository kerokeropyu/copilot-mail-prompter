# Copilot Mail Prompter

社内 M365 Copilot にメール添削・返信作成をさせる際の「貼り付け用プロンプト」を組み立てるデスクトップツール。プロンプトを生成してクリップボードにコピーするだけで、API は使わない。

## 起動方法

### 前提

- Python 3.12 以上
- [uv](https://docs.astral.sh/uv/) がインストール済みであること

### インストール〜初回起動

```bash
git clone <このリポジトリの URL>
cd copilot-mail-prompter

# 依存パッケージのインストール（仮想環境も自動作成される）
uv sync

# アプリ起動
uv run python -m copilot_mail_prompter.app
```

### 2回目以降

```bash
uv run python -m copilot_mail_prompter.app
```

## 使い方

1. **宛先種別** を「社内」または「社外」から選ぶ（デフォルト: 社内）
2. **自分の下書き・要点** か **相手から来たメール** のどちらか一方を入力する
   - 入力するとプロンプトがリアルタイムで自動生成される
   - 下書きのみ → 添削モード
   - 受信メールのみ → 返信作成モード
3. 返信作成の場合、必要に応じて「誰から」「誰へ」を入力する（任意）
4. 出力欄をクリックするとプロンプトをクリップボードにコピーできる
5. Copilot チャットに貼り付けて使う

各テキストエリア右上の **クリア** ボタンで入力内容をリセットできる。

> **注意**: 下書きと受信メールを両方入力するとエラーになる。どちらか一方だけ入力すること。

## プロンプトのカスタマイズ

プロジェクトルートの `config.toml` を編集することで、Copilot に渡す定型文を変更できる。

```toml
[prompts]
rule_block      = "..."   # 厳守ルール
style_internal  = "..."   # 社内向け文体指示
style_external  = "..."   # 社外向け文体指示
proofread_body  = "..."   # 添削モードのプロンプト本体（{draft} を含めること）
reply_body      = "..."   # 返信作成モードのプロンプト本体（{received}・{draft} を含めること）
```

- 変更後はアプリを再起動すると反映される
- `config.toml` が存在しない場合はビルトインのデフォルトを使用する

## 開発

```bash
# テスト実行
uv run python -m pytest

# Lint
uv run ruff check src tests

# 型チェック
uv run mypy src
```

## スコープ外（実装していないもの）

- Claude / OpenAI 等の API 連携・実際のメール生成
- Outlook / メールクライアント連携
- 入力履歴の永続化
- exe パッケージング（必要になったら `uv run pyinstaller build.spec --noconfirm`）
