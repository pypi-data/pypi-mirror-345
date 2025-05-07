import os
import sys

from hud_sdk.worker.worker import init_hud_thread as init


def run_previous_sitecustomize() -> None:
    auto_init_dir = os.path.dirname(__file__)
    if auto_init_dir not in sys.path:
        try:
            import sitecustomize  # type: ignore[import-not-found] # noqa: F401
        except ImportError:
            pass
        return

    index = sys.path.index(auto_init_dir)
    del sys.path[index]

    our_sitecustomize = sys.modules["sitecustomize"]
    del sys.modules["sitecustomize"]

    try:
        import sitecustomize  # noqa: F401
    except ImportError:
        sys.modules["sitecustomize"] = our_sitecustomize
    finally:
        sys.path.insert(index, auto_init_dir)


init()
run_previous_sitecustomize()
