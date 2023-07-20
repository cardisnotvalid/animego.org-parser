import asyncio
import logging

import rich.traceback
from rich.console import Console
from rich.logging import RichHandler

from scraper import Scraper


def setup_logging(console: Console, debug: bool = False) -> None:
    rich.traceback.install(console=console)
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(message)s",
        datefmt="%H:%M:%S",
        handlers=(
            RichHandler(
                console=console,
                omit_repeated_times=False,
                show_path=False,
                rich_tracebacks=True
            ),
        ),
    )
    logging.getLogger("httpx").setLevel(logging.ERROR)
    

async def main() -> None:
    console = Console()
    setup_logging(console)
    
    scraper = Scraper(console)
    await scraper.run()
    
    
if __name__ == "__main__":
    asyncio.run(main())