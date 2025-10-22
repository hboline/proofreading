import curses

from dataclasses import dataclass
from typing import Optional

from .utils import Clipboard, Window
from .ui import MainUI, OptionsUI, UIResult

@dataclass
class Vars():
    convert_english: bool
    result: Optional[str]
        
@dataclass
class State():
    screen: curses.window
    active_ui: Optional[str]
    error: Optional[Exception]
    vars: Vars

class App():
    ui_map = {
        "main": MainUI(),
        "options": OptionsUI(),
    }
    
    def __init__(
        self,
        stdscr,
        reader_window_name: str = "adobe",
        clipboard_value: str | None = None,
    ):
        self.stdscr = stdscr
        self.clipboard = Clipboard(clipboard_value)
        self.reader_window = Window(reader_window_name)
        self.process_window = Window()
        self.state = State(
            screen = stdscr,
            active_ui = "main",
            error = None,
            vars = Vars(
                convert_english = True,
                result = None
            )
        )

    def run(self):
        while self.state.active_ui is not None:
            ui = self.ui_map[self.state.active_ui]
            result = ui.run(self.state)
            self.handle_result(result)

    def handle_result(self, result: UIResult):
        pass
        
            
