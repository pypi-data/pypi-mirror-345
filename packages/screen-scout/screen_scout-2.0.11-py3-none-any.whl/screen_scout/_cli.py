import asyncio
import sys
from .main_async import main as _async_main


def entry_point() -> None:
    """
    Synchronous shim used by console_scripts.
    Mirrors `python -m screen_scout` behaviour.
    """

    asyncio.run(_async_main(sys.argv[1:])
