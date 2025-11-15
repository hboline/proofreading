## TODO
* add a chaining option (i.e. press space to chain, type e.g. "13r", press space to send)
* implement logging
* allow UI to send keypress to app that are held until some state is reached in the app (*what did I mean by this*)
* add a microsoft word mode (ugh)
* add a UI for searching Merriam-Webster (incorporate API?)
* incorporate a dictionary to do pluralization, conjugation, etc.
* add cross-platform support
* add an ability to cut and paste while preserving the clipboard
* text still sometimes doesn't process correctly (pasting without brackets  and odd formatting)
  * app is still performing user input, but for some reason the clipboard doesn't seem to be getting manipulated correctly. implementing logging may help diagnose the issue.
  * consider performing window actions in a separate thread
* make and write LICENSE.md (creative-commons)
* ~~handle actions like `"filesave"` or `"toggle history output"` in `process_action` by defining functions that act on `self: App`~~
* ~~get rid of `SpecialFunc` type; add a `FuncType.Special` enum type for use by `FuncContainer` class~~
* ~~fix ingest of accented latin characters (e.g. é gets turned into \`e)~~ partially complete, list of latin letters in `LIG_DICT` incomplete
* ~~add string aliases to actions for better history readout~~
* ~~change error readout to it's own `_curses_add_lines` call instead of appending it to the options~~
* ~~curses crashes when terminal window is too small: `_curses.error: addwstr() returned ERR`~~
* ~~clipboard is not resetting properly~~
