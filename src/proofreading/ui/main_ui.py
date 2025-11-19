# ruff: noqa: F405
from typing import Callable, Dict
from functools import partial

from .base_ui import BaseUI
from .utils import COLOR_GRAY
from ..utils import KEY, KEY_IGNORE, UIResult, FuncContainer, FuncType, PasteOption, Action
from ..prooftools import *
from ..controller import close_app, filesave, clear_history

import curses

class MainUI(BaseUI):
    lines = [
        "Choose option: ",
        "[tab] manual input",
        "[;] add rule",
        "[1] hyphenate",
        "[2] delete symbol",
        "[3] lowercase",
        "[4] title case",
        "[9] look up word",
        "[0] google word",
        " ",
        "[e] paste highlighted",
        "[r] flip words",
        "[t] paste \"Then,\"",
        " ",
        "[a] paste \"and\"",
        "[s] pluralizer (simple)",
        "[d] to past tense (simple)",
        "[f] fix common errors",
        " ",
        "[c] paste colon",
        " ",
        ("[`] options", COLOR_GRAY()),
        ("[esc] exit", COLOR_GRAY()),
    ]

    actions: Dict[str, Action] = {
        '1': hyphenate,
        '2': FuncContainer(delete_symbol, special = True, special_default='2'),
        '3': lower,
        '4': upper,
        '9': FuncContainer(look_up_word, FuncType.Default, PasteOption.Nothing),
        '0': FuncContainer(google_word, FuncType.Default, PasteOption.Nothing),
        'e': get_word,
        'r': flip_words,
        't': FuncContainer(partial(paster, "Then, "), FuncType.NoCopy),
        'a': FuncContainer(partial(paster, "and"), FuncType.NoCopy),
        's': pluralize,
        'd': to_past_tense,
        'f': common_error_parser,
        'g': to_present_participle,
        'c': FuncContainer(partial(paster, ':'), FuncType.NoCopy, PasteOption.Raw),
        ',': FuncContainer(filesave, FuncType.Super),
        '-': FuncContainer(clear_history, FuncType.Super),
        KEY.esc: FuncContainer(close_app, FuncType.Super),
    }

    to_other_ui = {
        '`': "options",
        KEY.tab: "manual_input",
        ';': "add_session_rule",
    }

    def draw(self, state) -> curses.window:
        win = super().draw(state)
        return win
   
    def run(self, state) -> UIResult:
        win = self.draw(state)
        
        user_input: str = ''

        user_input = curses.keyname(win.getch()).decode()
        curses.flushinp()
        
        output: UIResult = UIResult(error = state.error)
        
        # ignore certain keypresses (e.g. curses.KEY_RESIZE)
        if user_input in KEY_IGNORE:
            return output
        
        # check if user activate another ui
        try:
            output.ui = self.to_other_ui[user_input]
        except KeyError:
            pass
        else:
            output.error = None
            return output

        # check if user has selected a valid action
        try:
            action = self.actions[user_input]
        except KeyError:
            output.error = Exception(f"invalid input {user_input}")
        else:
            output.error = None
            output.action = FuncContainer(action) if isinstance(action, Callable) else action

        return output
