from __future__ import annotations
from typing import TYPE_CHECKING, Callable, List, Tuple, TypeAlias, Optional
from dataclasses import dataclass
from enum import Enum, auto

import curses

if TYPE_CHECKING:
    from ..controller import State

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
    Dummy = auto(),

@dataclass
class FuncContainer:
    func: Callable
    func_type: FuncType = FuncType.Default
    paste_type: PasteOption = PasteOption.Bracketed

class FuncChain:
    def __init__(self, state: State, chain: List[FuncContainer | BaseUI]):
        self.state = state
        self.chain = self._base_ui_check(chain)

    def _base_ui_check(self, chain) -> List[FuncContainer]:
        for id, link in enumerate(chain):
            if isinstance(link, BaseUI):
                _, link, _ = link.run(self.state).unwrap()
                assert isinstance(link, FuncContainer)
                chain[id] = link
        return chain
        
Action: TypeAlias = FuncContainer | BaseUI
           
@dataclass
class UIResult():
    ui: Optional[str] = None
    action: Optional[Action | FuncChain] = None
    error: Optional[Exception] = None

    def unwrap(self) -> Tuple[
        Optional[str],
        Optional[Action | FuncChain],
        Optional[Exception],
    ]:
        return self.ui, self.action, self.error
