import os
from pathlib import Path

import pytomlpp
import typer
from loguru import logger

import modapp_tools.env as env
from modapp_tools.code_generators.web_service import parse_and_generate_web_service
from modapp_tools.tools.create_package import create_package as _create_package
from modapp_tools.tools.link_all import link_all as _link_all
from modapp_tools.tools.regenerate_protos import regenerate_all as _regenerate_all
from modapp_tools.tools.watch import watch as _watch


app = typer.Typer()


def init_env() -> None:
    call_path = Path(os.getcwd())
    all_paths_to_root = [call_path] + list(call_path.parents)
    config_found = False
    for path in all_paths_to_root:
        config_path = path / "modapp_workspace.toml"
        if config_path.exists():
            env.WORKSPACE_PATH = path
            config_found = True

    if config_found:
        modapp_def = pytomlpp.load(env.WORKSPACE_PATH / "modapp_workspace.toml", "r")
        try:
            paths = modapp_def["tool"]["modapp"]
        except KeyError:
            raise Exception("Modapp workspace config is incomplete")

        env.PROTOS_PATH = env.WORKSPACE_PATH / paths.get("protos_path", "")
        env.SERVER_PATH = env.WORKSPACE_PATH / paths.get("server_path", "")
        env.SERVER_GENERATED_PROTOS_PATH = env.WORKSPACE_PATH / paths.get(
            "server_generated_protos_path", ""
        )
        env.CLIENT_PATH = env.WORKSPACE_PATH / paths.get("client_path", "")
        env.CLIENT_SERVICES_PATH = env.WORKSPACE_PATH / paths.get(
            "client_services_path", ""
        )
    else:
        raise Exception("Modapp workspace('modapp_workspace.toml') not found")


init_env()


@app.command()
def generate_from_proto(kind: str, source_file: Path, output_dir: Path) -> None:
    if kind == "webservice":
        parse_and_generate_web_service(source_file, output_dir)
    else:
        logger.error(f"Unknown kind: '{kind}'")


@app.command()
def create_package(name: str, parent_dir: Path):
    _create_package(name, parent_dir)


@app.command()
def link_all():
    _link_all()


@app.command()
def regenerate_all():
    _regenerate_all()


@app.command()
def watch():
    _watch()


if __name__ == "__main__":
    app()
