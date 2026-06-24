# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Copilot Mail Prompter (src レイアウト).

customtkinter は .json テーマや .otf フォントなどのデータファイルを含むため、
collect_all で submodules / data / binaries をまとめて取り込む。
これがないと exe 起動時に「theme json が見つからない」系のエラーになる。

ビルド:
    uv run pyinstaller build.spec --noconfirm

重要:
    - customtkinter のデータファイル都合で --onefile は不可。onedir でビルドする。
    - PyInstaller はクロスコンパイル不可。Windows exe は Windows 上でビルドする
      (WSL/Linux 上ではなく Windows ホスト側で実行すること)。
"""

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all("customtkinter")

a = Analysis(
    ["src/copilot_mail_prompter/app.py"],
    pathex=["src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="copilot_mail_prompter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI アプリなのでコンソール非表示。デバッグ時は True にする
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="assets/icon.ico",  # アイコンがあれば指定
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="copilot_mail_prompter",
)
