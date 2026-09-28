from types import SimpleNamespace

import pytest

from proofreading.common import KEY
from proofreading.ui import utils


@pytest.mark.parametrize(
    ("code", "name", "expected"),
    [
        (8, b"^H", KEY.bksp),
        (127, b"^?", KEY.bksp),
        (9, b"^I", KEY.tab),
        (27, b"^[", KEY.esc),
        (999, b"KEY_BACKSPACE", KEY.bksp),
        (ord("a"), b"a", "a"),
        (-1, b"", ""),
    ],
)
def test_read_key_normalizes_terminal_keys(monkeypatch, code, name, expected):
    monkeypatch.setattr(utils.curses, "keyname", lambda _: name)
    assert utils.read_key(SimpleNamespace(getch=lambda: code)) == expected


def test_init_colors_uses_basic_color_when_256_colors_are_unavailable(monkeypatch):
    pairs = []
    monkeypatch.setattr(utils, "_active_color_pairs", set())
    monkeypatch.setattr(utils.curses, "has_colors", lambda: True)
    monkeypatch.setattr(utils.curses, "start_color", lambda: None)
    monkeypatch.setattr(utils.curses, "COLORS", 8, raising=False)
    monkeypatch.setattr(utils.curses, "COLOR_PAIRS", 4, raising=False)
    monkeypatch.setattr(utils.curses, "init_pair", lambda *args: pairs.append(args))
    monkeypatch.setattr(utils.curses, "color_pair", lambda pair: pair * 10)

    utils.init_colors()

    assert pairs[0] == (1, utils.curses.COLOR_WHITE, utils.curses.COLOR_BLACK)
    assert utils.COLOR_GRAY() == 10
    assert utils.COLOR_RED() == 20
    assert utils.COLOR_GREEN() == 30


def test_no_color_or_cursor_support_uses_plain_text(monkeypatch):
    monkeypatch.setattr(utils, "_active_color_pairs", set())
    monkeypatch.setattr(utils.curses, "has_colors", lambda: False)
    monkeypatch.setattr(utils.curses, "curs_set", lambda _: (_ for _ in ()).throw(utils.curses.error()))

    utils.init_colors()
    utils.set_cursor(0)

    assert utils.COLOR_GRAY() == 0
    assert utils.COLOR_RED() == 0
