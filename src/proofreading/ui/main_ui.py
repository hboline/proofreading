from .base_ui import BaseUI
from .utils import COLOR_GRAY, UIResult
from ..utils import KEY, KEY_IGNORE

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

        try:
            return UIResult(self.to_other_ui[user_input])
        except KeyError:
            pass

        output.user_input = user_input

        return output
