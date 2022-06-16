"""
Tried following strategies:
1. Build AST using transformer & ast_utils immediately after parsing
   It has one big con: the result is only AST without tree/token instances and
   visitors/transformers should be implementend manually, lark-based cannot be used

2. Build ParseTree
"""
import sys
from pathlib import Path
from typing import cast

from lark.lark import Lark
from lark.tree import Tree
from lark.lexer import Token
from lark.visitors import Transformer
from lark import ast_utils

from .ast import *


class ProtoAstTransformer(Transformer):
    true = lambda self, _: True
    false = lambda self, _: False

    def instruction(self, instruction):
        # ignore statement, return first children(statement has always only one child)
        if isinstance(instruction[0], Tree):
            return instruction[0].children[0]
        return instruction[0]

    def value(self, value):
        return value[0]
    
    def statement(self, statement):
        return statement[0]
    
    # Message
    def message_name(self, name):
        return name[0]
    
    def message_content(self, content):
        # return message children, 'message_content' is not needed
        return content
    
    def data_type(self, data_type):
        # return data type directly, 'data_type' tree is not needed
        return data_type[0]

    def repeated(self, repeated):
        return len(repeated) > 0
    
    def property_name(self, name):
        # return name directly
        return name[0]
    
    def property_number(self, number):
        # return number directly
        return number[0]
    
    # Enum
    def enum_name(self, name):
        # return name directly
        return name[0]
    
    def enum_items(self, items):
        # return items directly
        return items

    def enum_item_name(self, name):
        # return name directly
        return name[0]
    
    def enum_item_value(self, value):
        # return value directly
        return value[0]

    # Service
    def service_name(self, name):
        # return name directly
        return name[0]
    
    def service_content(self, content):
        # return children directly
        return content

    # Endpoint
    def endpoint_name(self, name):
        # return name directly
        return name[0]
    
    def endpoint_argument(self, arg):
        # return arg directly
        return arg
    
    def argument_stream(self, argument_stream):
        # return stream value directly
        return argument_stream[0]
    
    def endpoint_argument_type(self, data_type):
        # return data type directly
        return data_type[0]
    
    def endpoint_return(self, return_value):
        # return value directly
        return return_value
    
    def return_stream(self, return_stream):
        # return stream value directly
        return return_stream[0]
    
    def endpoint_return_type(self, data_type):
        # return data type directly
        return data_type[0]

    def stream(self, stream):
        return len(stream) > 0

    # Tokens
    def CPP_COMMENT(self, comment: Token):
        # cut '//'
        return comment.value[2:]

    def NEWLINE(self, newline: Token):
        return newline.value

    def ESCAPED_STRING(self, escaped_string: Token):
        # strip quotes
        return escaped_string.value[1:-1]
    
    def IDENTIFIER(self, identifier: Token):
        return identifier.value
    
    def CNAME(self, cname: Token):
        return cname.value

    def INT(self, number: Token):
        return int(number.value)


this_module = sys.modules[__name__]
transformer = ast_utils.create_transformer(this_module, ProtoAstTransformer())


def parse_protobuf(filepath: Path) -> ProtoModule:
    current_filepath = Path(__file__).parent
    with open(current_filepath / 'protobuf3.lark', 'r') as protobuf_lark:
        protobuf_parser = Lark(protobuf_lark.read(), start='proto_module', parser='lalr', transformer=transformer, cache=True, debug=True)

    with open(filepath, 'r') as protobuf_source:
        parse_tree = protobuf_parser.parse(protobuf_source.read())

    return cast(ProtoModule, parse_tree)
