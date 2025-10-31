from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Callable, TYPE_CHECKING, Tuple
from functools import partial

import curses

from ..actions import MAIN_ACTIONS, OPTIONS_ACTIONS, FuncContainer
from ..utils import KEY_IGNORE
from app.utils.constants import KEY
if TYPE_CHECKING:
    from app import State

COLOR_GRAY = partial(curses.color_pair, 1)
COLOR_RED = partial(curses.color_pair, 2)
COLOR_GREEN = partial(curses.color_pair, 3)

@dataclass
class UIResult():
    ui: Optional[str] = None
    action: Optional[str | Callable | FuncContainer] = None
    error: Optional[Exception] = None

def _curses_add_lines(
    win: curses.window,
    lines: (
        List[str | Tuple[str, Callable[[], int]]] |
        str |
        Tuple[str, Callable[[], int]]
    ),
    line_start: int = 0,
    wrap_x = False,
) -> int:
    if not isinstance(lines, list):
        lines = [lines]
    
    line_number = 0
    max_y, max_x = win.getmaxyx()
    y_offset = 0
    for line_number, line in enumerate(lines):
        text: str = ''
        attr: int | Callable = 0
        
        line_number += line_start + y_offset
        
        if isinstance(line, str):
            text = line
            attr = 0
        elif isinstance(line, tuple):
            text, attr = line
            if isinstance(attr, Callable):
                attr = attr()
        try:
            assert isinstance(text, str)
            assert isinstance(attr, int)
            
            if wrap_x is False:
                text = text[:max_x]
            else:
                y_offset += len(text)//max_x
                text = text[:(max_y - line_number)*max_x]
                
            win.addstr(line_number, 0, text, attr)
        except curses.error:
            pass

    return line_number

# base UI class all UIs will inherit from 
class BaseUI:
    lines: List[str | Tuple[str, Callable]]
    
    def run(self, state: State) -> UIResult:
        raise NotImplementedError

    def draw(self, state: State) -> curses.window:
        win = state.screen
        win.clear()

        max_y, max_x  = win.getmaxyx()

        # TODO: the "..."s aren't quite right; check ui
        trunc: int = 2
        sub_lines: List = self.lines.copy()
        end_lines: List = [("...",COLOR_GRAY)] + [sub_lines[-1]]
        error_lines: List = []
        history_lines: List = state.action_history
        if state.error is not None:
            trunc += 1
            error_lines = ["",(state.error.args[0], COLOR_RED)]
            end_lines.extend([error_lines[-1]])

        if max_y > len(sub_lines):
            error_trim = 1 if (max_y - len(sub_lines)) == 1 else 0
            line_number = _curses_add_lines(win, sub_lines) + 1
            if len(error_lines) > 0:
                line_number = _curses_add_lines(win, error_lines[error_trim:], line_number, wrap_x=True)
            if len(state.action_history) > 0:
                line_number = _curses_add_lines(
                    win, 
                    ['History','─'*max_x],
                    line_start = line_number
                )
                
            _ = _curses_add_lines(
                win,
                [('▸'+line,func) for (line,func) in history_lines[:(max_y-line_number)]],
                line_number+1,
                wrap_x=True
            )
        else:
            max_line = max_y-trunc
            _ = _curses_add_lines(win, sub_lines[:max_line])
            _ = _curses_add_lines(win, end_lines, max_line, wrap_x=True)

        win.move(0, 0)
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
        
        output: UIResult = UIResult(error = state.error)
        
        # ignore certain keypresses (e.g. curses.KEY_RESIZE)
        if user_input in KEY_IGNORE:
            return output

        if user_input == '`':
            output.ui = "options"
            output.error = None
            return output

        try:
            output.action = MAIN_ACTIONS[user_input]
        except KeyError:
            output.error = Exception(f"invalid input {user_input}")
        else:
            if output.action != "filesave":
                state.action_history = [(f"{output.action}", COLOR_GREEN)] + state.action_history
            output.error = None

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
        
        output: UIResult = UIResult(error = state.error)
        
        # ignore certain keypresses (e.g. curses.KEY_RESIZE)
        if user_input in KEY_IGNORE:
            return output
        
        if user_input == KEY.bksp:
            output.ui = "main"
            output.error = None
            return output

        try:
            output.action = OPTIONS_ACTIONS[user_input]
        except KeyError:
            output.error = Exception(f"invalid input {user_input}")
        else:
            output.error = None
        
        return output
