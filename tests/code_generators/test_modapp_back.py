from pathlib import Path

from modapp_tools.code_generators.modapp_back import generate_model, generate_service
from modapp_tools.protobuf_parser.ast import ProtoModule

from .fixtures import addressbook_proto_module


def test__generate_model__generates_model_if_not_exists():
    generate_model(ProtoModule(instructions=[]), Path('.'), Path('.'))


def test__generate_service__generates_router_if_not_exists():
    generate_service(addressbook_proto_module, Path('addressbook'), Path(''))
    assert 0 == 1
