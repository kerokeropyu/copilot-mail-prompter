"""Copilot Mail Prompter - CustomTkinter デスクトップアプリ."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import customtkinter as ctk

APP_NAME = "Copilot Mail Prompter"

# ── デフォルトプロンプトテンプレート ────────────────────────────────────────────
_D_RULE_BLOCK = """\
# 厳守ルール
1. 結論・用件を先に書く。長い前置きを避ける。
2. 入力に無い事実・数値・日付を創作しない。不足箇所は本文中に【要確認】と明記する。
3. 返信作成の場合、出力はメール本文のみ。説明・前置きは不要。添削の場合はメールタイトルも生成。"""

_D_STYLE_INTERNAL = """\
# 文体: 社内向け。「お疲れ様です」始まり。過度な敬語・クッション言葉は不要。簡潔・端的に。"""

_D_STYLE_EXTERNAL = """\
# 文体: 社外取引先向け。標準的なビジネス敬語。丁寧だが冗長にしない。"""

_D_PROOFREAD_BODY = """\
以下のメール下書きを、文体ブロックと厳守ルールに従って添削してください。
元の意図は変えないこと。意味が不明瞭な箇所は勝手に直さず【意図確認】と注記する。

# 下書き
\"\"\"
{draft}
\"\"\""""

_D_REPLY_BODY = """\
あなたは下記の受信メールに返信する担当者です。文体ブロックと厳守ルールに従い返信本文を作成してください。
受信メールの問いにすべて漏れなく答えること。

# 受信メール
\"\"\"
{received}
\"\"\"

# 自分が伝えたい要点（口語・順不同でOK。空なら受信メールへの妥当な返答を作る）
\"\"\"
{draft}
\"\"\""""

# ── UI 定数 ──────────────────────────────────────────────────────────────────
_LABEL_OUTPUT = "生成されたプロンプト — クリックでコピー"
_LABEL_COPIED = "コピー済み ✓"
_COLOR_BADGE_DEFAULT: tuple[str, str] = ("gray50", "gray55")
_COLOR_BADGE_COPIED: tuple[str, str] = ("#2a8a2a", "#5ecf5e")


# ── 設定ファイル読み込み ─────────────────────────────────────────────────────
def _find_config() -> Path:
    cwd_cfg = Path.cwd() / "config.toml"
    if cwd_cfg.exists():
        return cwd_cfg
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "config.toml"
    return Path(__file__).parent.parent.parent / "config.toml"


def _load_templates() -> dict[str, str]:
    path = _find_config()
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return data.get("prompts", {})  # type: ignore[return-value]


_t = _load_templates()
_RULE_BLOCK = _t.get("rule_block", _D_RULE_BLOCK)
_STYLE_INTERNAL = _t.get("style_internal", _D_STYLE_INTERNAL)
_STYLE_EXTERNAL = _t.get("style_external", _D_STYLE_EXTERNAL)
_PROOFREAD_BODY = _t.get("proofread_body", _D_PROOFREAD_BODY)
_REPLY_BODY = _t.get("reply_body", _D_REPLY_BODY)


# ── プロンプト組み立て ───────────────────────────────────────────────────────
def _build_prompt(
    *,
    draft: str,
    received: str,
    sender: str,
    recipient: str,
    internal: bool,
) -> str:
    style = _STYLE_INTERNAL if internal else _STYLE_EXTERNAL

    if draft:
        body = _PROOFREAD_BODY.format(draft=draft)
    else:
        body = _REPLY_BODY.format(received=received, draft=draft)
        meta = []
        if sender:
            meta.append(f"送信者: {sender}")
        if recipient:
            meta.append(f"宛先: {recipient}")
        if meta:
            body = "\n".join(meta) + "\n\n" + body

    return f"{body}\n\n{style}\n\n{_RULE_BLOCK}"


# ── UI ──────────────────────────────────────────────────────────────────────
class App(ctk.CTk):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self._debounce_id: str | None = None
        self._copy_reset_id: str | None = None
        self._build_ui()
        self._center_window(720, 860)

    def _center_window(self, w: int, h: int) -> None:
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    # ── UI 構築 ──────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(8, weight=1)

        LP = {"padx": 16}

        # 1. 宛先種別ラジオボタン
        radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        radio_frame.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))
        self._audience = ctk.StringVar(value="internal")
        ctk.CTkLabel(radio_frame, text="宛先種別:").pack(side="left", padx=(0, 12))
        ctk.CTkRadioButton(
            radio_frame, text="社内", variable=self._audience, value="internal",
            command=self._schedule_generate,
        ).pack(side="left", padx=(0, 12))
        ctk.CTkRadioButton(
            radio_frame, text="社外", variable=self._audience, value="external",
            command=self._schedule_generate,
        ).pack(side="left")

        # 2. テキストエリア A
        self._build_textbox_section(
            label_row=1, box_row=2, label="自分の下書き・要点",
            attr="_draft_box", lp=LP,
        )

        # 3. テキストエリア B
        self._build_textbox_section(
            label_row=3, box_row=4, label="相手から来たメール",
            attr="_received_box", lp=LP,
        )

        # 4. 誰から / 誰へ
        meta_frame = ctk.CTkFrame(self, fg_color="transparent")
        meta_frame.grid(row=5, column=0, sticky="ew", padx=16, pady=(2, 6))
        meta_frame.grid_columnconfigure((0, 1), weight=1)

        self._sender_var = ctk.StringVar()
        self._recipient_var = ctk.StringVar()
        self._sender_var.trace_add("write", lambda *_: self._schedule_generate())
        self._recipient_var.trace_add("write", lambda *_: self._schedule_generate())

        from_inner = ctk.CTkFrame(meta_frame, fg_color="transparent")
        from_inner.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        from_inner.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(from_inner, text="誰から", width=50).grid(row=0, column=0, padx=(0, 6))
        self._sender_entry = ctk.CTkEntry(
            from_inner, textvariable=self._sender_var, placeholder_text="例: 田中部長"
        )
        self._sender_entry.grid(row=0, column=1, sticky="ew")

        to_inner = ctk.CTkFrame(meta_frame, fg_color="transparent")
        to_inner.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        to_inner.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(to_inner, text="誰へ", width=50).grid(row=0, column=0, padx=(0, 6))
        self._recipient_entry = ctk.CTkEntry(
            to_inner, textvariable=self._recipient_var, placeholder_text="例: 山田課長"
        )
        self._recipient_entry.grid(row=0, column=1, sticky="ew")

        # 5. 出力ヘッダー（ラベル + コピー状態バッジ）
        output_hdr = ctk.CTkFrame(self, fg_color="transparent")
        output_hdr.grid(row=7, column=0, sticky="ew", padx=16, pady=(8, 2))
        output_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(output_hdr, text=_LABEL_OUTPUT, anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        self._copy_badge = ctk.CTkLabel(
            output_hdr, text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=_COLOR_BADGE_COPIED,
            anchor="e",
        )
        self._copy_badge.grid(row=0, column=1, sticky="e")

        # 6. 出力エリア（クリックでコピー）
        self._output_box = ctk.CTkTextbox(self, state="disabled")
        self._output_box.grid(row=8, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self._output_box._textbox.configure(cursor="hand2")
        self._output_box._textbox.bind("<Button-1>", self._on_output_click)

    def _build_textbox_section(
        self,
        *,
        label_row: int,
        box_row: int,
        label: str,
        attr: str,
        lp: dict[str, int],
    ) -> None:
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=label_row, column=0, sticky="ew", padx=16, pady=(4, 2))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text=label, anchor="w").grid(row=0, column=0, sticky="w")

        box = ctk.CTkTextbox(self, height=150)
        box.grid(row=box_row, column=0, sticky="ew", pady=(0, 6), **lp)
        setattr(self, attr, box)
        self._bind_text_change(box)

        ctk.CTkButton(
            hdr, text="クリア", width=60, height=26,
            fg_color=("gray82", "gray28"),
            text_color=("gray20", "gray90"),
            hover_color=("gray70", "gray38"),
            border_width=0,
            corner_radius=6,
            command=lambda b=box: self._clear_box(b),
        ).grid(row=0, column=1, sticky="e")

    # ── ヘルパー ─────────────────────────────────────────────────────────
    def _bind_text_change(self, box: ctk.CTkTextbox) -> None:
        def on_modified(_event: object) -> None:
            box._textbox.edit_modified(False)
            self._schedule_generate()
        box._textbox.bind("<<Modified>>", on_modified)

    def _clear_box(self, box: ctk.CTkTextbox) -> None:
        box.delete("1.0", "end")

    def _read_box(self, box: ctk.CTkTextbox) -> str:
        return box.get("1.0", "end-1c").strip()

    def _read_output(self) -> str:
        self._output_box.configure(state="normal")
        text = self._output_box.get("1.0", "end-1c")
        self._output_box.configure(state="disabled")
        return text

    def _set_output(self, text: str) -> None:
        self._output_box.configure(state="normal")
        self._output_box.delete("1.0", "end")
        self._output_box.insert("1.0", text)
        self._output_box.configure(state="disabled")

    # ── イベントハンドラ ─────────────────────────────────────────────────
    def _schedule_generate(self) -> None:
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(300, self._on_generate)

    def _on_generate(self) -> None:
        draft = self._read_box(self._draft_box)
        received = self._read_box(self._received_box)

        if not draft and not received:
            self._set_output("")
            return

        if draft and received:
            self._set_output(
                "どちらか一方の入力にしてください（下書きと受信メールを同時に入力しないでください）。"
            )
            return

        self._set_output(
            _build_prompt(
                draft=draft,
                received=received,
                sender=self._sender_var.get().strip(),
                recipient=self._recipient_var.get().strip(),
                internal=self._audience.get() == "internal",
            )
        )

    def _on_output_click(self, _event: object = None) -> None:
        text = self._read_output()
        if not text.strip():
            return
        self.clipboard_clear()
        self.clipboard_append(text)

        self._copy_badge.configure(text=_LABEL_COPIED)
        if self._copy_reset_id:
            self.after_cancel(self._copy_reset_id)
        self._copy_reset_id = self.after(
            2000, lambda: self._copy_badge.configure(text="")
        )


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
