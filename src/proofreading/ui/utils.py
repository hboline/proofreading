from functools import partial
from collections.abc import Callable

import curses

from ..common import KEY, Line

_active_color_pairs: set[int] = set()


def init_colors() -> None:
    _active_color_pairs.clear()
    if not curses.has_colors():
        return

    try:
        curses.start_color()
    except curses.error:
        return

    gray = 245 if curses.COLORS > 245 else curses.COLOR_WHITE
    for pair, foreground in (
        (1, gray),
        (2, curses.COLOR_RED),
        (3, curses.COLOR_GREEN),
    ):
        if pair >= curses.COLOR_PAIRS or foreground >= curses.COLORS:
            continue
        try:
            curses.init_pair(pair, foreground, curses.COLOR_BLACK)
        except curses.error:
            continue
        _active_color_pairs.add(pair)


def color_pair(pair: int) -> int:
    return curses.color_pair(pair) if pair in _active_color_pairs else 0


COLOR_GRAY = partial(color_pair, 1)
COLOR_RED = partial(color_pair, 2)
COLOR_GREEN = partial(color_pair, 3)


def set_cursor(visibility: int) -> None:
    try:
        curses.curs_set(visibility)
    except curses.error:
        pass


def read_key(win: curses.window) -> str:
    key = win.getch()
    if key == -1:
        return ""
    if key in (8, 127, curses.KEY_BACKSPACE):
        return KEY.bksp
    if key == 9:
        return KEY.tab
    if key == 27:
        return KEY.esc

    name = curses.keyname(key).decode(errors="replace")
    if name in ("KEY_BACKSPACE", "^H", "^?"):
        return KEY.bksp
    return name


def curses_add_lines(
    win: curses.window,
    lines: Line | list[Line],
    line_start: int = 0,
    wrap_x=False,
) -> int:
    """Line: str | Tuple[str, int] | Tuple[str, Callable[..., int]]"""
    if not isinstance(lines, list):
        lines = [lines]

    line_number = 0
    max_y, max_x = win.getmaxyx()
    y_offset = 0
    for line_number, line in enumerate(lines):
        text: str = ""
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
                y_offset += len(text) // max_x
                text = text[: (max_y - line_number) * max_x]

            win.addstr(line_number, 0, text, attr)
        except curses.error:
            pass

    return line_number
