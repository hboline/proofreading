from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Tuple, TypeAlias, Optional
from dataclasses import dataclass
from enum import Enum, auto

import curses

if TYPE_CHECKING:
    from ..controller import State
    from .types import RecursiveFunc

Line: TypeAlias = str | Tuple[str, int] | Tuple[str, Callable[..., int]]

class BaseUI:
    def run(self, state: State) -> UIResult:
        raise NotImplementedError

    def draw(self, state: State) -> curses.window:
        return state.screen

class PasteOption(Enum):
    Bracketed = auto(),
    Raw = auto(),
    Nothing = auto(),

class FuncType(Enum):
    Default = auto(),
    NoCopy = auto(),
    Super = auto(),
    Prompt = auto(),

@dataclass
class FuncContainer:
    func: Callable | BaseUI
    func_type: FuncType = FuncType.Default
    paste_type: PasteOption = PasteOption.Bracketed

Action: TypeAlias = Callable | FuncContainer | BaseUI

class RecursiveFunc:
    def __init__(self, action: Action, queue: Optional[RecursiveFunc]):
        self.action = action
        self.queue = queue
            
@dataclass
class UIResult():
    ui: Optional[str] = None
    action: Optional[FuncContainer] = None
    error: Optional[Exception] = None
