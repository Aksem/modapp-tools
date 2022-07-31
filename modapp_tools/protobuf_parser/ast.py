from dataclasses import dataclass
from typing import List, Sequence, Union

from lark import ast_utils

from modapp_tools.cst import CstNode


class _Ast(ast_utils.Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass


class _Statement(_Ast, CstNode):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass


@dataclass
class ProtoModule(_Ast, ast_utils.AsList, CstNode):
    instructions: List[_Statement]

    @property
    def children(self) -> Sequence[_Ast]:
        return self.instructions


@dataclass
class Newline(_Statement):
    content: str


@dataclass
class Comment(_Statement):
    text: str
    newline: str = "\n"


@dataclass
class Syntax(_Statement):
    syntax_name: str


@dataclass
class Package(_Statement):
    package_name: str


@dataclass
class Import(_Statement):
    module_to_import: str


Value = Union[str, bool, int, float]


@dataclass
class Option(_Statement):
    name: str
    value: Value


@dataclass
class Message(_Statement):
    name: str
    statements: List[_Statement]

    @property
    def children(self) -> Sequence[CstNode]:
        return self.statements


@dataclass
class MessageProperty(_Statement):
    repeated: bool
    data_type: str
    name: str
    number: int


@dataclass
class EnumItem(_Statement):
    name: str
    value: int


@dataclass
class Enum(_Statement):
    name: str
    items: List[_Statement]


@dataclass
class ServiceEndpoint(_Statement):
    name: str
    argument_is_stream: bool
    argument_type: str
    return_is_stream: bool
    return_type: str


@dataclass
class Service(_Statement):
    name: str
    statements: List[_Statement]
    
    @property
    def children(self) -> Sequence[_Ast]:
        return self.statements
