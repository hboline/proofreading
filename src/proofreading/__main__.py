from pathlib import Path
import tomllib

import curses
from platformdirs import user_config_dir

from .controller import App

# config
CONFIG_DIR = Path(user_config_dir(
  appname="proofreading",
  roaming=True,
))
CONFIG_FILE = CONFIG_DIR / "config.toml"

def load_config(CONFIG_FILE: Path) -> dict:
    if not CONFIG_FILE.exists():
        return {}

    with CONFIG_FILE.open('rb') as f:
        return tomllib.load(f)
   
def run(stdscr: curses.window):
    # initialize curses
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.scrollok(False)

    curses.start_color()
    curses.init_pair(1, 245, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    # initialize config
    config = load_config(CONFIG_FILE)

    app = App(stdscr, config)
    app.run()

def main():
    curses.wrapper(run)

if __name__ == "__main__":
    main()
