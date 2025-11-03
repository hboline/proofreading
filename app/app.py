from dataclasses import dataclass
from typing import Callable, List, Optional
import inspect

from functools import partial
import curses

from app.utils import Clipboard, Window, FuncContainer, FuncType, PasteOption
from app.ui import MainUI, OptionsUI, UIResult, BaseUI
from app.actions import function_stringifier

@dataclass
class Vars():
    convert_english: bool
    show_output: bool

@dataclass
class State():
    screen: curses.window
    clipboard: Clipboard
    reader_window: Window
    process_window: Window
    active_ui: Optional[BaseUI]
    error: Optional[Exception]
    action_history: List[str]
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
            action_history = [],
            vars = Vars(
                convert_english = True,
                show_output = True,
            )
        )

    def run(self):
        while self.state.active_ui is not None:
            result = self.state.active_ui.run(self.state)
            try:
                self.handle_result(result)
            except Exception as e:
                self.state.error = e

    def process_action(self, FC: FuncContainer):
        func = FC.func
        func_type = FC.func_type
        paste_type = FC.paste_type
        is_special = FC.special
        special_default = FC.special_default

        args = list()
        kwargs = dict()
        
        reader = self.state.reader_window
        c = self.state.clipboard
       
        if is_special is True:
            input = curses.keyname(self.state.screen.getch()).decode()
            if input == special_default:
                args.append(None)
            else:
                args.append(input)
        
        c.save()
       
        # process input based on function type
        word: str = ''
        match func_type:
            case FuncType.Default:
                reader.activate()
                c.copy()
                word = c.get()
            case FuncType.NoCopy:
                assert isinstance(func, partial)
                word = func.args[0]
                func = func.func
            case FuncType.Super:
                func(self) # I could also just "try except" this
                return     # instead of FuncType.Super
        
        func_kwargs = {k:str(v.annotation) for k,v in inspect.signature(func).parameters.items()}
        for k,v in func_kwargs.items():
            if v == 'State':
                kwargs[k] = self.state
        
        # process action function
        try:
            result = func(word, *args, **kwargs)
        except AssertionError:
            c.reset()
            raise Exception("input is not string")
        except Exception as e:
            c.reset()
            raise e
        else:
            args.insert(0, word)
            
            self.state.action_history.insert(0, 
                f"{function_stringifier(func, *args)}" + \
                (f" -> \"{result}\"" if result and self.state.vars.show_output else '')
            )
            
            # process function output based on paste type
            match paste_type:
                case PasteOption.Bracketed:
                    c.set(f"[{result}]")
                case PasteOption.Raw:
                    c.set(result)
                case PasteOption.Nothing:
                    c.reset()
                    return
            c.paste()
            c.reset()
        
    def handle_result(self, result: UIResult):
        # check next UI
        if result.ui:
            self.state.active_ui = self.ui_map[result.ui]
        
        # check for error
        if result.error:
            self.state.error = result.error
        else:
            self.state.error = None

        # check for actions
        if result.action:
            if isinstance(result.action, Callable):
                self.process_action(FuncContainer(result.action))
            elif isinstance(result.action, FuncContainer):
                self.process_action(result.action)
               
