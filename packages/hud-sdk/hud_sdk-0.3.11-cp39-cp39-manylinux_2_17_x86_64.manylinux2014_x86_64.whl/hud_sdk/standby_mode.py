import threading
import time
from typing import Callable, Optional, Union

from .config import config
from .logging import internal_logger, user_logger
from .native import get_hud_running_mode, set_hud_running_mode
from .run_mode import HudRunningMode
from .user_options import UserOptions
from .users_logs import UsersLogs
from .worker import worker

first_active_session_id: Optional[str] = None


def is_first_active_session_id_set() -> bool:
    return first_active_session_id is not None


def set_first_active_session_id(session_id: Union[str, None]) -> None:
    global first_active_session_id
    first_active_session_id = session_id


def validate_standby_arguments(
    standby_callback: Union[Callable[[], bool], None],
    standby_check_interval: Union[float, None],
) -> bool:
    if bool(standby_callback) != bool(standby_check_interval):
        user_logger.log(*UsersLogs.HUD_STANDBY_ARGS_INVALID)
        return False

    return True


def enforce_minimum_standby_interval(standby_check_interval: float) -> float:
    if standby_check_interval < config.standby_check_minimum_interval:
        user_logger.log(*UsersLogs.HUD_STANDBY_MINIMUM_INTERVAL)
        return config.standby_check_minimum_interval

    return standby_check_interval


def init_standby_thread(
    standby_callback: Callable[[], bool],
    standby_check_interval: float,
    user_options: UserOptions,
) -> Union[None, threading.Thread]:
    should_continue_worker = execute_standby_callback_safely(standby_callback)
    if should_continue_worker is None:
        user_logger.log(*UsersLogs.HUD_STANDBY_CALLBACK_UNEXPECTED_BEHAVIOR)
        return None

    standby_check_interval = enforce_minimum_standby_interval(standby_check_interval)

    if not should_continue_worker:
        enter_standby_mode()

    internal_logger.info(
        "Starting standby thread",
        data={"standby_check_interval": standby_check_interval},
    )
    standby_thread = threading.Thread(
        target=standby_task,
        args=(user_options, standby_callback, standby_check_interval),
        daemon=True,
    )
    standby_thread.start()
    return standby_thread


def execute_standby_callback_safely(
    standby_callback: Callable[[], bool],
) -> Union[bool, None]:
    try:
        should_continue_worker = standby_callback()
    except Exception:
        user_logger.log(*UsersLogs.HUD_STANDBY_CALLBACK_EXCEPTION_INFO, exc_info=True)
        internal_logger.warning("Standby callback failed", exc_info=True)
        return None

    if type(should_continue_worker) is not bool:
        internal_logger.warning(
            "Standby callback did not return a boolean",
            data={"return_type": type(should_continue_worker)},
        )
        return None

    return should_continue_worker


def enter_standby_mode() -> None:
    internal_logger.info("Entering standby mode")
    user_logger.log(*UsersLogs.HUD_STANDBY_MODE)
    set_hud_running_mode(HudRunningMode.STANDBY)

    if not is_first_active_session_id_set():
        internal_logger.info("No first active session prior to standby mode")


def activate_worker(user_options: UserOptions) -> None:
    if not get_hud_running_mode() == HudRunningMode.STANDBY:
        internal_logger.warning(
            "HUD is not in standby mode, skipping activation",
            data={"current_mode": get_hud_running_mode()},
        )
        return

    internal_logger.info(
        "Activating HUD with new session",
        data={"first_active_session_id": first_active_session_id},
    )
    set_hud_running_mode(HudRunningMode.ENABLED)
    worker.start_worker_thread(user_options)


def standby_task(
    user_options: UserOptions,
    standby_callback: Callable[[], bool],
    standby_check_interval: float,
) -> None:
    while True:
        time.sleep(standby_check_interval)

        current_running_mode = get_hud_running_mode()

        if should_terminate_standby_task():
            internal_logger.info(
                "HUD is disabled or main thread has exited, exiting standby task"
            )
            return

        should_continue_worker = execute_standby_callback_safely(standby_callback)

        if should_continue_worker is None:
            return
        elif should_continue_worker and current_running_mode == HudRunningMode.STANDBY:
            activate_worker(user_options)
        elif (
            not should_continue_worker
            and current_running_mode == HudRunningMode.ENABLED
        ):
            enter_standby_mode()


def should_terminate_standby_task() -> bool:
    return bool(
        get_hud_running_mode() == HudRunningMode.DISABLED or main_thread_exited()
    )


def main_thread_exited() -> bool:
    main_thread = threading.main_thread()
    return not main_thread.is_alive()
