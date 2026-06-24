# pyproject.toml の設定ブロック

`uv init --package` と `uv add` が生成した `pyproject.toml` に、ツール設定だけを**追記**する。

## 重要: 追記してよいのはツール設定だけ

- `[project]` / `[project.scripts]` / `[build-system]` は `uv init --package` が生成済み。作り直さない。
- `[dependency-groups]` は `uv add --dev` が自動生成・管理する。**手で追記すると TOML の duplicate key エラーになる**ので追記しないこと。
- 手で追記するのは `[tool.ruff]` / `[tool.mypy]` / `[tool.pytest.ini_options]` の3つだけ。

## 追記するブロック

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
# E,F: pyflakes/pycodestyle, I: isort, UP: pyupgrade, B: bugbear, SIM: simplify
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_unused_configs = true
# customtkinter は型スタブが未整備なので未解決インポートを許容する
[[tool.mypy.overrides]]
module = ["customtkinter.*"]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## 完成後の pyproject.toml 全体イメージ

`customtkinter>=5.2.2` の行は `uv add customtkinter` が、`[dependency-groups]` は `uv add --dev ...` が入れたもの。

```toml
[project]
name = "myapp"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "customtkinter>=5.2.2",
]

[project.scripts]            # uv init --package が生成。uv run myapp の起点
myapp = "myapp:main"

[build-system]               # uv init --package が生成。これがあるので uv が venv に install する
requires = ["uv_build>=0.11.7,<0.12.0"]
build-backend = "uv_build"

[dependency-groups]          # uv add --dev が生成・管理（手で書かない）
dev = [
    "ruff>=0.8",
    "mypy>=1.13",
    "pytest>=8.3",
    "pyinstaller>=6.11",
]

# ↓ ここから下が手で追記する部分
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_unused_configs = true

[[tool.mypy.overrides]]
module = ["customtkinter.*"]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## 各設定のねらい

- **build-system (uv_build)**: src レイアウトでは `[build-system]` があることで uv がパッケージを venv に install する。これにより `from myapp import app` がテストや実行で解決できる。flat レイアウトで使っていた `pythonpath = ["."]` ハックは src レイアウトでは**不要**。
- **project.scripts**: `uv run myapp` でアプリを起動できる。exe もこの main を起点にする。
- **ruff line-length=100**: PHP/Laravel から来る場合 79 は窮屈なので 100 に設定。好みで変更可。
- **mypy strict=true**: 型注釈を厳格にチェック。`from __future__ import annotations` をテンプレートで入れているので Python 3.12 でも問題なく動く。
- **customtkinter の overrides**: customtkinter は型スタブを同梱しないため、これがないと strict モードで大量にエラーが出る。
- **py.typed**: `src/myapp/py.typed`（空ファイル）を置くと、このパッケージが型付きとして扱われ mypy が安定する。

## mypy の実行
src レイアウトでは対象を明示する:

```bash
uv run mypy src tests
```
