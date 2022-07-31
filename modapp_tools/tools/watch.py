import asyncio
from pathlib import Path

from loguru import logger
from watchfiles import awatch, DefaultFilter

import modapp_tools.env as env
from .regenerate_protos import regenerate_all, regenerate_proto
from ._watch_server import watch_server


async def prestart():
    logger.info("Regenerate all")
    # cache file hashes and compare instead?
    regenerate_all()
    for proto_file in env.PROTOS_PATH.rglob("*.proto"):
        regenerate_proto(proto_file)


async def watch_protos():
    logger.info(f"Start watching: {str(env.PROTOS_PATH)}")
    async for changes in awatch(env.PROTOS_PATH, watch_filter=DefaultFilter()):
        logger.info("Changed: " + ", ".join(map(lambda change: change[1], changes)))
        logger.info("Regenerating protos libs")
        regenerate_all()
        for change in changes:
            regenerate_proto(Path(change[1]))
        logger.info("3/3 Regenerated services")


def watch():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(prestart())

    try:
        asyncio.ensure_future(watch_protos())
        asyncio.ensure_future(watch_server(env.SERVER_PATH))
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Stop watching")


if __name__ == "__main__":
    watch()
