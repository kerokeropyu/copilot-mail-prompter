# PyInstaller で exe 化する

CustomTkinter アプリの exe 化には固有の落とし穴がある。`build.spec`（assets/build.spec）を使うことでこれらを回避済みだが、背景を理解しておくとトラブル時に対処しやすい。

## ビルド手順

```bash
uv run pyinstaller build.spec --noconfirm
```

成果物は `dist/<PKG>/` 以下に生成される。`dist/<PKG>/<PKG>.exe` を実行して起動を確認する。配布時はこの `dist/<PKG>/` フォルダごと渡す。

`build.spec` はエントリスクリプトを `src/<PKG>/app.py`、`pathex=["src"]` に設定済み（src レイアウト対応）。

## 落とし穴と対策

### 1. `--onefile` は使えない → `--onedir`
customtkinter は `.json`（テーマ）や `.otf`（フォント）といったデータファイルを含む。PyInstaller の `--onefile` はこれらの同梱が不安定なため、`--onedir`（フォルダ形式）でビルドする。`build.spec` は `COLLECT` を使う onedir 構成になっている。

### 2. テーマ JSON が見つからない → `collect_all`
PyInstaller は customtkinter のデータファイルを自動では取り込まない。そのまま exe 化すると起動時に theme json 関連のエラーになる。`build.spec` 冒頭の以下で submodules / data / binaries をまとめて取り込んでいる:

```python
from PyInstaller.utils.hooks import collect_all
datas, binaries, hiddenimports = collect_all("customtkinter")
```

これは site-packages のパスを手書きする方法より堅牢で、環境が変わっても壊れない。

### 3. クロスコンパイル不可 → Windows exe は Windows で作る
PyInstaller はクロスコンパイラではない。**WSL/Linux 上でビルドすると Linux 用バイナリができてしまい、Windows では動かない。** Windows exe を作るときは Windows ホスト側（PowerShell など）で `uv run pyinstaller build.spec` を実行すること。Windows + WSL2 環境では特に注意。

### 4. コンソール窓を消す
`build.spec` の `EXE(... console=False ...)` で GUI 起動時の黒いコンソール窓を抑止している。例外調査などでログを直接見たいときは一時的に `console=True` にする。

### 5. アイコンを付ける
`.ico` を用意して `build.spec` の `EXE(...)` 内の `icon="assets/icon.ico"` のコメントを外す。

## バンドル後のリソース参照
exe 内に同梱した追加リソース（画像など）を読むときは、実行パスが変わるため次のヘルパーでパスを解決する:

```python
import sys
from pathlib import Path

def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / relative
```

ログ出力先（logs/）は exe の隣に作られるので、書き込み権限のある場所に exe を置くこと。
