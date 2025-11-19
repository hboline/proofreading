from typing import Callable, TYPE_CHECKING

from ..utils import Action, FuncContainer

def function_stringifier(
    func: Action,
    *args
) -> str:
    if isinstance(func, FuncContainer):
        func = func.func
    elif isinstance(func, Callable):
        func = func

    func_name = str(func).split()[1]
    args = [f"\"{arg}\"" if isinstance(arg, str) else arg for arg in args]

    func_string = f"{func_name}" + \
        (f"({', '.join(str(arg) for arg in args)})" if (args and args != ['\"\"']) else '')
    
    return func_string
