from __future__ import annotations

import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .window import Window


def shortcut(key: str, target: Window) -> None:
    if sys.platform == "darwin":
        _mac_shortcut(key, target)
    else:
        import pyautogui

        pyautogui.hotkey("ctrl", key)


def _mac_shortcut(key: str, target: Window) -> None:
    import Quartz

    # The app currently uses only Copy, Paste, and Save. These are the same ANSI
    # virtual key codes used by PyAutoGUI's macOS backend.
    key_codes = {"c": 0x08, "v": 0x09, "s": 0x01}
    if key not in key_codes:
        raise ValueError(f"Unsupported macOS shortcut: {key!r}")
    if not Quartz.CGPreflightPostEventAccess():
        raise RuntimeError(
            "Sending shortcuts needs Accessibility permission for the app running proofread"
        )

    source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStatePrivate)
    if source is None:
        raise RuntimeError("Could not create a macOS keyboard event source")
    down = Quartz.CGEventCreateKeyboardEvent(source, key_codes[key], True)
    up = Quartz.CGEventCreateKeyboardEvent(source, key_codes[key], False)
    if down is None or up is None:
        raise RuntimeError("Could not create macOS shortcut events")
    for event in (down, up):
        Quartz.CGEventSetFlags(event, Quartz.kCGEventFlagMaskCommand)

    pid = target.require_active()
    # Address both events to the verified process. Command is part of each
    # event, rather than a separate modifier press that can cross a focus switch.
    try:
        Quartz.CGEventPostToPid(pid, down)
    finally:
        Quartz.CGEventPostToPid(pid, up)
    # Preserve PyAutoGUI's previous post-shortcut pause before reading or
    # restoring the clipboard. Focus confirmation itself has no fixed delay.
    time.sleep(0.1)
