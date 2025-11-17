from __future__ import annotations
from typing import Callable, Optional, Dict, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum, auto

if TYPE_CHECKING:
    from .app import State

class PasteOption(Enum):
    Bracketed = auto(),
    Raw = auto(),
    Nothing = auto(),

class FuncType(Enum):
    Default = auto(),
    NoCopy = auto(),
    Super = auto(),

@dataclass
class FuncContainer:
    func: Callable
    func_type: FuncType = FuncType.Default
    paste_type: PasteOption = PasteOption.Bracketed
    special: bool = False
    special_default: Optional[str] = None

    def __post_init__(self):
        if self.special is True:
            assert self.special_default is not None
