from enum import Enum, auto
import re

def is_acronym(input: str):
    """
        Check if the word is an acronym.
        
        e.g. "is_acronym("NASA") = True"
    """
    if input[-1] == 's':
        input = input[:-1]
    return input.isupper()

class Case(Enum):
    Lower = auto()
    Upper = auto()
    Acronym = auto()

def check_case(word: str) -> Case:
    if is_acronym(word):
        return Case.Acronym
    elif re.sub(r'[^A-Za-z]','',word).istitle():
        return Case.Upper
    else:
        return Case.Lower
