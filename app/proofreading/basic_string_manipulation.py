import webbrowser

from ..utils.constants import SYMBOLS
    
def delete_symbol(word: str, symbol_to_remove: str | None) -> str:
    if symbol_to_remove is None:
        for sym in SYMBOLS:
            word = word.replace(sym,'')
    elif symbol_to_remove in SYMBOLS:
        word = word.replace(symbol_to_remove, '')
    else:
        raise ValueError(f"delete symbol: no match for {symbol_to_remove}")
    return word

def hyphenate(word: str) -> str:
    if (new := word.replace(' ','-')) == word:
        word = word.replace('-',' ')
    else:
        word = new
    return word

def upper(word: str) -> str:
    word = word.title()
    return word

def lower(word: str) -> str:
    word = word.lower()
    return word

def pluralize(word: str) -> str:
    if word[-1] == 's':
        return word[:-1]
    else:
        return word + 's'

VOWELS = "aeiou"
def past_tensifier_simple(word: str) -> str:
    if word[-1] == 'e':
        return word + 'd'
    elif word[-1] == 'y' and word[-2] not in VOWELS:
        return word[:-1] + "ied"
    elif word[-1] == 'c':
        return word + "ked"
    elif (
            word[-1] not in {'w','x','y'} and
            word[-2] in VOWELS and
            not any(letter in VOWELS for letter in word[:-2])
        ):
        return word + word[-1] + "ed"
    else:
        return word + "ed"

def flip_words(words: str) -> str:
    words = ' '.join(words.split()[::-1])
    return words

def paster(word: str) -> str:
    return word

def get_word(word: str) -> str:
    return word

def google_word(word: str) -> None:
    try:
        assert webbrowser.open(
            "https://www.google.com/search?q="
            f"{'+'.join(word.split())}"
        )
    except AssertionError:
        raise Exception("webbrowser: failed to open browser")

def look_up_word(word: str) -> None:
    try:
        assert webbrowser.open(
            "https://www.merriam-webster.com/dictionary/"
            f"{word}"
        )
    except AssertionError:
        raise Exception("webbrowser: failed to open browser")
    
