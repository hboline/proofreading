from rapidfuzz.fuzz import partial_ratio

from .digest import get_filename, load_document

class File():
    def __init__(self):
        self.filename = get_filename()
        self.doc = load_document(self.filename)

    def get_page_number(self, search: str) -> int|None:
        best_page = None
        best_score = 0.0

        for page, text in self.doc.items():
            score = partial_ratio(search, text)
            if score > best_score and score > 75.0:
                best_page = page
                best_score = score

        return best_page
        
