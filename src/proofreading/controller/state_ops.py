from __future__ import annotations
import os
import sys
from typing import TYPE_CHECKING

import curses
from pyautogui import hotkey

if TYPE_CHECKING:
    from .app import App

def close_app(*_):
    curses.endwin()
    os.system("cls")
    sys.exit()

def filesave(self: App):
    self.reader.activate()
    hotkey("ctrl","s")
    
def toggle_convert_english(self: App):
    self.state.vars.convert_english ^= True
    
def toggle_show_output(self: App):
    self.state.vars.show_output ^= True
    
def clear_history(self: App):
    self.state.action_history = []

def toggle_reader_mode(self: App):
    text = ""
    current = self.state.vars.reader
    if current == "adobe":
        self.state.vars.reader = "word"
        text = "the"
    elif current == "word":
        self.state.vars.reader = "adobe"
        text = "[the]"
    # self.clipboard.set(text)
    # self.state.clipboard_text = text
    self.clipboard.value = text
    self.reader.__init__(self.state.vars.reader)
