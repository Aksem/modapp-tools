from pathlib import Path

import typer
from loguru import logger

from modapp_tools.code_generators.web_service import generate_web_service
from modapp_tools.protobuf_parser.parser import parse_protobuf

app = typer.Typer()


def parse_and_generate_web_service(source_file: Path, output_dir: Path) -> None:
    proto_module = parse_protobuf(source_file)
    generate_web_service(proto_module, output_dir / f"{source_file.stem}.js")


@app.command()
def generate_from_proto(kind: str, source_file: Path, output_dir: Path) -> None:
    if kind == "webservice":
        parse_and_generate_web_service(source_file, output_dir)
    else:
        logger.error(f"Unknown kind: '{kind}'")


if __name__ == "__main__":
    app()
