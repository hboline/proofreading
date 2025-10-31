import curses

from app import App

def main(stdscr: curses.window):
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.scrollok(False)

    curses.start_color()
    curses.init_pair(1, 245, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    app = App(stdscr, clipboard_value="[the]")
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
