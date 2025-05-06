import asyncio
import sys

from ..config import config
from ..logging import internal_logger
from ..utils import dump_logs_sync
from .exporter import Exporter

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    internal_logger.set_component("exporter")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        exporter = Exporter(config.exporter_unique_id, loop, creation_id=sys.argv[1])
        sys.exit(loop.run_until_complete(exporter.run()))
    except Exception:
        try:
            # If the exception is before getting the user options, we can't send the error
            internal_logger.critical("Exporter failed", exc_info=True)
            dump_logs_sync(None)
        except Exception:
            pass
