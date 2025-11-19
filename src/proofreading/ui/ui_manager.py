from __future__ import annotations
from typing import Dict, TYPE_CHECKING

from .base_ui import BaseUI
from .main_ui import MainUI
from .options_ui import OptionsUI
from .interactors import ManualInput, AddSessionRule
from ..utils import UIResult
if TYPE_CHECKING:
    from ..controller import State

ui_map: Dict[str, BaseUI] = {
    "main": MainUI(),
    "options": OptionsUI(),
    "manual_input": ManualInput(),
    "add_session_rule": AddSessionRule(),
}

def activate_ui(ui: str, state: State) -> UIResult:
    return ui_map[ui].run(state)
