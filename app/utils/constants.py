from types import SimpleNamespace
from typing import NamedTuple


CLEAR_CONSOLE = '\033[2J'
MOVE_CURSOR = '\033[H'

VALID_BASE_INPUT = {
   '`',
   '\x1b', #esc
   '0',
}

VALID_OPTIONS_INPUT = {
  '1',
  '`',
  '\x08', #backspace
  '\x1b', #esc
}

KEY = SimpleNamespace({
    "esc": '^[',
})

# Ligature (or other problematic) character codes for conversion
LIGDICT = {
    # ligatures
    '\x0c': 'fi',
    '\x0b': 'ff',
    '\x0e': 'ffi',
    # foreign/special letters
    '\x7fo': 'ö',
    # symbols
    '’': '\'',
    '{': '-', # this one is a little suspicious
    '−': '-',
}

# common errors with defined fixes
COMERRDICT = {
    # contractions
    "doesn't": "does not",
    "can't": "cannot",
    "isn't": "is not",
    "it's": "it is",
    "won't": "will not",
    "aren't": "are not",
    "that's": "that is",
    "let's": "let us",
    # other
    "put": "set",
    "the sequel": "what follows",
    "combing": "combining",
    "wellposedness": "well-posedness",
    "firstly": "first",
    "secondly": "second",
    "thirdly": "third",
    "fourthly": "fourth",
    "fifthly": "fifth",
    "sixthly": "sixth",
    "—": ", ", 
}

# abbreviations (need to be handled slightly differently)
# note: subsets (e.g. eq is in eqs) need to come first
ABBVDICT = {
    # abbreviations
    "sec.": "section",
    "thrm": "theorem",
    "thm.": "theorem",
    "eq.": "eq",
    "eqs.": "eqs",
    "fig.": "figure",
}

# english -> american conversion
EN2AMDICT = {
    "behaviour": "behavior",
    "neighbour": "neighbor",
    "minimis": "minimiz", # note: this takes care of minimises, minimiser, minimisers, etc.
    "maximis": "maximiz",
    "realis": "realiz",
    "optimis": "optimiz",
    "generalis": "generaliz",
    "symbolis": "symboliz",
    "utilis": "utiliz",
    "characteris": "charateriz",
    "modell": "model",
    "visualis": "visualiz",
    "homogenis": "homogeniz",
    "heterogenis": "heterogeniz",
    "emphasis": "emphasiz",
    "summaris": "summariz",
    "organis": "organiz",
    "labell": "label",
    "colour": "color",
    "individualis": "individualiz",
    "centre": "center",
    "travell": "travel",
}

SYMBOLS = [
    '-',
    '\'',
    ' ',
    '.',
]

WORDS = {
    "and": "and",
    "then": "Then, ",
    ".": ".",
    ":": ":",
    ";": ";",
}
