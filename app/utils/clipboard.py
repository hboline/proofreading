import pyperclip as ppc
import pyautogui as pag

from .constants import LIGDICT

def ligature_parser(input: str) -> str:
    for k, v in LIGDICT.items():
        input = input.replace(k, v)
    return input
    
class Clipboard():
    def __init__(self, value: str | None = None) -> None:
        # optionally set clipboard value
        if value is not None:
            self.value = value
        else:
            self.value: str
            
    def save(self):
        self.value = ppc.paste()
    
    def reset(self):
        ppc.copy(self.value)

    def get(self):
        return ligature_parser(
            ppc.paste().replace('\r\n',' ')
        ).strip("[]")

    def set(self, word: str):
        ppc.copy(word)

    def copy(self):
        pag.hotkey('ctrl','c')
    
    def paste(self):
        pag.hotkey('ctrl','v')
