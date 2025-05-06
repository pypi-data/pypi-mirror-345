import contextlib
import os
from enum import IntEnum
from typing import Optional, Union

from ._internal import worker_queue
from .logging import internal_logger, send_logs_handler
from .native import (
    get_and_swap_aggregations,
    get_hud_running_mode,
    set_hud_running_mode,
)
from .utils import dump_logs_sync

should_check_env_var = True


# HudRunningMode enum is also declared in native.h
# Any changes to HudRunningMode enum should be reflected in native.h as well.
class HudRunningMode(IntEnum):
    DISABLED = 0
    ENABLED = 1
    STANDBY = 2


def set_dont_check_env_var() -> None:
    global should_check_env_var
    should_check_env_var = False


def get_hud_enable() -> Union[str, None]:
    return os.environ.get("HUD_ENABLE", None)


def valid_hud_enable(hud_env_var: str) -> bool:
    return isinstance(hud_env_var, str) and (
        hud_env_var.lower() == "true" or hud_env_var == "1"
    )


def check_hud_enabled_by_env_var() -> bool:
    hud_env_var = get_hud_enable()
    if hud_env_var is None:
        internal_logger.info("HUD_ENABLE is not set")
        return False
    if not valid_hud_enable(hud_env_var):
        internal_logger.info("HUD_ENABLE is not set to 'true' or '1'")
        return False
    return True


def should_run_hud() -> bool:
    if should_check_env_var and not check_hud_enabled_by_env_var():
        return False
    if not get_hud_running_mode() == HudRunningMode.ENABLED:
        internal_logger.info("HUD is not enabled")
        return False
    return True


def disable_hud(
    should_dump_logs: bool,
    should_clear: bool = True,
    session_id: Optional[str] = None,
) -> None:
    internal_logger.info(
        "Disabling HUD"
    )  # It will print to the console if HUD_DEBUG is set
    set_hud_running_mode(HudRunningMode.DISABLED)

    if should_dump_logs:
        with contextlib.suppress(Exception):
            dump_logs_sync(session_id)

    if should_clear:
        clear_hud()


def clear_hud() -> None:
    worker_queue.clear()

    get_and_swap_aggregations().clear()
    # we have two dictionaries swapping
    get_and_swap_aggregations().clear()

    send_logs_handler.get_and_clear_logs()


def enable_hud() -> None:
    set_hud_running_mode(HudRunningMode.ENABLED)
