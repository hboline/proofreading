# ruff: noqa: F403, F405
from dataclasses import dataclass
from functools import partial
from typing import Callable
from enum import Enum, auto

from .proofreading import * 
from .utils import KEY

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

MAIN_ACTIONS = {
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
}
