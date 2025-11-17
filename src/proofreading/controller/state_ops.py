from __future__ import annotations
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App

import curses
from pyautogui import hotkey

def close_app(*_):
    curses.endwin()
    os.system("cls")
    sys.exit()

def filesave(self: App):
    self.state.reader_window.activate()
    hotkey("ctrl","s")
    
def toggle_convert_english(self: App):
    self.state.vars.convert_english ^= True
    
def toggle_show_output(self: App):
    self.state.vars.show_output ^= True
    
def clear_history(self: App):
    self.state.action_history = []
 
