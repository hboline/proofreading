from typing import Callable, Iterable, Literal, Optional
from functools import partial

import curses
from curses.textpad import Textbox

from .utils import COLOR_GREEN
from ..prooftools import paster, delete_symbol
from ..common import SYMBOLS, BaseUI, UIResult, FuncContainer, FuncType, FuncChain, containerize

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
    curs: int = 2,
    getch: bool = False,
) -> str:
    validator = _textbox_validator(*validation_chars)

    curses.curs_set(curs)
    _, max_x = win.getmaxyx()
    
    if message is not None:
        win.addstr(y, x, message, text_color)
        win.refresh()
        
    if getch:
        # curses.flushinp()
        ch = curses.keyname(win.getch()).decode()
        return ch
    
    assert message is not None
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

    def __init__(self, alt_val=False):
        self.alt_val = alt_val
    
    def run(self, state) -> UIResult:
        if self.alt_val is True:
            validation_chars = (10,13,93)
        else:
            validation_chars = (10,13)
        
        win = self.draw(state)
        
        output = UIResult("main")
        
        try:
            input = _prompt(
                win,
                2, 0,
                "[tab] manual input: ",
                n_lines=4,
                validation_chars=validation_chars
            )
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
            key_input = _prompt(win, 3, 0, "set rule key: ", error_message="+in key").lower()
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

        input = _prompt(
            win,
            5, 0,
            "[2] delete symbol: " + ' '.join(f"[{ch}]" for ch in SYMBOLS),
            curs=0,
            getch=True
        )
        
        output: UIResult = UIResult("main")
        output.action = FuncContainer(partial(
            delete_symbol,
            symbol_to_remove=input,
            _none_symbol=self.none_symbol,
        ))

        return output

# I can't really think of another way to enforce this other than
# adding some additional attribute to the Actions in ACTIONS in main_ui
VALID_CHAIN_COMMANDS = {
    '1', '2', '3', '4', 'r', 's', 'd', 'f', 'g',
}

class ChainCommands(BaseUI):
    def run(self, state) -> UIResult:
        from .main_ui import MainUI
        actions = MainUI().actions
        
        win = self.draw(state)

        input = _prompt(
            win,
            1, 0,
            "[space] chain commands: ",
            validation_chars=(32,)
        )

        output = UIResult("main")

        valid = [com for com in input if com in VALID_CHAIN_COMMANDS]
        invalid = [com for com in input if com not in VALID_CHAIN_COMMANDS]
        
        if len(invalid) > 0:
            output.error = Exception(f"removed invalid commands from chain: {''.join(invalid)}")
        
        actions = MainUI().actions
        chain: FuncChain = FuncChain(
            state,
            [containerize(actions[com]) for com in valid]
        )

        output.action = chain
        
        return output

