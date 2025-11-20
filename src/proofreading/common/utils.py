from typing import Any

def name(object: Any) -> str:
    return object.__class__.__name__

def istype(object: Any, type: str) -> bool:
    return name(object) == type
