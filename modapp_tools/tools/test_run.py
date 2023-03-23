from pathlib import Path
from typing import Optional

from command_runner import command_runner


def test_run_command(
    cmd: str,
    timeout: int = 10,
    cwd: Optional[Path] = None,
    print_on_failure: Optional[str] = None,
    print_on_success: Optional[str] = None,
) -> None:
    exit_code, output = command_runner(
        cmd,
        timeout=timeout,
        cwd=cwd,
    )

    if exit_code == -254:
        # command hasn't stopped after `timeout`, assume it was a successful start
        if print_on_success is not None:
            print(print_on_success)
    elif exit_code != 0:
        if print_on_failure is not None:
            print(print_on_failure)
        raise Exception("Process failed to start: " + str(output))
