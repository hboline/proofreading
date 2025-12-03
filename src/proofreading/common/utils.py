from typing import Any, Callable

from .types import Action, FuncContainer

def name(object: Any) -> str:
    return object.__class__.__name__

def istype(object: Any, type: str) -> bool:
    return name(object) == type

def containerize(action: Callable | Action) -> FuncContainer | Action:
    if isinstance(action, Callable):
       return FuncContainer(action)
    else:
        return action
