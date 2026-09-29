import sys
import time


def _desktop_windows():
    import pywinctl

    return pywinctl


def _mac_workspace():
    from AppKit import NSWorkspace

    return NSWorkspace.sharedWorkspace()


def _mac_app_matches(app, name: str) -> bool:
    bundle_id = (app.bundleIdentifier() or "").casefold()
    name = name.casefold()

    if name == "adobe":
        return (
            bundle_id in {"com.adobe.acrobat.pro", "com.adobe.reader"}
            or bundle_id.startswith("com.adobe.acrobat.")
        )
    if name == "word":
        return bundle_id == "com.microsoft.word"
    return name in (app.localizedName() or "").casefold()


class Window:
    """Find and activate a desktop app without relying on document titles on macOS."""

    def __init__(self, partial_name: str | None = None):
        self._partial_name = partial_name
        # Capture the terminal now; named apps can be found when an action needs them.
        self._handle = self._find_window(None) if partial_name is None else None

    @staticmethod
    def _find_window(partial_name: str | None):
        if sys.platform == "darwin":
            workspace = _mac_workspace()
            if partial_name is None:
                return workspace.frontmostApplication()
            return next(
                (
                    app for app in workspace.runningApplications()
                    if _mac_app_matches(app, partial_name)
                ),
                None,
            )

        pwc = _desktop_windows()
        if partial_name is None:
            return pwc.getActiveWindow()

        windows = pwc.getWindowsWithTitle(
            partial_name,
            condition=pwc.Re.CONTAINS,
            flags=pwc.Re.IGNORECASE,
        )
        if windows:
            return windows[0]

        app_names = pwc.getAppsWithName(
            partial_name,
            condition=pwc.Re.CONTAINS,
            flags=pwc.Re.IGNORECASE,
        )
        return next(
            (
                window for window in pwc.getAllWindows()
                if window.getAppName() in app_names
            ),
            None,
        )

    def activate(self) -> None:
        if self._partial_name is not None:
            self._handle = self._find_window(self._partial_name)

        if self._handle is None:
            target = self._partial_name or "the previously active window"
            raise RuntimeError(f"Could not find {target}; open the app before using this action")

        if sys.platform == "darwin":
            from AppKit import NSApplicationActivateIgnoringOtherApps

            activated = self._handle.activateWithOptions_(
                NSApplicationActivateIgnoringOtherApps
            )
        else:
            activated = self._handle.activate(wait=True)
            if sys.platform == "win32" and not activated:
                # PyWinCtl's Windows activate(wait=True) checks focus immediately.
                # Give Windows a moment to complete the foreground switch.
                for _ in range(10):
                    if self._handle.isActive:
                        activated = True
                        break
                    time.sleep(0.05)

        if not activated:
            target = self._partial_name or "the previously active window"
            raise RuntimeError(f"Could not activate {target}")

    def is_active(self) -> bool:
        if self._partial_name is not None:
            self._handle = self._find_window(self._partial_name)
        if self._handle is None:
            return False
        if sys.platform == "darwin":
            return bool(self._handle.isActive())
        return bool(self._handle.isActive)
