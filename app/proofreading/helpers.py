from enum import Enum, auto

def is_acronym(input: str):
    return all(letter.isupper() for letter in input)

class Case(Enum):
    Lower = auto()
    Upper = auto()
    Acronym = auto()

def check_case(word: str) -> Case:
    if is_acronym(word):
        return Case.Acronym
    if word.isupper():
        return Case.Upper
    else:
        return Case.Lower
