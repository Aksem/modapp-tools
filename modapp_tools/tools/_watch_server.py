import os
from pathlib import Path

import isort
from command_runner import command_runner
from loguru import logger
from watchfiles import awatch, PythonFilter
from watchfiles.run import start_process

import modapp_tools.env as env


async def watch_server(path: Path):
    logger.info(f"Start watching: {str(path)}")
    process = None
    os.chdir(path)
    server_app_name = path.name

    try:
        while True:
            logger.trace("Start application")
            process = start_process(
                target=f"poetry run python {server_app_name}/main.py",
                target_type="command",
                args=(),
                kwargs={},
            )
            changes = []
            async for changed_files in awatch(path, watch_filter=PythonFilter()):
                changes = changed_files
                break

            if process.is_alive():
                # if server start fails, process is already dead
                process.stop()

            filepaths = [file_change[1] for file_change in changes]
            filepaths_str = "\n".join(filepaths)
            logger.trace("Changed files:" + "\n" + filepaths_str)

            logger.trace("Sorting imports in changed files")
            for filepath in filepaths:
                isort.file(filepath)

            logger.trace("Format changed files")
            exit_code, output = command_runner(
                f'poetry run black {" ".join(filepaths)}', shell=True
            )
            logger.trace(f"Result: {exit_code}, {output}")

            logger.trace("Check types in whole project after changes")
            exit_code, output = command_runner(
                f"poetry run mypy --strict {(env.SERVER_PATH).as_posix()}",
                shell=True,
            )
            logger.trace(f"Result: {exit_code}, {output}")
    except KeyboardInterrupt:
        if process is not None:
            process.stop()
        logger.info("stopped")
