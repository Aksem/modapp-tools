import fileinput
import shutil
from pathlib import Path

import grpc_tools
from loguru import logger
from grpc_tools.protoc import main as protoc

import modapp_tools.env as env


def regenerate():
    result_path = env.SERVER_GENERATED_PROTOS_PATH
    for old_file in result_path.glob("*.py"):
        if old_file.is_file():
            old_file.unlink()

    proto_files = list(env.PROTOS_PATH.rglob('*.proto'))
    protoc_path = Path(grpc_tools.__file__).parent / 'protoc.py'
    try:
        protoc([
            str(protoc_path.absolute()),
            f'-I{str(env.PROTOS_PATH.parent)}/',
            f'--python_out={env.SERVER_GENERATED_PROTOS_PATH}',
            f"--grpclib_python_out={env.SERVER_GENERATED_PROTOS_PATH}",
        ] + list(map(lambda x: str(x), proto_files)))
        logger.info("Successfully regenerated")
    except Exception as error:
        logger.error(f"Regenerate status: {error}")
        raise Exception("Failed to generate")

    # protoc generates in the dir with the same name as protos dir instead of just destination dir, move generated files
    shutil.copytree(result_path / env.PROTOS_PATH.stem, result_path, dirs_exist_ok=True)
    shutil.rmtree(result_path / env.PROTOS_PATH.stem)

    # the same problem with a package name. It is like protos dir name, rename
    with fileinput.FileInput(files=result_path.glob("*.py"), inplace=True) as file:
        for line in file:
            print(line.replace(f"{env.PROTOS_PATH.stem}.", f"{env.SERVER_GENERATED_PROTOS_PATH.stem}."), end="")


if __name__ == "__main__":
    regenerate()
