from types import SimpleNamespace

KEY = SimpleNamespace({
    "esc": '^[',
    "bksp": '^H',
    "tab": '^I',
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
    '\r': 'fl',
    # symbols
    '’': '\'',
    '{': '-', # this one is a little suspicious
    '−': '-',
    '–': '-',
    # accented latin letters (Type 1)
    '´e': 'é',
    '¨o': 'ö',
    '¨a': 'ä',
    # accented latin letters (Type 2)
    '\x7fo': 'ö',
    '\x13': 'é',
    # U32 characters? E.g., equation symbols
    '\U00100000': '-',
}

# common errors with defined fixes
COMERRDICT = {
    # contractions
    "doesn't": "does not",
    "didn't": "did not",
    "can't": "cannot",
    "isn't": "is not",
    "it's": "it is",
    "won't": "will not",
    "aren't": "are not",
    "that's": "that is",
    "let's": "let us",
    "hasn't": "has not",
    "don't": "do not",
    "we're": "we are",
    "we'll": "we will",
    "wouldn't": "would not",
    "couldn't": "could not",
    "we've": "we have",
    "wasn't": "was not",
    # other
    "towards": "toward",
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
}

PRONOUNDICT = {
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
    "sec.": "Section",
    "thrm": "Theorem",
    "thm.": "Theorem",
    "eq.": "Eq",
    "eqs.": "Eqs",
    "fig.": "Figure",
    "tab.": "Table",
    "def.": "Definition",
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
    "characteris": "characteriz",
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
    "analys": "analyz",
    "discretis": "discretiz",
    "parameteris": "parameteriz",
    "linearis": "lineariz",
    "specialis": "specializ",
    "formalis": "formaliz",
    "regularis": "regulariz",
    "penalis": "penaliz",
    "localis": "localiz",
    "normalis": "normaliz",
    "standardis": "standardiz",
    "programme": "program",
    "stabilis": "stabiliz",
    "prioritis": "prioritiz",
    "fulfil": "fulfill",
    "initialis": "initializ",
    "dimensionalis": "dimensionaliz",
}


SYMBOLS = [
    '-',
    '\'',
    ' ',
    '.',
    ',',
    '"',
]
