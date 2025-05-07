from . import set_hook
from .run_mode import set_dont_check_env_var
from .worker.worker import init_hud_thread as init

set_dont_check_env_var()
set_hook()

__all__ = ["init"]
