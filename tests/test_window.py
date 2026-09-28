from types import SimpleNamespace

import pytest

from proofreading.controller import window


def test_mac_reader_uses_bundle_id_and_can_open_after_startup(monkeypatch):
    running = []
    workspace = SimpleNamespace(runningApplications=lambda: running)
    monkeypatch.setattr(window.sys, "platform", "darwin")
    monkeypatch.setattr(window, "_mac_workspace", lambda: workspace)

    reader = window.Window("adobe")
    assert not reader.is_active()

    activations = []
    running.append(SimpleNamespace(
        bundleIdentifier=lambda: "com.adobe.Acrobat.Pro",
        activateWithOptions_=lambda options: activations.append(options) or True,
        isActive=lambda: True,
    ))
    reader.activate()

    assert reader.is_active()
    assert len(activations) == 1


def test_captures_active_mac_app(monkeypatch):
    active = SimpleNamespace(isActive=lambda: True)
    workspace = SimpleNamespace(frontmostApplication=lambda: active)
    monkeypatch.setattr(window.sys, "platform", "darwin")
    monkeypatch.setattr(window, "_mac_workspace", lambda: workspace)

    target = window.Window()
    assert target.is_active()


def test_missing_mac_reader_reports_error_when_action_needs_it(monkeypatch):
    workspace = SimpleNamespace(runningApplications=lambda: [])
    monkeypatch.setattr(window.sys, "platform", "darwin")
    monkeypatch.setattr(window, "_mac_workspace", lambda: workspace)

    reader = window.Window("adobe")
    with pytest.raises(RuntimeError, match="Could not find adobe"):
        reader.activate()


def test_activation_failure_stops_action(monkeypatch):
    target_window = SimpleNamespace(activate=lambda **kwargs: False)
    monkeypatch.setattr(window.sys, "platform", "win32")
    monkeypatch.setattr(
        window,
        "_desktop_windows",
        lambda: SimpleNamespace(getActiveWindow=lambda: target_window),
    )

    with pytest.raises(RuntimeError, match="Could not activate the previously active window"):
        window.Window().activate()
