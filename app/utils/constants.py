from types import SimpleNamespace

KEY = SimpleNamespace({
    "esc": '^[',
    "bksp": '^H',
})

KEY_IGNORE = {
    '',
    "KEY_RESIZE",
}

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
    " —": ", ",
    # pronouns
    "his": "their",
    "him": "them",
    "he": "they",
    "her": "their",
    # "her" "them", # TODO: how do I handle this?
    "she": "they", 
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
    "favour": "favor",
}


SYMBOLS = [
    '-',
    '\'',
    ' ',
    '.',
    ',',
    '"',
]
