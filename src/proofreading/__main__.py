from pathlib import Path
import tomllib

import curses
from platformdirs import user_config_dir

from .controller import App
from .ui.utils import init_colors, set_cursor

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
    set_cursor(0)
    stdscr.keypad(True)
    stdscr.scrollok(False)

    init_colors()

    # initialize config
    config = load_config(CONFIG_FILE)

    app = App(stdscr, config)
    app.run()

def main():
    curses.wrapper(run)

if __name__ == "__main__":
    main()
