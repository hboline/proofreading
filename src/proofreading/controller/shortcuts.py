import sys

import pyautogui


def shortcut(key: str) -> None:
    modifier = "command" if sys.platform == "darwin" else "ctrl"
    pyautogui.hotkey(modifier, key)
