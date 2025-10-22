import pyperclip as ppc
import pyautogui as pag

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

        def copy(self):
            pag.hotkey('ctrl','c')
        
        def paste(self):
            pag.hotkey('ctrl','v')

        # maybe this shouldn't be here?
        def filesave(self):
            pag.hotkey('ctrl','s')
