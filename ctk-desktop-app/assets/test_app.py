"""{{APP_NAME}} のテスト.

CI でも回せるよう、GUI を起動しないロジック部分を対象にする。
ウィンドウ表示を伴うテストはヘッドレス環境で落ちるため、ここでは扱わない。
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from {{PKG}} import app


def test_setup_logging_creates_log_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """setup_logging がログディレクトリとハンドラを用意することを確認する。"""
    log_dir = tmp_path / "logs"
    monkeypatch.setattr(app, "LOG_DIR", log_dir)
    monkeypatch.setattr(app, "LOG_FILE", log_dir / "app.log")
    # 既存ハンドラをクリアして冪等にする
    app.logger.handlers.clear()

    app.setup_logging()

    assert log_dir.exists()
    assert app.logger.level == logging.DEBUG
    assert len(app.logger.handlers) == 2


def test_app_name_is_set() -> None:
    assert app.APP_NAME
