from pathlib import Path

from command_runner import command_runner
from loguru import logger

import modapp_tools.env as env
from modapp_tools.code_generators.web_service import parse_and_generate_web_service
from ._fix_protos_js import fix_js_protos
from ._regenerate_py import regenerate as regenerate_py


def regenerate_all():
    try:
        regenerate_py()
    except Exception as error:
        logger.error(
            f"Fail to regenerate server protos: {error}"
        )

    client_exit_code, client_output = command_runner(
        "yarn run generate-services", shell=True, cwd=env.CLIENT_PATH
    )
    if client_exit_code != 0:
        logger.error(
            f"Fail to regenerate client protos, status code: {client_exit_code}"
        )
        logger.error(client_output)
        raise Exception("Fail to regenerate client protos")

    try:
        fix_js_protos()
        logger.info("2/3: Regenerated client protos successfully")
    except Exception as error:
        logger.error(
            f"Fail to regenerate client protos: {error}"
        )


def regenerate_proto(proto_path: Path) -> None:
    # regenerate js service
    output_path = (
        env.CLIENT_PATH / env.CLIENT_SERVICES_PATH
    )
    try:
        parse_and_generate_web_service(proto_path.absolute(), output_path)
    except Exception as error:
        logger.error(
            f"Fail to regenerate client protos: {error}"
        )


if __name__ == "__main__":
    regenerate_all()
