from dataclasses import dataclass, asdict
from typing import Callable, Optional
import os
import inspect

from functools import partial
from pyautogui import hotkey
import curses

from .utils import Clipboard, Window
from .ui import MainUI, OptionsUI, UIResult, BaseUI
from .actions import FuncContainer, FuncType, PasteOption, SpecialFunc

@dataclass
class Vars():
    convert_english: bool

@dataclass
class State():
    screen: curses.window
    clipboard: Clipboard
    reader_window: Window
    process_window: Window
    active_ui: Optional[BaseUI]
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
        self.state = State(
            screen = stdscr,
            clipboard = Clipboard(clipboard_value),
            reader_window = Window(reader_window_name),
            process_window = Window(),
            active_ui = self.ui_map["main"],
            error = None,
            vars = Vars(
                convert_english = True,
            )
        )

    def run(self):
        while self.state.active_ui is not None:
            result = self.state.active_ui.run(self.state)
            self.state.error = None
            try:
                self.handle_result(result)
            except Exception as e:
                self.state.error = e

    def process_action(self, FC: FuncContainer):
        func = FC.func
        func_type = FC.func_type
        paste_type = FC.paste_type

        args = list()
        kwargs = dict()
        
        reader = self.state.reader_window
        c = self.state.clipboard
        
        # TODO: not a big fan of this. a better version would loop to a new ui
        if isinstance(func, SpecialFunc):
            none_value = func.none_value
            func = func.func
            input = curses.keyname(self.state.screen.getch()).decode()
            if input == none_value:
                args.append(None)
            else:
                args.append(input)
            
        reader.activate()
        
        # process input based on function type
        word: str = ''
        match func_type:
            case FuncType.Default:
                c.save()
                c.copy()
                word = c.get()
            case FuncType.NoCopy:
                assert isinstance(func, partial)
                word = func.args[0]
                func = func.func
        
        vars_dict = asdict(self.state.vars)
        func_args = inspect.signature(func).parameters.keys()
        # kwargs = {k:v for k,v in vars_dict.items() if k in func_args}
        kwargs.update([(k,v) for k,v in vars_dict.items() if k in func_args])
        
        # process action function
        try:
            assert isinstance(word, str)
            result = func(word, *args, **kwargs)
        except AssertionError:
            raise Exception("input is not string")
        except Exception as e:
            raise e

        # process function output based on paste type
        match paste_type:
            case PasteOption.Bracketed:
                c.set(f"[{result}]")
            case PasteOption.Raw:
                c.set(result)
            case PasteOption.Nothing:
                return
        c.paste()
        
    def handle_result(self, result: UIResult):
        # check next UI
        if result.ui:
            self.state.active_ui = self.ui_map[result.ui]
        
        # check for error
        if result.error:
            self.state.error = result.error

        # check for actions
        if result.action:
            if isinstance(result.action, Callable | SpecialFunc):
                self.process_action(FuncContainer(result.action))
            elif isinstance(result.action, FuncContainer):
                self.process_action(result.action)
            elif isinstance(result.action, str):
                match result.action:
                    case "filesave":
                        self.state.reader_window.activate()
                        hotkey("ctrl","s")
                    case "exit":
                        curses.endwin()
                        os.system("cls")
                        exit()
                    case "toggle convert english":
                        self.state.vars.convert_english ^= True
                
