from functools import partial
from typing import Callable, List

import curses

from ..common import Line

COLOR_GRAY = partial(curses.color_pair, 1)
COLOR_RED = partial(curses.color_pair, 2)
COLOR_GREEN = partial(curses.color_pair, 3)

def curses_add_lines(
    win: curses.window,
    lines: Line | List[Line],
    line_start: int = 0,
    wrap_x = False,
) -> int:
    """Line: str | Tuple[str, int] | Tuple[str, Callable[..., int]]"""
    if not isinstance(lines, list):
        lines = [lines]
    
    line_number = 0
    max_y, max_x = win.getmaxyx()
    y_offset = 0
    for line_number, line in enumerate(lines):
        text: str = ''
        attr: int | Callable = 0
        
        line_number += line_start + y_offset
        
        if isinstance(line, str):
            text = line
            attr = 0
        elif isinstance(line, tuple):
            text, attr = line
            if isinstance(attr, Callable):
                attr = attr()
        try:
            assert isinstance(text, str)
            assert isinstance(attr, int)
            
            if wrap_x is False:
                text = text[:max_x]
            else:
                y_offset += len(text)//max_x
                text = text[:(max_y - line_number)*max_x]
                
            win.addstr(line_number, 0, text, attr)
        except curses.error:
            pass

    return line_number
