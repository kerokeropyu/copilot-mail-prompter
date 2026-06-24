"""Copilot Mail Prompter のテスト.

GUI を起動しないロジック部分（_build_prompt）を対象にする。
"""

from __future__ import annotations

from copilot_mail_prompter.app import _build_prompt


def test_proofread_mode_uses_draft() -> None:
    result = _build_prompt(draft="下書きテスト", received="", sender="", recipient="", internal=True)
    assert "下書きテスト" in result
    assert "添削" in result


def test_reply_mode_uses_received() -> None:
    result = _build_prompt(draft="", received="受信メールテスト", sender="", recipient="", internal=True)
    assert "受信メールテスト" in result
    assert "返信" in result


def test_internal_style_applied() -> None:
    result = _build_prompt(draft="テスト", received="", sender="", recipient="", internal=True)
    assert "社内向け" in result


def test_external_style_applied() -> None:
    result = _build_prompt(draft="テスト", received="", sender="", recipient="", internal=False)
    assert "社外取引先向け" in result


def test_rule_block_always_included() -> None:
    result = _build_prompt(draft="テスト", received="", sender="", recipient="", internal=True)
    assert "厳守ルール" in result


def test_sender_recipient_in_reply_mode() -> None:
    result = _build_prompt(
        draft="", received="受信テスト", sender="田中部長", recipient="山田課長", internal=True
    )
    assert "田中部長" in result
    assert "山田課長" in result


def test_sender_recipient_not_in_proofread_mode() -> None:
    result = _build_prompt(
        draft="下書き", received="", sender="田中部長", recipient="山田課長", internal=True
    )
    # 添削モードでは誰から/誰への情報は不要（プロンプトに含めない）
    assert "田中部長" not in result
    assert "山田課長" not in result


def test_app_name_is_set() -> None:
    from copilot_mail_prompter.app import APP_NAME
    assert APP_NAME == "Copilot Mail Prompter"
