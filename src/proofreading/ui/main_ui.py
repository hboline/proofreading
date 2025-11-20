# ruff: noqa: F405
from typing import Dict, List
from functools import partial
import traceback

import curses

from .prompts import *
from .utils import COLOR_GRAY, COLOR_RED, COLOR_GREEN, curses_add_lines
from ..common import BaseUI, KEY, KEY_IGNORE, UIResult, FuncContainer, FuncType, PasteOption, Line, Action
from ..prooftools import *
from ..controller import close_app, filesave, clear_history

class MainUI(BaseUI):
    lines = [
        "Choose option: ",
        "[space] chain commands",
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
        KEY.tab: ManualInput(),
        ';': AddSessionRule(),
        '1': hyphenate,
        '2': DeleteSymbol(none_symbol='2'),
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
    }

    def draw(self, state) -> curses.window:
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
   
    def run(self, state) -> UIResult:
        win = self.draw(state)
        
        user_input: str = ''

        user_input = curses.keyname(win.getch()).decode()
        curses.flushinp()
        
        output: UIResult = UIResult(error = state.error)
        
        # ignore certain keypresses (e.g. curses.KEY_RESIZE)
        if user_input in KEY_IGNORE:
            return output

        # view error traceback and optionally enter debug mode
        if user_input == '/':
            win.clear()
            line_num = 0
            if state.error is not None:
                tb = traceback.format_tb(state.error.__traceback__)
                tb_lines: List[Line] = [
                    (line, COLOR_GRAY())
                    for level
                    in tb
                    for line
                    in level.splitlines()
                ]
                line_num = curses_add_lines(win, tb_lines, wrap_x = True)
            curses_add_lines(
                win,
                [
                    ("[any] enter debugger", COLOR_RED()),
                    ("[esc] continue", COLOR_GREEN())
                ],
                line_num+2
            )
            
            choice = ''
            while choice in KEY_IGNORE:
                choice = curses.keyname(win.getch()).decode()
                
            if choice == KEY.esc:
                return output
            else:
                curses.endwin()
                breakpoint()
        
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
            if not isinstance(action, FuncContainer):
                action = FuncContainer(action)
            output.action = action

        return output
