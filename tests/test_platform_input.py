"""Focus and keyboard regression tests; never post input to the desktop."""

import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from proofreading.controller import shortcuts, window


@pytest.fixture
def quartz_api(monkeypatch):
    api = SimpleNamespace(
        CGPreflightPostEventAccess=lambda: True,
        kCGEventSourceStatePrivate=-1,
        kCGEventFlagMaskCommand=1 << 20,
        CGEventSourceCreate=lambda _: object(),
        CGEventCreateKeyboardEvent=lambda source, key, down: SimpleNamespace(key=key, down=down),
        CGEventSetFlags=lambda event, flags: setattr(event, "flags", flags),
        CGEventPostToPid=Mock(),
    )
    monkeypatch.setitem(sys.modules, "Quartz", api)
    monkeypatch.setattr(shortcuts, "time", SimpleNamespace(sleep=Mock()))
    return api


def test_focus_requires_both_application_and_window(focus_api):
    module, _, values = focus_api
    focus = module.MacFocus(42)
    assert focus.is_active()
    values[("app", 42), "frontmost"] = False
    assert not focus.is_active()
    values[("app", 42), "frontmost"] = True
    values[("app", 42), "focused_window"] = "dialog"
    assert not focus.is_active()


def test_window_can_appear_during_activation(focus_api):
    module, _, values = focus_api
    del values[("app", 42), "focused_window"]
    focus = module.MacFocus(42)
    assert not focus.is_active()
    values[("app", 42), "focused_window"] = "new-window"
    assert focus.is_active()
    assert focus.window == "new-window"


def test_wait_returns_immediately_when_active(focus_api, monkeypatch):
    module, _, _ = focus_api
    clock = SimpleNamespace(monotonic=lambda: 0, sleep=Mock())
    monkeypatch.setattr(module, "time", clock)
    assert module.MacFocus(42).wait_until_active()
    clock.sleep.assert_not_called()


@pytest.mark.parametrize("activates", [True, False])
def test_wait_stops_on_activation_or_deadline(focus_api, monkeypatch, activates):
    module, _, values = focus_api
    values[("app", 42), "frontmost"] = False
    elapsed = [0.0]
    sleeps = []

    def sleep(duration):
        sleeps.append(duration)
        elapsed[0] += duration
        if activates:
            values[("app", 42), "frontmost"] = True

    monkeypatch.setattr(module, "time", SimpleNamespace(monotonic=lambda: elapsed[0], sleep=sleep))
    assert module.MacFocus(42).wait_until_active(timeout=0.05) is activates
    assert elapsed[0] == pytest.approx(0.02 if activates else 0.05)
    assert all(duration <= 0.02 for duration in sleeps)


def test_permission_failure_is_actionable(focus_api, monkeypatch):
    module, ax, _ = focus_api
    monkeypatch.setattr(ax, "AXIsProcessTrusted", lambda: False)
    with pytest.raises(RuntimeError, match="Accessibility permission"):
        module.MacFocus(42)


def test_activation_uses_observed_focus_even_if_request_returns_false(focus_api, monkeypatch):
    _, ax, values = focus_api
    values[("app", 42), "frontmost"] = False

    def activate(_):
        values[("app", 42), "frontmost"] = True
        return False

    handle = SimpleNamespace(processIdentifier=lambda: 42, activateWithOptions_=Mock(side_effect=activate))
    monkeypatch.setattr(window, "sys", SimpleNamespace(platform="darwin"))
    monkeypatch.setattr(window.Window, "_find_window", staticmethod(lambda _: handle))
    monkeypatch.setitem(sys.modules, "AppKit", SimpleNamespace(NSApplicationActivateIgnoringOtherApps=2))
    target = window.Window("adobe")
    target.activate()
    assert target.require_active() == 42
    ax.AXUIElementPerformAction.assert_called_once_with("pdf-window", "raise")


def test_activation_timeout_never_marks_target_confirmed(focus_api, monkeypatch):
    module, _, values = focus_api
    values[("app", 42), "frontmost"] = False
    handle = SimpleNamespace(processIdentifier=lambda: 42, activateWithOptions_=lambda _: True)
    monkeypatch.setattr(window, "sys", SimpleNamespace(platform="darwin"))
    monkeypatch.setattr(window.Window, "_find_window", staticmethod(lambda _: handle))
    monkeypatch.setitem(sys.modules, "AppKit", SimpleNamespace(NSApplicationActivateIgnoringOtherApps=2))
    monkeypatch.setattr(module.MacFocus, "wait_until_active", lambda self: False)
    target = window.Window("adobe")
    with pytest.raises(RuntimeError, match="Could not confirm focus"):
        target.activate()
    with pytest.raises(RuntimeError, match="no shortcut was sent"):
        target.require_active()


@pytest.mark.parametrize("key,code", [("c", 8), ("v", 9), ("s", 1)])
def test_shortcut_includes_command_and_targets_verified_pid(quartz_api, key, code):
    target = SimpleNamespace(require_active=Mock(return_value=42))
    shortcuts._mac_shortcut(key, target)
    calls = quartz_api.CGEventPostToPid.call_args_list
    assert len(calls) == 2
    assert [(call.args[0], call.args[1].key, call.args[1].down) for call in calls] == [
        (42, code, True), (42, code, False)
    ]
    assert all(call.args[1].flags == quartz_api.kCGEventFlagMaskCommand for call in calls)
    target.require_active.assert_called_once()


def test_focus_change_blocks_all_keyboard_events(focus_api, quartz_api, monkeypatch):
    module, _, values = focus_api
    target = window.Window("adobe")
    target._mac_focus = module.MacFocus(42)
    values[("app", 42), "focused_window"] = "different-pdf"
    with pytest.raises(RuntimeError, match="no shortcut was sent"):
        shortcuts._mac_shortcut("v", target)
    quartz_api.CGEventPostToPid.assert_not_called()


def test_key_up_is_attempted_if_posting_fails(quartz_api):
    quartz_api.CGEventPostToPid.side_effect = [RuntimeError("post failed"), None]
    with pytest.raises(RuntimeError, match="post failed"):
        shortcuts._mac_shortcut("s", SimpleNamespace(require_active=lambda: 42))
    assert quartz_api.CGEventPostToPid.call_args_list[-1].args[1].down is False


def test_input_permission_failure_posts_nothing(quartz_api, monkeypatch):
    monkeypatch.setattr(quartz_api, "CGPreflightPostEventAccess", lambda: False)
    with pytest.raises(RuntimeError, match="Accessibility permission"):
        shortcuts._mac_shortcut("s", SimpleNamespace(require_active=lambda: 42))
    quartz_api.CGEventPostToPid.assert_not_called()


@pytest.mark.parametrize("platform", ["win32", "linux"])
def test_non_mac_shortcuts_keep_using_control(monkeypatch, platform):
    hotkey = Mock()
    monkeypatch.setattr(shortcuts, "sys", SimpleNamespace(platform=platform))
    monkeypatch.setitem(sys.modules, "pyautogui", SimpleNamespace(hotkey=hotkey))
    shortcuts.shortcut("s", SimpleNamespace())
    hotkey.assert_called_once_with("ctrl", "s")


@pytest.mark.skipif(sys.platform != "darwin", reason="Inspect real Quartz events on macOS")
def test_real_quartz_event_flags_without_posting(monkeypatch):
    import Quartz

    events = []
    monkeypatch.setattr(Quartz, "CGPreflightPostEventAccess", lambda: True)
    monkeypatch.setattr(Quartz, "CGEventPostToPid", lambda pid, event: events.append((pid, event)))
    monkeypatch.setattr(shortcuts, "time", SimpleNamespace(sleep=lambda _: None))
    shortcuts._mac_shortcut("s", SimpleNamespace(require_active=lambda: 42))
    assert [Quartz.CGEventGetType(event) for _, event in events] == [Quartz.kCGEventKeyDown, Quartz.kCGEventKeyUp]
    assert all(pid == 42 for pid, _ in events)
    assert all(Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode) == 1 for _, event in events)
    assert all(Quartz.CGEventGetFlags(event) & Quartz.kCGEventFlagMaskCommand for _, event in events)
