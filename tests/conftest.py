import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from proofreading.controller import window


@pytest.fixture
def focus_api(monkeypatch):
    values = {
        (("app", 42), "frontmost"): True,
        (("app", 42), "focused_window"): "pdf-window",
    }
    ax = SimpleNamespace(
        AXIsProcessTrusted=lambda: True,
        AXUIElementCreateApplication=lambda pid: ("app", pid),
        AXUIElementSetMessagingTimeout=Mock(return_value=0),
        AXUIElementCopyAttributeValue=lambda element, attribute, _: (
            (0, values[element, attribute]) if (element, attribute) in values else (1, None)
        ),
        AXUIElementSetAttributeValue=Mock(return_value=0),
        AXUIElementPerformAction=Mock(return_value=0),
        kAXFrontmostAttribute="frontmost",
        kAXFocusedWindowAttribute="focused_window",
        kAXMainWindowAttribute="main_window",
        kAXMinimizedAttribute="minimized",
        kAXRaiseAction="raise",
        kAXErrorSuccess=0,
        kAXErrorNoValue=1,
        kAXErrorCannotComplete=2,
        kAXErrorInvalidUIElement=3,
        kAXErrorAttributeUnsupported=4,
    )
    monkeypatch.setitem(sys.modules, "ApplicationServices", ax)
    monkeypatch.setitem(sys.modules, "CoreFoundation", SimpleNamespace(CFEqual=lambda a, b: a == b))
    path = Path(window.__file__).with_name("macos_focus.py")
    spec = importlib.util.spec_from_file_location("focus_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(sys.modules, "proofreading.controller.macos_focus", module)
    return module, ax, values


