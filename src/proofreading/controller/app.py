from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import inspect
from functools import partial

import curses

from proofreading.common.utils import containerize

from .utils import function_stringifier
from .clipboard import Clipboard
from .window import Window
from ..prooftools import chain
from ..common import BaseUI, UIResult, FuncContainer, FuncType, Action, PasteOption, FuncChain, istype

@dataclass
class Vars():
    convert_english: bool
    show_output: bool

@dataclass
class State():
    screen: curses.window
    active_ui: Optional[str]
    error: Optional[Exception]
    action_history: List[str]
    session_rules: Dict[str, str] = field(default_factory=dict)
    vars: Vars = field(default_factory=lambda: Vars(
       convert_english=True,
       show_output=True,
   ))
    
class App():
    def __init__(
        self,
        stdscr,
        reader_window_name: str = "adobe",
        clipboard_value: str | None = None,
    ):
        from ..ui import activate_ui
        self.activate_ui = activate_ui
        
        self.clipboard = Clipboard(clipboard_value)
        self.reader = Window(reader_window_name)
        self.process = Window()
        
        self.state = State(
            screen = stdscr,
            active_ui = "main",
            error = None,
            action_history = [],
        )

    def run(self):
        while self.state.active_ui is not None:
            result = self.activate_ui(self.state.active_ui, self.state)
            try:
                self.handle_ui_result(result)
            except Exception as e:
                self.state.error = e

    def handle_ui_result(self, result: UIResult):
        # check next UI
        if result.ui:
            self.state.active_ui = result.ui
        
        # check for error
        if result.error:
            self.state.error = result.error
        else:
            self.state.error = None

        # check for actions
        if (action := result.action):
            self.process_action(action)
               
    def get_result(
        self,
        func: Callable,
        func_type: FuncType,
        input: Optional[str] = None
    ) -> Tuple[Optional[str], Callable, List[Any], Dict[Any, Any]]:
        # perform actions based on FuncType
        args = list()
        kwargs = dict()
        match func_type:
            case FuncType.Default:
                assert input is not None
                args.append(input)
            case FuncType.NoCopy | FuncType.Dummy:
                assert isinstance(func, partial)
                args += [*func.args]
                kwargs |= {k:v for k,v in func.keywords.items()}
                func = func.func
            case FuncType.Super:
                func(self)
                return None, func, args, kwargs
            
        # get state kwarg if necessary
        kwargs |= {
            k:self.state
            for k,v
            in inspect.signature(func).parameters.items()
            if str(v.annotation) == 'State'
        }

        assert func_type is not FuncType.Super
        output: str = func(*args, **kwargs)
        
        return output, func, args, kwargs
    
    def process_action(self, container: Action):
        if isinstance(container, BaseUI):
            return self.handle_ui_result(container.run(self.state))
        
        self.clipboard.save()
        self.reader.activate()
        self.clipboard.copy()
        input = self.clipboard.get()

        if isinstance(container, FuncChain):
            result = input
            for link in container.chain:
                result, *_ = self.get_result(link.func, link.func_type, result)
            assert result is not None
            container = FuncContainer(partial(chain, _input = result), FuncType.Dummy)
        
        try:
            result, func, args, kwargs = self.get_result(container.func, container.func_type, input)
        except Exception as e:
            raise e
        else:
            if container.func_type == FuncType.Super:
                return
        finally:
            self.clipboard.reset()

        self.state.action_history.insert(0,
            f"{function_stringifier(func, *args, **kwargs)}" + (
                f" -> \"{result}\""
                if result is not None
                and self.state.vars.show_output
                and container.func_type is not FuncType.NoCopy
                else ''
            )
        )

        # switch to reader window and paste based on PasteOption
        if not self.reader.is_active():
            self.reader.activate()
        match container.paste_type:
            case PasteOption.Nothing:
                return
            case PasteOption.Bracketed:
                self.clipboard.set(f"[{result}]")
            case PasteOption.Raw:
                self.clipboard.set(f"{result}")
        self.clipboard.paste()
        self.clipboard.reset()
            
