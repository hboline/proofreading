from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Callable, TYPE_CHECKING, Tuple
from functools import partial
if TYPE_CHECKING:
    from app import State

import curses

from utils.constants import KEY

COLOR_GRAY = partial(curses.color_pair, 1)

@dataclass
class UIResult():
    next_ui: Optional[str] = None
    action: Optional[str] = None
    error: Optional[Exception] = None

PLACEHOLDER = UIResult(error = Exception("hi"))

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
            win.addstr(line_number+2, 0, state.error.args[0], curses.COLOR_RED)
        
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
        user_input = curses.keyname(win.getch()).decode()
        output: UIResult = UIResult()
        match user_input:
            case KEY.esc:
                output.action = "exit"
        return output

class OptionsUI(BaseUI):
    lines = []
    
    def run(self, state) -> UIResult:
        self.draw(state)
        return PLACEHOLDER
