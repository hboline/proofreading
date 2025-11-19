from typing import Callable
from functools import partial

import curses
from curses.textpad import Textbox

from .base_ui import BaseUI
from .utils import COLOR_GREEN
from ..prooftools import paster
from ..utils import UIResult, FuncContainer, FuncType, PasteOption

def _textbox_validator(*args: int) -> Callable[[int], int]:
    def _textbox_validator_func(ch: int) -> int:
        if ch in args:
            return 7
        return ch
    return _textbox_validator_func

class ManualInput(BaseUI):
    def draw(self, state) -> curses.window:
        return state.screen

    def run(self, state) -> UIResult:
        win = self.draw(state)
        win.addstr(1, 0,"[tab] manual input: ", COLOR_GREEN())
        curses.curs_set(2)
    
        validator = _textbox_validator(10,13)
        
        _, max_x = win.getmaxyx()

        subwin = curses.newwin(4, max_x-20, 1, 20)
        box = Textbox(subwin)
    
        win.refresh()

        box.edit(validator)
        input = box.gather().replace('\n','').rstrip()

        curses.curs_set(0)
    
        output: UIResult = UIResult("main")
        
        if input == '':
            output.error = Exception("no text entered")
        else:
            output.action = FuncContainer(partial(paster, input), FuncType.NoCopy)

        return output

class AddSessionRule(BaseUI):
    def draw(self, state) -> curses.window:
        return state.screen

    def run(self, state) -> UIResult:
        win = self.draw(state)
        win.addstr(2, 0, "set rule key: ", COLOR_GREEN())
        curses.curs_set(2)

        validator = _textbox_validator(10,13)

        output: UIResult = UIResult("main")

        _, max_x = win.getmaxyx()

        subwin_key = curses.newwin(1, max_x-14, 2, 14)
        box_key = Textbox(subwin_key)
    
        win.refresh()

        box_key.edit(validator)
        key_input = box_key.gather().replace('\n','').rstrip()
    
        if key_input == '':
            output.error = Exception("no text entered in key")
            return output
    
        win.addstr(3, 0, "   set value: ", COLOR_GREEN())

        subwin_value = curses.newwin(1, max_x-14, 3, 14)
        box_value = Textbox(subwin_value)

        win.refresh()

        box_value.edit(validator)
        value_input = box_value.gather().replace('\n','').rstrip()
    
        if value_input == '':
            output.error = Exception("no text entered in value")
            return output

        state.session_rules.update({key_input: value_input})

        curses.curs_set(0)

        return output

