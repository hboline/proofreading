from .base_ui import BaseUI
from .utils import UIResult, COLOR_GRAY, COLOR_RED
from ..controller import OPTIONS_ACTIONS
from ..utils import KEY, KEY_IGNORE

import curses

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
