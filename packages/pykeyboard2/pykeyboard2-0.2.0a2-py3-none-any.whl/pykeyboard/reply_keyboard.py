try:
    from pyrogram.types import ReplyKeyboardMarkup
except ImportError:
    ReplyKeyboardMarkup = None

from ._helpers import require_module


@require_module(
    ReplyKeyboardMarkup,
    "Pyrogram is required: ReplyKeyboard depends on Pyrogram. Please install it",
)
class ReplyKeyboard:
    def __init__(
        self,
        resize_keyboard=None,
        one_time_keyboard=None,
        selective=None,
        placeholder=None,
        row_width=3,
    ):
        self.keyboard = list()
        super().__init__(
            keyboard=self.keyboard,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            selective=selective,
            placeholder=placeholder,
        )
        self.row_width = row_width

    def add(self, *args):
        self.keyboard = [
            args[i : i + self.row_width] for i in range(0, len(args), self.row_width)
        ]

    def row(self, *args):
        self.keyboard.append([button for button in args])
