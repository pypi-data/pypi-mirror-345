from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import Callable, Dict, Any

from GooeyEx.gui import seeder
from GooeyEx.gui import state as s
from GooeyEx.gui.state import FullGooeyState
from GooeyEx.python_bindings.types import Try, PublicGooeyState


def communicateFormValidation(
    state: FullGooeyState, callback: Callable[[Try[Dict[str, str]]], None]
) -> None:
    communicateAsync(s.buildFormValidationCmd(state), state, callback)


def communicateSuccessState(
    state: FullGooeyState, callback: Callable[[Try[PublicGooeyState]], None]
) -> None:
    communicateAsync(s.buildOnSuccessCmd(state), state, callback)


def communicateErrorState(
    state: FullGooeyState, callback: Callable[[Try[PublicGooeyState]], None]
) -> None:
    communicateAsync(s.buildOnErrorCmd(state), state, callback)


def fetchFieldValidation():
    pass


def fetchFieldAction():
    pass


def fetchFormAction():
    pass


def communicateAsync(cmd: str, state: FullGooeyState, callback: Callable[[Any], None]):
    """
    Callable MUST be wrapped in wx.CallAfter if its going to
    modify the UI.
    """

    def work():
        result = seeder.communicate(cmd, state["encoding"])
        callback(result)

    thread = Thread(target=work)
    thread.start()
