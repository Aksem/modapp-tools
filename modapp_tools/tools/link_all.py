import os
import shutil
from pathlib import Path
from typing import Dict, Set

import pytomlpp
from command_runner import command_runner
from loguru import logger

import modapp_tools.env as env


def resolve_dependencies(lib, libs_to_expand, local_libs_deps) -> Set[str]:
    result = set()
    for lib_to_expand in libs_to_expand:
        if lib_to_expand not in local_libs_deps[str(lib)]:
            result.add(lib_to_expand)
            result |= resolve_dependencies(
                lib, local_libs_deps[lib_to_expand], local_libs_deps
            )
    return result


def lib_is_in_dependencies(lib: str, deps: Set[str]) -> bool:
    # TODO: investigate why dependencies are sometimes with dashes and sometime with underscores
    return lib.replace("-", "_") in deps or lib.replace("_", "-") in deps or lib in deps


def link_all():
    # find all libs in workspace
    local_libs = [
        file
        for file in env.WORKSPACE_PATH.glob("*")
        if file.is_dir()
        and file.name != "scripts"
        and file.name != env.PROTOS_PATH.name
        and (file / "pyproject.toml").exists()
    ]
    local_libs_deps: Dict[str, Set[str]] = {}

    for local_lib in local_libs:
        pyproject_path = local_lib / "pyproject.toml"
        if not pyproject_path.exists():
            continue

        pyproject_def = pytomlpp.load(pyproject_path, "r")
        try:
            dependencies = pyproject_def["tool"]["poetry"]["dependencies"]
        except KeyError:
            dependencies = {}

        try:
            # TODO: check also new way with dependencies groups?
            dev_dependencies = pyproject_def["tool"]["poetry"]["dev-dependencies"]
        except KeyError:
            dev_dependencies = {}

        local_libs_deps[str(local_lib)] = set(
            [
                str(lib)
                for lib in local_libs
                if lib_is_in_dependencies(str(lib), dependencies)
                or lib_is_in_dependencies(str(lib), dev_dependencies)
            ]
        )

    for local_lib in local_libs:
        # resolve first level manually and all next levels recursively
        local_lib_deps = local_libs_deps[str(local_lib)]
        resolved_deps = local_lib_deps.copy()
        for local_lib_dep in local_lib_deps:
            resolved_deps |= local_libs_deps[str(local_lib_dep)]
        resolved_deps |= resolve_dependencies(
            local_lib, local_lib_deps, local_libs_deps
        )
        # lib itself is not needed in dependencies, if it is included
        if str(local_lib) in resolved_deps:
            resolved_deps.remove(str(local_lib))

        local_libs_deps[str(local_lib)] = resolved_deps.copy()

    # prepare env without current virtual env to avoid executing poetry with current venv
    environ = os.environ.copy()
    del environ["VIRTUAL_ENV"]

    for local_lib in local_libs:
        local_lib_deps = local_libs_deps[str(local_lib)]
        logger.trace(f"{local_lib} has local deps: {local_lib_deps}")
        # setuptools is package preinstalled by poetry, so it's available in all venvs
        exit_code, venv_package_path = command_runner(
            f'poetry run python -c "import setuptools; import os;'
            f' print(os.path.dirname(setuptools.__file__))"',
            shell=True,
            cwd=local_lib,
            env=environ,
        )
        if exit_code != 0:
            logger.error("Failed to get venv path")
            continue

        venv_path = Path(venv_package_path).parent
        logger.trace(f"venv path of {local_lib}: {venv_path}")

        for used_lib in local_lib_deps:
            used_lib_venv_path = venv_path / used_lib
            if used_lib_venv_path.exists():
                if not used_lib_venv_path.is_symlink():
                    # print(used_lib_venv_path)
                    shutil.rmtree(used_lib_venv_path)
                else:
                    used_lib_venv_path.unlink()
            else:
                logger.warning(
                    f"{used_lib} is dependency of {local_lib}, but was not in venv"
                )

            used_lib_resolved_path = (
                env.WORKSPACE_PATH / used_lib / used_lib
            ).resolve()
            used_lib_venv_path.symlink_to(
                used_lib_resolved_path, target_is_directory=True
            )


if __name__ == "__main__":
    link_all()
