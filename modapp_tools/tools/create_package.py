from os import makedirs
from pathlib import Path
from shutil import copy

from command_runner import command_runner

# from loguru import logger


def create_package(name: str, parent_dir: Path) -> None:
    pkg_root_dir = parent_dir / name
    makedirs(pkg_root_dir)

    command_runner(f"poetry init --name={name} --no-interaction", cwd=pkg_root_dir)

    # poetry doesn't create root src dir, but it can be changed in the next versions
    pkg_root_src = pkg_root_dir / name
    pkg_root_src.mkdir()

    pkg_root_src_init = pkg_root_src / "__init__.py"
    pkg_root_src_init.touch()

    readme_path = pkg_root_dir / "README.md"
    readme_path.touch()

    tests_dir = pkg_root_dir / "tests"
    tests_dir.mkdir()

    tests_init = tests_dir / "__init__.py"
    tests_init.touch()

    assets_dir = Path(__file__).parent / "assets"
    for pkg_file in assets_dir.rglob("*"):
        copy(pkg_file, pkg_root_dir)
