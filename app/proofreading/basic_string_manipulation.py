import webbrowser

from app.utils.constants import SYMBOLS
from app.proofreading.helpers import is_acronym
    
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

VOWELS = "aeiou"
def pluralize(word: str) -> str:
    """Return pluralized form of word based on general heuristic rules.
    Cannot go from plural to singular, and will not work on some words.\n
    e.g. \"cand[y]\" -> \"cand[ies]\""""
    
    if is_acronym(word):
        return word + 's'
        
    last_1 = word[-1]
    last_2 = word[-2:]
    if last_2 in ['ss','ch','sh'] or last_1 in ['s','x','z']:
        return word + 'es'
    elif last_2[0] not in VOWELS and last_1 == 'y':
        return word[:-1] + 'ies'
    elif ((val := last_2) == 'fe') or ((val := last_1) == 'f'):
        return word[:-len(val)] + 'ves'
    else:
        return word + 's'

def past_tensifier_simple(word: str) -> str:
    """Return past-tense of present-tense word based on general heuristic rules.
    Cannot go from past-tense to present-tense.\n
    e.g. \"pani[c]\" -> \"pani[cked]\""""
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

# the next two functions are identical, but it's helpful for them 
# to have different names (see: action.py, MAIN_OPTIONS)
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
    
