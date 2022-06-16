from __future__ import annotations
from typing import Set, Optional, List, Dict, Tuple


class Import:
    def __init__(self, name: str, default: bool, path: str):
        self.name = name
        self.default = default
        self.path = path
    
    def __eq__(self, other: Import) -> bool:
        return self.name == other.name and self.default == other.default and self.path == other.path
    
    def __hash__(self):
        return hash(self.name) + hash(self.default) + hash(self.path)


class CodeElement:
    def __init__(self, code: str, imports: Optional[Set[Import]] = None) -> None:
        self.code = code
        self.imports = imports


class CodeElementList:
    def __init__(self):
        self.elements = []
    
    def append(self, element: CodeElement):
        self.elements.append(element)
    
    @property
    def code(self) -> str:
        return f'\n'.join([el.code for el in self.elements])

    @property
    def imports(self) -> Set[Import]:
        result = set()
        for element in self.elements:
            if element.imports is not None:
                result |= element.imports
        return result
    
    def __add__(self, other: CodeElementList | None) -> CodeElementList:
        # support also None to simplify generate() usage
        if other is not None:
            self.elements += other.elements
        # imports?
        return self

    def to_js_module_code(self) -> str:
        imports_code = ""
        imports_by_paths: Dict[str, List[Import]] = {}
        for el_import in self.imports:
            if el_import.path not in imports_by_paths:
                imports_by_paths[el_import.path] = []
            imports_by_paths[el_import.path].append(el_import)
        
        imports_paths = list(imports_by_paths.keys())
        # sort to get always the same output
        imports_paths.sort()
        for import_path in imports_paths:
            path_imports = imports_by_paths[import_path]
            default_import = None
            named_imports = []
            for path_import in path_imports:
                if path_import.default is True:
                    default_import = path_import.name
                else:
                    named_imports.append(path_import.name)
            # sort to get always the same output
            named_imports.sort()
            imports_code += f"import"
            if default_import is not None:
                imports_code += ' ' + default_import
            if default_import is not None and len(named_imports) > 0:
                imports_code += ','
            if len(named_imports) > 0:
                imports_code += ' { ' + ', '.join(named_imports) + ' }'
            imports_code += f" from '{import_path}';\n"
            
        return f"{imports_code}\n{self.code}"
