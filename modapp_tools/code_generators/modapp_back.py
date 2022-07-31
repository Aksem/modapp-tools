from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import libcst as cst
import libcst.matchers as m
from libcst.codemod import (
    CodemodContext,
    VisitorBasedCodemodCommand,
    transform_module,
    TransformSuccess,
)
from libcst.codemod.visitors import AddImportsVisitor

import modapp_tools.env as env
from modapp_tools.visitor import Visitor
from modapp_tools.protobuf_parser.ast import (
    ProtoModule,
    ServiceEndpoint,
    Package,
    Service,
)
from modapp_tools.strutils import to_snake_case

# TODO:
# 1. Generate model if not exist
# 2. Generate service per rpc endpoint if not exist
# 3. Generate persistance per rpc endpoint if not exist
# 4. Generate service test  if not exist
# 5. Generate persistance test  if not exist

# TODO: detect changes in protos und update back appropriately


def generate_back(
    proto_module: ProtoModule, proto_module_path: Path, output: Path
) -> None:
    """Generate backend code for modapp-based app from ProtoModule instance.

    proto_module (ProtoModule) - proto module to generate code from
    proto_module_path (Path) - path of proto module relative to root
    output (Path) - path to modapp app root directory
    """
    py_module_rel_path = proto_module_path.parent / f"{proto_module_path.stem}.py"
    # generate_model(proto_module, py_module_rel_path, output)
    generate_service(proto_module, py_module_rel_path, output)


def read_or_create_py_module_to_str(path: Path) -> str:
    if path.exists():
        with open(path, "r") as module_file:
            return module_file.read()
    return ""


def generate_model(
    proto_module: ProtoModule, py_module_rel_path: Path, output: Path
) -> None:
    ...
    # model_module_path = output / "models" / py_module_rel_path
    # cst_module = read_or_create_py_module(model_module_path)

    # print(cst_module)


@dataclass
class ProtoModuleInfo:
    package_name: str = ""
    service_name: str = ""
    service_endpoints: List[ServiceEndpoint] = field(default_factory=list)


class ProtoServiceEndpointCollector(Visitor):
    def __init__(self, proto_info: ProtoModuleInfo) -> None:
        super().__init__()
        self.proto_info = proto_info

    def visit_Package(self, package: Package) -> bool:
        self.proto_info.package_name = package.package_name
        return False

    def visit_Service(self, service: Service) -> bool:
        self.proto_info.service_name = service.name
        return True

    def visit_ServiceEndpoint(self, endpoint: ServiceEndpoint) -> bool:
        self.proto_info.service_endpoints.append(endpoint)
        return False


class ModappServiceCodemod(VisitorBasedCodemodCommand):
    def __init__(
        self,
        context: CodemodContext,
        proto_info: ProtoModuleInfo,
        py_module_rel_path: Path,
        app_name: str,
    ) -> None:
        super().__init__(context)
        self.proto_info = proto_info
        self.py_module_rel_path = py_module_rel_path
        self.app_name = app_name

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.CSTNode:
        body = list(updated_node.body)

        router_assign_matcher = m.Assign(
            targets=(m.AssignTarget(target=m.Name(value="router")),),
            value=m.Call(func=m.Name(value="APIRouter")),
        )
        router_defined = m.matches(
            updated_node,
            m.Module(
                body=(
                    m.ZeroOrMore(),
                    m.SimpleStatementLine(body=(router_assign_matcher,)),
                    m.ZeroOrMore(),
                ),
            ),
        )

        if not router_defined:
            # insert before first function or class, because import can be also conditional.
            index_to_insert = -1
            for index, el in enumerate(body):
                if m.matches(el, m.FunctionDef() | m.ClassDef()):
                    index_to_insert = index

            service_grpc_class = f"{self.proto_info.service_name}Base"
            body.insert(
                index_to_insert,
                cst.SimpleStatementLine(
                    body=[
                        cst.Assign(
                            targets=(
                                cst.AssignTarget(target=cst.Name(value="router")),
                            ),
                            value=cst.Call(
                                func=cst.Name(value="APIRouter"),
                                args=(cst.Arg(value=cst.Name(service_grpc_class)),),
                            ),
                        ),
                    ],
                ),
            )
            AddImportsVisitor.add_needed_import(
                self.context,
                "modapp",
                "APIRouter",
            )
            module_name = self.py_module_rel_path.stem
            AddImportsVisitor.add_needed_import(
                self.context,
                f"{env.SERVER_GENERATED_PROTOS_PATH.name}.{module_name}_grpc",
                service_grpc_class,
            )

        py_module_import_path = str(self.py_module_rel_path).replace("/", ".")
        endpoint_path = self.proto_info.service_name
        if self.proto_info.package_name != "":
            endpoint_path = self.proto_info.package_name + "." + endpoint_path

        for endpoint in self.proto_info.service_endpoints:
            full_endpoint_path = f"/{endpoint_path}/{endpoint.name}"
            endpoint_exists = m.matches(
                updated_node,
                m.Module(
                    body=(
                        m.ZeroOrMore(),
                        m.FunctionDef(
                            decorators=(
                                m.ZeroOrMore(),
                                m.Decorator(
                                    decorator=m.Call(
                                        func=m.Attribute(
                                            value=m.Name(value="router"),
                                            attr=m.Name(value="endpoint"),
                                        ),
                                        # TODO: improve string check
                                        args=[
                                            m.Arg(
                                                value=m.SimpleString(
                                                    value=m.MatchIfTrue(
                                                        lambda x: (
                                                            full_endpoint_path in x
                                                        )
                                                    )
                                                )
                                            )
                                        ],
                                    )
                                ),
                            )
                        ),
                        m.ZeroOrMore(),
                    ),
                ),
            )

            if not endpoint_exists:
                func_name = f"{to_snake_case(endpoint.name)}_endpoint"
                request_class_name = f"{endpoint.name}Request"
                response_class_name = f"{endpoint.name}Reply"

                endpoint_template = f"""@router.endpoint("{full_endpoint_path}")
def {func_name}(request: {request_class_name}) -> {response_class_name}:
    return {response_class_name}()"""
                try:
                    parsed_template_body = list(cst.parse_module(endpoint_template).body)
                    # add empty line before new code
                    func_def = parsed_template_body[0]
                    parsed_template_body[0] = func_def.with_changes(leading_lines=[cst.EmptyLine(), cst.EmptyLine()])
                    body.extend(parsed_template_body)
                except Exception as e:
                    print(e)

                AddImportsVisitor.add_needed_import(
                    self.context,
                    f"{self.app_name}.models.{py_module_import_path}",
                    request_class_name,
                )
                AddImportsVisitor.add_needed_import(
                    self.context,
                    f"{self.app_name}.models.{py_module_import_path}",
                    response_class_name,
                )

        return updated_node.with_changes(body=tuple(body))


def generate_service(
    proto_module: ProtoModule, py_module_rel_path: Path, output: Path
) -> None:
    service_module_path = output / "services" / py_module_rel_path
    py_module_str = read_or_create_py_module_to_str(service_module_path)
    app_name = output.stem

    proto_info = ProtoModuleInfo()
    proto_info_collector = ProtoServiceEndpointCollector(proto_info)
    proto_module.visit(proto_info_collector)

    codemod_context = CodemodContext()
    codemod = ModappServiceCodemod(
        codemod_context, proto_info, py_module_rel_path, app_name
    )
    mod_result = transform_module(codemod, py_module_str)
    if not isinstance(mod_result, TransformSuccess):
        print(mod_result)
        raise Exception()

    if mod_result.code != py_module_str:
        with open(service_module_path, "w") as module_file:
            module_file.write(mod_result.code)
