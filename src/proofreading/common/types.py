from typing import Callable, Tuple, TypeAlias, Optional
from dataclasses import dataclass
from enum import Enum, auto

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

Line: TypeAlias = str | Tuple[str, int] | Tuple[str, Callable[..., int]]
Action: TypeAlias = Callable | FuncContainer

@dataclass
class UIResult():
    ui: Optional[str] = None
    action: Optional[FuncContainer] = None
    error: Optional[Exception] = None
