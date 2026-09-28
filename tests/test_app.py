from types import SimpleNamespace

import pytest

from proofreading.common import FuncContainer, FuncType
from proofreading.controller.app import App


def test_super_action_does_not_access_clipboard():
    app = App.__new__(App)
    app.clipboard = SimpleNamespace(save=lambda: pytest.fail("clipboard was accessed"))
    called = []

    app.process_action(FuncContainer(lambda _: called.append(True), FuncType.Super))

    assert called == [True]
