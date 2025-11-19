from __future__ import annotations
from typing import List, TYPE_CHECKING

from .utils import COLOR_GRAY, COLOR_RED, COLOR_GREEN, curses_add_lines
from ..utils import UIResult, Line

if TYPE_CHECKING:
    from ..controller import State
    
import curses

# base UI class all UIs will inherit from 
class BaseUI:
    lines: List[Line]
    
    def run(self, state: State) -> UIResult:
        raise NotImplementedError

    def draw(self, state: State) -> curses.window:
        win = state.screen
        win.clear()

        max_y, max_x  = win.getmaxyx()

        trunc: int = 2
        sub_lines: List = self.lines.copy()
        end_lines: List = [("...",COLOR_GRAY())] + [sub_lines[-1]]
        error_lines: List = []
        history_lines: List = [(action, COLOR_GREEN()) for action in state.action_history]
        if state.error is not None:
            trunc += 1
            error_lines = ["",(state.error.args[0], COLOR_RED())]
            end_lines.extend([error_lines[-1]])

        if max_y > len(sub_lines):
            error_trim = 1 if (max_y - len(sub_lines)) == 1 else 0
            line_number = curses_add_lines(win, sub_lines) + 1
            if len(error_lines) > 0:
                line_number = curses_add_lines(win, error_lines[error_trim:], line_number, wrap_x=True)
            if len(history_lines) > 0 and state.vars.show_output:
                line_number = curses_add_lines(
                    win, 
                    ['History','─'*max_x],
                    line_start = line_number + 1 + len(error_lines)//2
                )
                
                curses_add_lines(
                    win,
                    [('▸'+line,color) for (line,color) in history_lines[:(max_y-line_number)]],
                    line_number+1,
                    wrap_x=True
                )
        else:
            max_line = max_y-trunc
            _ = curses_add_lines(win, sub_lines[:max_line])
            _ = curses_add_lines(win, end_lines, max_line, wrap_x=True)

        win.move(0, 0)
        return win
