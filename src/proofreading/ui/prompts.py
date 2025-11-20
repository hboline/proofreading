from typing import Callable, Iterable, Optional
from functools import partial

import curses
from curses.textpad import Textbox

from proofreading.prooftools.basic_string_manipulation import delete_symbol

from .utils import COLOR_GREEN
from ..prooftools import paster
from ..common import BaseUI, UIResult, FuncContainer, FuncType, PasteOption

def _textbox_validator(*args: int, getch: bool = False) -> Callable[[int], int]:
    def _textbox_validator_func(ch: int) -> int:
        if getch or ch in args:
            return 7
        return ch
    return _textbox_validator_func

def _prompt(
    win: curses.window,
    y: int = 0,
    x: int = 0,
    message: Optional[str] = None,
    n_lines: int = 1,
    text_color: int = COLOR_GREEN(),
    validation_chars: Iterable[int] = (10,13),
    error_message: Optional[str] = None,
) -> str:
    if message is None:
        return curses.keyname(win.getch()).decode()
    
    validator = _textbox_validator(*validation_chars)

    curses.curs_set(2)
    _, max_x = win.getmaxyx()
    
    win.addstr(y, x, message, text_color)
    subwin = curses.newwin(n_lines, max_x-len(message), y, len(message))
    box = Textbox(subwin)

    win.refresh()

    box.edit(validator)
    input = box.gather().replace('\n','').rstrip()

    if input == '':
        if error_message is None:
            error_message = "no text entered"
        elif error_message[0] == '+':
            error_message = "no text entered " + error_message.lstrip('+').lstrip()
        raise ValueError(error_message)

    curses.curs_set(0)
    return input

class ManualInput(BaseUI):
    def run(self, state) -> UIResult:
        win = self.draw(state)
        
        output = UIResult("main")

        try:
            input = _prompt(win, 2, 0, "[tab] manual input: ", n_lines=4)
        except ValueError as e:
            output.error = e
        else:
            output.action = FuncContainer(partial(paster, input), FuncType.NoCopy)

        return output

class AddSessionRule(BaseUI):
    def run(self, state) -> UIResult:
        win = self.draw(state)

        output: UIResult = UIResult("main")

        try:
            key_input = _prompt(win, 3, 0, "set rule key: ", error_message="+in key")
            value_input = _prompt(win, 4, 0, "   set value: ", error_message="+in value")
        except ValueError as e:
            output.error = e
        else:
            state.session_rules.update({key_input: value_input})

        return output

class DeleteSymbol(BaseUI):
    def __init__(self, none_symbol: str):
        self.none_symbol = none_symbol
    
    def run(self, state) -> UIResult:
        win = self.draw(state)

        input = _prompt(win)
        
        output: UIResult = UIResult("main")
        output.action = FuncContainer(partial(
            delete_symbol,
            symbol_to_remove=input,
            _none_symbol=self.none_symbol,
        ))

        return output

class ChainCommands(BaseUI):
    def run(self, state) -> UIResult:
        win = self.draw(state)
        win.addstr(1, 0, "[space] chain commands", COLOR_GREEN())
        return UIResult()
    # TODO: before I can proceed with this, I need to rewrite/reorganize the
    #       process_action function in controller.app. It does far too much in
    #       one pass and needs to be broken up into smaller pieces.
