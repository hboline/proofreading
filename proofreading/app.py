from dataclasses import dataclass, astuple
from typing import Callable, List, Optional
import inspect

from functools import partial
import curses

from .utils import Clipboard, Window, FuncContainer, FuncType, PasteOption, UIResult
from .ui import MainUI, OptionsUI, BaseUI
from .actions import function_stringifier

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
        # explicit definition of FuncContainer types
        func: Callable
        func_type: FuncType
        paste_type: PasteOption
        is_special: bool
        special_default: Optional[str]
        
        # get all fields of FuncContainer as tuple
        func,\
        func_type,\
        paste_type,\
        is_special,\
        special_default\
        = astuple(FC)
        
        # get reader window, clipboard object, and save clipboard
        reader = self.state.reader_window
        c = self.state.clipboard
        c.save()
       
        # NOTE: this is only used for special functions and for printing function to history
        args = list()
        
        # get additional input if function is special (consider baking this into FuncType somehow)
        if is_special is True:
            input = curses.keyname(self.state.screen.getch()).decode()
            if input == special_default:
                args.append(None)
            else:
                args.append(input)
       
        # perform actions based on FuncType
        word: str = ''
        result: Optional[str] = None
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
                result = func(self) # NOTE: might need a better way to handle this
                if result is None:
                    return
        
        # get any additional args/kwargs
        # NOTE: this currently only looks for a State object from the app and nothing else
        kwargs = dict()
        func_kwargs = {k:str(v.annotation) for k,v in inspect.signature(func).parameters.items()}
        for k,v in func_kwargs.items():
            if v == 'State':
                kwargs[k] = self.state
        
        # call function, get output (if any), and catch exceptions
        try:
            if func_type is not FuncType.Super:
                result = func(word, *args, **kwargs)
            assert result is not None
        except AssertionError:
            raise Exception("input is not a string")
        except Exception as e:
            raise e
        finally:
            c.reset()

        # get string representation of function for printing function to history in main UI
        args.insert(0, word)
        self.state.action_history.insert(0, 
            f"{function_stringifier(func, *args)}" + \
            (f" -> \"{result}\"" if result and self.state.vars.show_output else '')
        )
        
        # switch to reader window and paste based on PasteOption
        if not reader.is_active():
            reader.activate()
        match paste_type:
            case PasteOption.Nothing:
                return
            case PasteOption.Bracketed:
                c.set(f"[{result}]")
            case PasteOption.Raw:
                c.set(result)
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
               
