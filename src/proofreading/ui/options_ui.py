from typing import Callable
from .base_ui import BaseUI
from .utils import COLOR_GRAY, COLOR_RED
from ..controller import toggle_convert_english, toggle_show_output
from ..utils import KEY, KEY_IGNORE, UIResult, FuncContainer, FuncType

import curses

class OptionsUI(BaseUI):
    lines = []

    actions = {
        '1': FuncContainer(toggle_convert_english, FuncType.Super),
        '2': FuncContainer(toggle_show_output, FuncType.Super),
    }

    to_other_ui = {
        KEY.bksp: "main",
    }
    
    def draw(self, state) -> curses.window:
        vars = state.vars
        win = state.screen
        win.clear()
        
        win.addstr(0, 0,
            "[1] toggle EN/US conversion ["
            f"{"EN->US" if vars.convert_english else "US->EN"}]"
        )
        win.addstr(1, 0,
            "[2] toggle history output ["
            f"{"show" if vars.show_output else "hidden"}]"
        )
        win.addstr(2,0,"[bksp] return to main", COLOR_GRAY())

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
        
        try:
            output.ui = self.to_other_ui[user_input]
        except KeyError:
            pass
        else:
            output.error = None
            return output
            
        try:
            action = self.actions[user_input]
        except KeyError:
            output.error = Exception(f"invalid input {user_input}")
        else:
            output.error = None
            output.action = FuncContainer(action) if isinstance(action, Callable) else action
        
        return output
