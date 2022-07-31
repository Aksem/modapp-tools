"""
Use top-down approach.

In current implementation template-based approach is used for code generation,
maybe Protobuf AST -> JS AST -> code would be better, need to be investigated.
The probem is that there are almost no JS code  generators in python.

The con of template-based approach is that code formatter should be run on 
generated code to match project formatting style.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Set

from modapp_tools.cst import CstNode
from modapp_tools.protobuf_parser.ast import (
    Comment,
    Message,
    MessageProperty,
    Package,
    ProtoModule,
    Service,
    ServiceEndpoint,
)
from modapp_tools.protobuf_parser.parser import parse_protobuf
from modapp_tools.visitor import Visitor
from .js_cst import CodeElement, CodeElementList, Import


class WebServiceGenerator(Visitor):
    def __init__(self) -> None:
        super().__init__()

        self.code_el_list: CodeElementList = CodeElementList()
        self.package_name: Optional[str] = None
        self.current_service: Optional[Service] = None
        self.local_messages: Dict[str, Message] = {}
        self.msg_props_by_msg_name: Dict[str, List[MessageProperty]] = {}
        # NOTE: messages can be nested, that's why sequence is needed
        self.current_messages: List[Message] = []

    def visit_ProtoModule(self, module: ProtoModule) -> bool:
        # module itself generates no code, return True to process all children
        return True

    def leave_ProtoModule(self, module: ProtoModule) -> CstNode:
        # package name and local messages are module-specific, reset them
        self.package_name = None
        self.local_messages = {}
        self.msg_props_by_msg_name = {}
        return module

    def visit_Package(self, package: Package) -> bool:
        self.package_name = package.package_name
        return False

    def visit_Message(self, message: Message) -> bool:
        self.current_messages.append(message)
        self.local_messages[message.name] = message
        return True

    def leave_Message(self, message: Message) -> CstNode:
        self.current_messages.pop(-1)
        return message

    def visit_MessageProperty(self, msg_property: MessageProperty) -> bool:
        if len(self.current_messages) == 0:
            raise Exception("Message property visit, but there is no Message")
        current_message = self.current_messages[-1]

        if current_message.name not in self.msg_props_by_msg_name:
            self.msg_props_by_msg_name[current_message.name] = []
        self.msg_props_by_msg_name[current_message.name].append(msg_property)
        return False

    def visit_Service(self, service: Service) -> bool:
        service_name_formatted = service.name[0].lower() + service.name[1:]
        self.code_el_list.append(
            CodeElement(f"export const {service_name_formatted} = {{")
        )
        self.current_service = service
        for child in service.statements:
            child.visit(self)
        self.current_service = None
        self.code_el_list.append(CodeElement("};"))
        return False

    def visit_ServiceEndpoint(self, endpoint: ServiceEndpoint) -> bool:
        if self.current_service is None:
            raise Exception("ServiceEndpoint generation, but there is no service")

        imports: Set[Import] = set()
        formatted_name = endpoint.name[0].lower() + endpoint.name[1:]
        endpoint_type = ""
        if endpoint.argument_is_stream:
            endpoint_type += "Stream"
        else:
            endpoint_type += "Unary"
        if endpoint.return_is_stream:
            endpoint_type += "Stream"
        else:
            endpoint_type += "Unary"

        if self.package_name is not None:
            endpoint_package = self.package_name + "."
        else:
            endpoint_package = ""

        method_args: List[str] = []
        endpoint_argument_params: List[str] = []
        if endpoint.argument_type in self.local_messages.keys():
            # local message
            argument_type_full_name = endpoint.argument_type
            if self.package_name is not None:
                argument_type_full_name = (
                    f"{self.package_name}.{argument_type_full_name}"
                )
                imports.add(
                    Import(
                        name=self.package_name.split(".")[0],
                        default=False,
                        path="./protos.js",
                    )
                )
            else:
                # no package, import message by name
                imports.add(
                    Import(
                        name=argument_type_full_name, default=False, path="./protos.js"
                    )
                )

            for msg_property in self.msg_props_by_msg_name[endpoint.argument_type]:
                method_args.append(f"{msg_property.name} = null")
                endpoint_argument_params.append(msg_property.name)
        else:
            # imported message
            argument_type_full_name = endpoint.argument_type
            # google.rpc.Empty -> import 'google' const
            imports.add(
                Import(
                    name=argument_type_full_name.split(".")[0],
                    default=False,
                    path="./protos.js",
                )
            )
            # TODO: check whether message exists in source module?
            # TODO: msg_properties of imported message

        if endpoint.return_type in self.local_messages.keys():
            # local message
            return_type_full_name = endpoint.return_type
            if self.package_name is not None:
                return_type_full_name = f"{self.package_name}.{return_type_full_name}"
                imports.add(
                    Import(
                        name=self.package_name.split(".")[0],
                        default=False,
                        path="./protos.js",
                    )
                )
            else:
                # no package, import message by name
                imports.add(
                    Import(
                        name=return_type_full_name, default=False, path="./protos.js"
                    )
                )
        else:
            # imported message
            return_type_full_name = endpoint.return_type
            # google.rpc.Empty -> import 'google' const
            imports.add(
                Import(
                    name=return_type_full_name.split(".")[0],
                    default=False,
                    path="./protos.js",
                )
            )
            # TODO: check whether message exists in source module?

        if len(method_args) > 0:
            method_args_str = "{" + ", ".join(method_args) + "} = {}"
        else:
            method_args_str = ""
        endpoint_argument_params_str = "{ " + ", ".join(endpoint_argument_params) + " }"
        func_name = f"rpc{endpoint_type}Call"
        if endpoint_type == "UnaryStream":
            template = f"""    {formatted_name}: {func_name}(
        '/{endpoint_package}{self.current_service.name}/{endpoint.name}',
        {argument_type_full_name},
        {return_type_full_name}
    ),
"""
        else:
            template = f"""    {formatted_name}({method_args_str}) {{
        return {func_name}(
            '/{endpoint_package}{self.current_service.name}/{endpoint.name}',
            {argument_type_full_name},
            {return_type_full_name},
            {endpoint_argument_params_str}
        );
    }},
"""
        imports.add(Import(func_name, default=False, path="./rpc.js"))
        self.code_el_list.append(CodeElement(template, imports=imports))
        return False

    def visit_Comment(self, comment: Comment) -> bool:
        # keep all comments
        self.code_el_list.append(CodeElement(f"// {comment.text}"))
        return False


def generate_web_service(proto_module: ProtoModule, output: Path) -> None:
    """Generate web service module from ProtoModule instance.

    proto_module (ProtoModule) - proto module to generate code from
    output (Path) - path to output file including name and extension
    """
    visitor = WebServiceGenerator()
    proto_module.visit(visitor)

    with open(output, "w") as output_file:
        output_file.write(visitor.code_el_list.to_js_module_code())


def parse_and_generate_web_service(source_file: Path, output_dir: Path) -> None:
    proto_module = parse_protobuf(source_file)
    generate_web_service(proto_module, output_dir / f"{source_file.stem}.js")
