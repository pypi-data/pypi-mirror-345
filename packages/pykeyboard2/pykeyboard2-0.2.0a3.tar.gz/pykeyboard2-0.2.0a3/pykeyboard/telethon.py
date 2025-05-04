try:
    from telethon import types

    BaseInlineMarkup = types.ReplyInlineMarkup
except ImportError:
    types = None
    BaseInlineMarkup = None

from ._helpers import require_module


@require_module(
    BaseInlineMarkup,
    "Telethon module is not installed. Please install it using 'pip install telethon'",
)
class InlineKeyboard:
    def __init__(self, row_width=3):
        self.row_width = row_width
        self.rows = []

    def add(self, *args):
        self._check_buttons(args)
        for i in range(0, len(args), self.row_width):
            row = args[i : i + self.row_width]
            self.rows.append(types.KeyboardButtonRow(buttons=list(row)))

    def row(self, *args):
        self._check_buttons(args)
        self.rows.append(types.KeyboardButtonRow(buttons=list(args)))

    def _check_buttons(self, buttons):
        for btn in buttons:
            if not isinstance(
                btn,
                (
                    types.InputKeyboardButtonUrlAuth,
                    types.InputKeyboardButtonUserProfile,
                    types.KeyboardButtonBuy,
                    types.KeyboardButtonCallback,
                    types.KeyboardButtonCopy,
                    types.KeyboardButtonGame,
                    types.KeyboardButtonSwitchInline,
                    types.KeyboardButtonUrl,
                    types.KeyboardButtonWebView,
                ),
            ):
                raise ValueError(
                    f"Invalid button type: expected an inline button, got {type(btn).__name__}"
                )
