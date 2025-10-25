from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Callable, TYPE_CHECKING, Tuple
from functools import partial

from app.utils.constants import KEY

if TYPE_CHECKING:
    from app import State

import curses

from ..actions import MAIN_ACTIONS, OPTIONS_ACTIONS, FuncContainer
from ..utils import KEY_IGNORE

COLOR_GRAY = partial(curses.color_pair, 1)
COLOR_RED = partial(curses.color_pair, 2)

@dataclass
class UIResult():
    ui: Optional[str] = None
    action: Optional[str | Callable | FuncContainer] = None
    error: Optional[Exception] = None

# base UI class all UIs will inherit from 
class BaseUI:
    lines: List[str | Tuple[str, Callable]]
    
    def run(self, state: State) -> UIResult:
        raise NotImplementedError

    def draw(self, state: State) -> curses.window:
        win = state.screen
        win.clear()
        
        line_number: int = 0
        for line_number, line in enumerate(self.lines):
            if isinstance(line, str):
                text = line
                attr = 0
            elif isinstance(line, tuple):
                text, attr = line
                if isinstance(attr, Callable):
                    attr = attr() # this seems fucked up
            else:
                text, attr = ("", 0)
            win.addstr(line_number, 0, text, attr)

        if state.error:
            win.addstr(line_number+2, 0, state.error.args[0], COLOR_RED())
        
        win.move(0, 0)
        win.refresh()
        return win

class MainUI(BaseUI):
    lines = [
        "Choose option: ",
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
        ("[`] options", COLOR_GRAY),
        ("[esc] exit", COLOR_GRAY),
    ]
   
    def run(self, state) -> UIResult:
        win = self.draw(state)
        
        user_input: str = ''
        user_input = curses.keyname(win.getch()).decode()
        
        output: UIResult = UIResult()
        
        # ignore certain keypresses (e.g. curses.KEY_RESIZE)
        if user_input in KEY_IGNORE:
            return output

        if user_input == '`':
            output.ui = "options"
            return output

        try:
            output.action = MAIN_ACTIONS[user_input]
        except KeyError:
            output.error = Exception(f"invalid input {user_input}")

        return output

class OptionsUI(BaseUI):
    lines = []

    def draw(self, state) -> curses.window:
        vars = state.vars
        win = state.screen
        win.clear()
        
        win.addstr(0, 0,
            "[1] toggle EN/US conversion ["
            f"{"EN->US" if vars.convert_english else "US->EN"}]"
        )
        win.addstr(1,0,"[bksp] return to main", COLOR_GRAY())

        if state.error:
            win.addstr(3, 0, state.error.args[0], COLOR_RED())
        
        return win
    
    def run(self, state) -> UIResult:
        win = self.draw(state)

        user_input: str = ''
        user_input = curses.keyname(win.getch()).decode()
        
        output: UIResult = UIResult()
        
        # ignore certain keypresses (e.g. curses.KEY_RESIZE)
        if user_input in KEY_IGNORE:
            return output
        
        if user_input == KEY.bksp:
            output.ui = "main"
            return output

        try:
            output.action = OPTIONS_ACTIONS[user_input]
        except KeyError:
            output.error = Exception(f"invalid input {user_input}")
        
        return output

# class DummyUI(BaseUI):
#     def draw(self, state) -> curses.window:
#         return state.screen

#     def run(self, state) -> UIResult:
#         win = self.draw(state)
#         user_input = curses.keyname(win.getch()).decode()
#         output: UIResult = UIResult()
#         return output
