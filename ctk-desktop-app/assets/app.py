"""{{APP_NAME}} - CustomTkinter デスクトップアプリ.

アプリ本体を1モジュールに集約。ログローテーションを内蔵し、PyInstaller での exe 化に対応する。
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import customtkinter as ctk

# ── 定数 ──────────────────────────────────────────────────────────────
APP_NAME = "{{APP_NAME}}"
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"
LOG_MAX_BYTES = 1_000_000  # 1ファイルあたり最大1MB
LOG_BACKUP_COUNT = 5  # 過去ログを5世代まで保持

logger = logging.getLogger(APP_NAME)


def setup_logging() -> None:
    """ログ設定を初期化する。

    RotatingFileHandler でファイルサイズ上限と世代数を管理し、肥大化を防ぐ。
    開発時に見えるようコンソール出力も併設する。
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False


class App(ctk.CTk):  # type: ignore[misc]  # customtkinter は型スタブ未整備のため
    """アプリのメインウィンドウ."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("480x320")

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self._build_ui()
        logger.info("アプリを起動しました")

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            frame,
            text="Hello, CustomTkinter",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.label.grid(row=0, column=0, padx=20, pady=(40, 20))

        self.button = ctk.CTkButton(frame, text="クリック", command=self._on_click)
        self.button.grid(row=1, column=0, padx=20, pady=10)

    def _on_click(self) -> None:
        logger.debug("ボタンがクリックされました")
        self.label.configure(text="クリックされました!")


def main() -> None:
    setup_logging()
    try:
        app = App()
        app.mainloop()
    except Exception:
        logger.exception("予期しないエラーで終了しました")
        raise
    finally:
        logger.info("アプリを終了しました")
