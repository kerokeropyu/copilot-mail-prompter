---
name: ctk-desktop-app
description: Scaffold a Python desktop application using uv (src layout) + customtkinter + ruff + mypy + log rotation, with pytest and PyInstaller packaging. Use this skill whenever the user wants to build, start, or scaffold a Python desktop app, GUI app, or CustomTkinter app — even if they only say "デスクトップアプリ作って" or "Python の GUI ツール作りたい" without naming the stack. Also use it when adding ruff/mypy/log rotation/PyInstaller packaging to a Python desktop project. This is the standard, opinionated scaffold for desktop tooling.
---

# CustomTkinter デスクトップアプリのスキャフォルド

uv (src レイアウト) / customtkinter / ruff / mypy / ログローテーション を標準構成として、Python デスクトップアプリを立ち上げるためのスキル。pytest のひな形と PyInstaller での exe 化まで含む。アプリ本体は1モジュール（`app.py`）に集約するシンプル構成。

## いつ使うか

ユーザーが Python のデスクトップアプリ / GUI ツール / CustomTkinter アプリを作りたいと言ったとき。スタック名を明示していなくても、デスクトップ GUI の話であればこの構成を提案・適用する。既存の Python デスクトップ案件に ruff/mypy/ログローテーション/exe 化を足したいときにも使う。

## 構成の全体像（src レイアウト）

```
myapp/
├── pyproject.toml        # [project]/[project.scripts]/[build-system] + ruff/mypy/pytest 設定
├── uv.lock               # コミット推奨
├── .python-version
├── .gitignore
├── README.md
├── src/
│   └── myapp/
│       ├── __init__.py   # main を公開（エントリポイント）
│       ├── py.typed      # 型付きパッケージの目印（空ファイル）
│       └── app.py        # アプリ本体（CTk + ログローテーション）
├── tests/
│   ├── __init__.py
│   └── test_app.py       # pytest ひな形
└── logs/                 # 実行時に生成（gitignore 済み）
```

src レイアウトを採用する理由: 開発時の import がカレントディレクトリではなく**インストール済みパッケージ**に解決されるため、配布物と同じ状態でテストでき、import の事故を防げる。

採用理由を一言ずつ: **uv**=高速で再現性のある依存管理、**customtkinter**=モダンな見た目の tkinter、**ruff**=高速 lint+import 整列、**mypy**=型安全、**ログローテーション**=長期運用でのログ肥大化防止、**PyInstaller**=配布用 exe 化。

## プレースホルダ

テンプレート（このスキルの `assets/`）には2種類のプレースホルダがある。置換して使う:

- `{{PKG}}` … import 可能なパッケージ名。`src/<PKG>/`、import 文、`[project.scripts]`、exe 名に使う。小文字・アンダースコア区切り（ハイフン不可）。例: `myapp`
- `{{APP_NAME}}` … ウィンドウタイトルなどの表示名。日本語や空白も可。例: `My App`

## 手順

### 1. プロジェクト初期化（src レイアウト）
```bash
uv init --package myapp
cd myapp
```
`--package` を付けると src レイアウト（`src/myapp/__init__.py`）と `[build-system]`・`[project.scripts]` が生成される。**`--package` を忘れると flat レイアウトになる**ので必須。

### 2. 依存追加
```bash
uv add customtkinter
uv add --dev ruff mypy pytest pyinstaller
```

### 3. ファイル配置
- `assets/app.py` → `src/myapp/app.py`
- `assets/package_init.py` → `src/myapp/__init__.py`（uv 生成の `__init__.py` を上書き）
- `assets/test_app.py` → `tests/test_app.py`
- `assets/build.spec` → プロジェクト直下の `build.spec`
- `assets/gitignore` → `.gitignore`（uv が生成済みなら追記・統合）
- 空ファイルを作成: `src/myapp/py.typed`, `tests/__init__.py`
- すべてのファイルで `{{PKG}}` をパッケージ名に、`{{APP_NAME}}` を表示名に置換する

### 4. pyproject.toml に設定追記
`references/pyproject.md` を読み、`[tool.ruff]` / `[tool.mypy]` / `[tool.pytest.ini_options]` の3ブロックだけを追記する。**`[project]`/`[project.scripts]`/`[build-system]` は uv 生成のものを作り直さないこと。また `[dependency-groups]` は `uv add --dev` が既に書き込んでいるので手で追記しない**（追記すると TOML の duplicate key エラーになる）。customtkinter の mypy overrides は必須（型スタブ未整備のため）。src レイアウトではパッケージが venv に install されるので、flat 用の `pythonpath` ハックは不要。

### 5. 検証
```bash
uv run ruff check .
uv run ruff format .
uv run mypy src tests
uv run pytest
uv run myapp          # GUI 環境でのみ起動確認（uv run <PKG> がエントリポイント）
```
ruff / mypy / pytest が緑になることを確認する。ヘッドレス環境では GUI 起動は確認できないので、lint・型・テストの通過をもって完了とする。

なお pytest は `import {{PKG}}.app`→customtkinter→tkinter の連鎖で tkinter を要求する。Windows の標準 Python には同梱されるためローカルでは問題ないが、Linux の CI で回す場合は `python3-tk` の導入が必要。

### 6. exe 化（任意・配布時）
`references/packaging.md` を読んでからビルドする。**重要な注意点が複数あるので必ず参照すること**（`--onefile` 不可 / customtkinter データ同梱 / WSL では Windows exe を作れない）。
```bash
uv run pyinstaller build.spec --noconfirm
```

## 設計方針

- **app.py 1モジュールに集約**: ログ設定もアプリ本体も `app.py` に置く。複数画面に育ってきたら同じパッケージ内に `views/` などへ分割を提案してよいが、最初から構造化しない。
- **頼まれていない機能を足さない**: テンプレートの UI は最小限のサンプル。ユーザーの要件に沿って書き換え、余計な機能は追加しない。
- **ログは RotatingFileHandler**: ファイルサイズ上限と世代数で管理する（テンプレートは 1MB×5世代）。要件に応じて値を調整。日次ローテーションが要るなら TimedRotatingFileHandler に差し替える。

## 参照ファイル
- `references/pyproject.md` — ruff/mypy/pytest の設定ブロックと各設定のねらい（src レイアウト前提）
- `references/packaging.md` — PyInstaller + customtkinter の落とし穴と対策
