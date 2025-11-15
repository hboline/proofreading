import webbrowser
import re

from ..utils.constants import SYMBOLS
from ..prooftools.helpers import is_acronym
    
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

def upper(words: str) -> str:
    words = ' '.join(word[0].upper() + word[1:] for word in words.split())
    return words

def lower(word: str) -> str:
    word = word.lower()
    return word

VOWELS = "aeiou"
def pluralize(word: str) -> str:
    """
        Return pluralized (or depluralized) form of word based
        on general heuristic rules. May not always work correctly,
        and will not work on some words entirely.
    
        e.g. \"cand[y]\" -> \"cand[ies]\"
             \"defin[es]\" -> \"defin[e]\"
    """

    # check if word is already plural
    re_match = re.search("..s$", word)
    if re_match is not None:
        end = re_match.group() 
        if end == 'ies':
            return word.rstrip(end) + 'y'
        elif end == 'ves':
            return word.rstrip(end) + 'fe' if word[-1] in VOWELS else 'f'
        elif (end[-2:] == 'es' and (
                    word.rstrip(end)[-2:] in ['ss','ch','sh'] or
                    word.rstrip(end)[-1] in ['s','x','z'])
            ):
            return word.rstrip('s')
        elif end[-1] == 's':
            return word[:-1]
    
    # now attempt to pluralize the word
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

def to_past_tense(word: str) -> str:
    """
        Return past-tense of present-tense word based on
        general heuristic rules. Cannot go from past-tense
        to present-tense.
        
        e.g. \"pani[c]\" -> \"pani[cked]\"
    """
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

def to_present_participle(word: str) -> str:
    """
        Return present participle of present-tense word based
        on general heuristic rules. Cannot go from present
        participle to present-tense. Words such as "beginning"
        will not conjugate properly.
        
        e.g. \"hop\" -> \"hop[ping]\"
             \"hop[e]\" -> \"hop[ing]\"
    """
    if word[-1] == 'e':
        word = word.rstrip('e')
    elif word[-2:] == 'ie':
        word = word.rstrip('ie') + 'y'
    elif (
        sum(letter in VOWELS for letter in word) == 1 and
        word[-1] not in (VOWELS + 'x')
    ):
        word += word[-1]

    return word + 'ing'
        

def flip_words(words: str) -> str:
    words_list = words.split()
    if len(words_list) <= 1:
        raise Exception("not enough words to reverse")
    first_word = words_list[0]
    last_word = words_list[-1]
    if first_word.istitle() and not is_acronym(first_word):
        words_list[-1] = last_word.title()
        words_list[0] = first_word.lower()
    words = ' '.join(words_list[::-1])
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
    
