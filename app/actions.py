# ruff: noqa: F403, F405
from functools import partial
from typing import Callable, Dict

from app.proofreading import * 
from app.utils import KEY, SpecialFunc, FuncContainer, PasteOption, FuncType, Action

def function_stringifier(
    func: Action,
    *args
) -> str:
    if isinstance(func, str):
        return func
    elif isinstance(func, SpecialFunc | FuncContainer):
        func = func.func
    else:
        func = func

    func_name = str(func).split()[1]
    args = [f"\"{arg}\"" if isinstance(arg, str) else arg for arg in args]

    func_string = f"{func_name}" + \
        (f"({', '.join(str(arg) for arg in args)})" if args else '')
    
    return func_string
    
MAIN_ACTIONS: Dict[str, str | Callable | SpecialFunc | FuncContainer] = {
    '1': hyphenate,
    '2': SpecialFunc(delete_symbol, '2'),
    '3': lower,
    '4': upper,
    '9': FuncContainer(look_up_word, FuncType.Default, PasteOption.Nothing),
    '0': FuncContainer(google_word, FuncType.Default, PasteOption.Nothing),
    'e': get_word,
    'r': flip_words,
    't': FuncContainer(partial(paster, "Then, "), FuncType.NoCopy),
    'a': FuncContainer(partial(paster, "and"), FuncType.NoCopy),
    's': pluralize,
    'd': past_tensifier_simple,
    'f': common_error_parser,
    'c': FuncContainer(partial(paster, ':'), FuncType.NoCopy, PasteOption.Raw),
    ',': "filesave",
    '-': "clear history",
    KEY.esc: "exit",
}

OPTIONS_ACTIONS = {
    '1': "toggle convert english",
    '2': "toggle show output",
}
