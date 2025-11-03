# ruff: noqa: F403, F405
from functools import partial
from typing import Callable, Dict

from app.helpers import *
from app.proofreading import * 
from app.utils import KEY, FuncContainer, PasteOption, FuncType, Action

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
        (f"({', '.join(str(arg) for arg in args)})" if args else '')
    
    return func_string
    
MAIN_ACTIONS: Dict[str, Action] = {
    '1': hyphenate,
    '2': FuncContainer(delete_symbol, special = True, special_default='2'),
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
    ',': FuncContainer(filesave, FuncType.Super),
    '-': FuncContainer(clear_history, FuncType.Super),
    KEY.esc: FuncContainer(close_app, FuncType.Super),
}

OPTIONS_ACTIONS = {
    '1': FuncContainer(toggle_convert_english, FuncType.Super),
    '2': FuncContainer(toggle_show_output, FuncType.Super),
}

