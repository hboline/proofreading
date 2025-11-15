from __future__ import annotations
from functools import partial
import os
import sys
from typing import TYPE_CHECKING

import curses
from curses.textpad import Textbox
from pyautogui import hotkey

COLOR_GREEN = partial(curses.color_pair, 3)

if TYPE_CHECKING:
    from app import App

def filesave(self: App):
    self.state.reader_window.activate()
    hotkey("ctrl","s")
    
def close_app(*_):
    curses.endwin()
    os.system("cls")
    sys.exit()
    
def toggle_convert_english(self: App):
    self.state.vars.convert_english ^= True
    
def toggle_show_output(self: App):
    self.state.vars.show_output ^= True
    
def clear_history(self: App):
    self.state.action_history = []

def _textbox_validator(ch: int) -> int:
    if ch in (10,13):
        return 7
    return ch

def manual_input(self: App) -> str:
    win = self.state.screen
    win.addstr(1, 0,"[tab] manual input: ", COLOR_GREEN())
    curses.curs_set(2)

    _, max_x = win.getmaxyx()

    subwin = curses.newwin(4, max_x-20, 1, 20)
    box = Textbox(subwin)
    
    win.refresh()

    box.edit(_textbox_validator)
    input = box.gather().replace('\n','').rstrip()

    if input == '':
        raise Exception("no text entered")

    curses.curs_set(0)
    
    return input

def add_session_rule(self: App):
    win = self.state.screen
    win.addstr(2, 0, "set rule key: ", COLOR_GREEN())
    curses.curs_set(2)

    _, max_x = win.getmaxyx()

    subwin_key = curses.newwin(1, max_x-14, 2, 14)
    box_key = Textbox(subwin_key)
    
    win.refresh()

    box_key.edit(_textbox_validator)
    key_input = box_key.gather().replace('\n','').rstrip()
    
    if key_input == '':
        raise Exception("no text entered in key")
    
    win.addstr(3, 0, "   set value: ", COLOR_GREEN())

    subwin_value = curses.newwin(1, max_x-14, 3, 14)
    box_value = Textbox(subwin_value)

    win.refresh()

    box_value.edit(_textbox_validator)
    value_input = box_value.gather().replace('\n','').rstrip()
    
    if value_input == '':
        raise Exception("no text entered in value")

    self.state.session_rules.update({key_input: value_input})

    curses.curs_set(0)
    
