import pyperclip as ppc
import pyautogui as pag
import re

from ..common import LIGDICT

def ligature_parser(input: str) -> str:
    for k, v in LIGDICT.items():
        input = input.replace(k, v)
    return input
    
class Clipboard():
    def __init__(self, value: str | None = None) -> None:
        # optionally set clipboard value
        if value is not None:
            self.value = value
            self.set(self.value)
        else:
            self.value: str
            
    def save(self):
        self.value = ppc.paste()
    
    def reset(self):
        ppc.copy(self.value)

    def get(self):
        words: str = ppc.paste()
        words = re.sub('|'.join([
            r"\r\n[0-9]+",
            r"[0-9]+\r\n",
        ]), '', words)
        words = re.sub(r"\r\n", ' ', words)
        return ligature_parser(words).strip("[]")

    def set(self, word: str):
        ppc.copy(word)

    def copy(self):
        pag.hotkey('ctrl','c')
    
    def paste(self):
        pag.hotkey('shift')
        pag.hotkey('ctrl','v')

