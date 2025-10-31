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

@dataclass
class SpecialFunc():
    func: Callable
    none_value: str

@dataclass
class FuncContainer:
    func: Callable | SpecialFunc
    func_type: FuncType = FuncType.Default
    paste_type: PasteOption = PasteOption.Bracketed
    
Line: TypeAlias = str | Tuple[str, int] | Tuple[str, Callable[..., int]]
Action: TypeAlias = str | Callable | FuncContainer | SpecialFunc

@dataclass
class UIResult():
    ui: Optional[str] = None
    action: Optional[Action] = None
    error: Optional[Exception] = None
    
