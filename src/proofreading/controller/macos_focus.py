"""On-demand focus checks using live macOS Accessibility queries."""

import time

import ApplicationServices as ax
from CoreFoundation import CFEqual


POLL_INTERVAL = 0.02
FOCUS_TIMEOUT = 2.0
AX_TIMEOUT = 0.05


class MacFocus:
    """Remember the target app's current window for one proofreading action."""

    def __init__(self, pid: int):
        if not ax.AXIsProcessTrusted():
            raise RuntimeError(
                "Focus checks need Accessibility permission. Allow the app running "
                "proofread (usually your terminal) in System Settings > Privacy & "
                "Security > Accessibility, then restart proofread."
            )
        self.pid = pid
        self.application = ax.AXUIElementCreateApplication(pid)
        # Bound IPC too: an unresponsive app must not stall the curses interface.
        ax.AXUIElementSetMessagingTimeout(self.application, AX_TIMEOUT)
        self.window = self._read(self.application, ax.kAXFocusedWindowAttribute)
        if self.window is None:
            self.window = self._read(self.application, ax.kAXMainWindowAttribute)

    @staticmethod
    def _read(element, attribute):
        error, value = ax.AXUIElementCopyAttributeValue(element, attribute, None)
        if error == ax.kAXErrorSuccess:
            return value
        if error in {
            ax.kAXErrorNoValue,
            ax.kAXErrorCannotComplete,
            ax.kAXErrorInvalidUIElement,
            ax.kAXErrorAttributeUnsupported,
        }:
            # Focus/window data can be unavailable during a transition.
            return None
        raise RuntimeError(f"Could not check macOS focus (Accessibility error {error})")

    def raise_window(self) -> None:
        if self.window is None:
            return
        ax.AXUIElementSetMessagingTimeout(self.window, AX_TIMEOUT)
        if self._read(self.window, ax.kAXMinimizedAttribute):
            ax.AXUIElementSetAttributeValue(self.window, ax.kAXMinimizedAttribute, False)
        # These requests can fail during activation. The focus check below, not
        # the request's return value, determines whether activation succeeded.
        ax.AXUIElementPerformAction(self.window, ax.kAXRaiseAction)

    def is_active(self) -> bool:
        # Query the target process directly: unlike NSRunningApplication.active,
        # this does not depend on our Cocoa run loop refreshing a cached value.
        # The system-wide AXFocusedApplication query fails on some desktops.
        if not self._read(self.application, ax.kAXFrontmostAttribute):
            return False
        window = self._read(self.application, ax.kAXFocusedWindowAttribute)
        if window is None:
            return False
        if self.window is None:
            # Some apps expose their window only once activation completes.
            self.window = window
        return bool(CFEqual(self.window, window))

    def wait_until_active(self, timeout: float = FOCUS_TIMEOUT) -> bool:
        deadline = time.monotonic() + timeout
        while True:
            if self.is_active():
                return True
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            time.sleep(min(POLL_INTERVAL, remaining))
