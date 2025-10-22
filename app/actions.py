# ruff: noqa: F403, F405
from functools import partial
import webbrowser

from proofreading import * 

def look_up_word(word: str) -> None:
    try:
        assert webbrowser.open(
            "https://www.merriam-webster.com/dictionary/"
            f"{word}"
        )
    except AssertionError:
        raise Exception("webbrowser: failed to open browser")

MAIN_ACTIONS = {
    '1': hyphenate,
    '2': delete_symbol,
    '3': lower,
    '4': upper,
    '9': look_up_word,
    'e': get_word,
    'r': flip_words,
    't': partial(paster, "Then, "),
    'a': partial(paster, "and"),
    'd': lambda: None
}
