from pygetwindow import getWindowsWithTitle, getActiveWindow
from pygetwindow._pygetwindow_win import Win32Window

def getActiveWindowNotNone() -> Win32Window:
    try:
        handle = getActiveWindow()
        assert handle is not None
    except AssertionError:
        raise Exception("getActiveWindow: error fetching active window handle")
    else:
        return handle

class Window():
    _handle: Win32Window
    
    def __init__(self, partial_name: str | None = None):
        if partial_name is None:
            self._handle = getActiveWindowNotNone()
        elif partial_name is not None:
            try:
                self._handle = getWindowsWithTitle(partial_name)[0]
            except IndexError:
                raise Exception(f"Window: error finding window with {partial_name} in title")

    # maybe this needs an await or something? idk
    def activate(self):
        self._handle.activate()
        # assert self.is_active()

    def is_active(self):
        return self._handle.isActive

    def set_window(self):
        self._handle = getActiveWindowNotNone()
        
