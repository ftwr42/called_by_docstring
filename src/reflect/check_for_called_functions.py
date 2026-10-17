import ast
from pathlib import Path
from typing import List

from models import ModuleModel
from reflect.reflect_the_dir import _resolve_module_file


class CheckForCalledFunctions:
    def __init__(self, modules: List[ModuleModel]):
        self.modules = modules

    def check(self) -> List[ModuleModel]:
        """
        Record calls to functions defined in the supplied modules.
        """
        modules = self.modules
        known_functions = {
            function.function_name
            for module in modules
            for function in module.functions or []
        }

        for module in modules:
            module_path = self._resolve_module_path(module.path)
            with module_path.open(encoding="utf-8") as source_file:
                syntax_tree = ast.parse(source_file.read(), filename=str(module_path))

            function_nodes = [
                node
                for node in ast.walk(syntax_tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            for function in module.functions or []:
                matching_nodes = [
                    node for node in function_nodes if node.name == function.function_name
                ]
                called_names: List[str] = []
                for node in matching_nodes:
                    visitor = _FunctionCallVisitor()
                    for statement in node.body:
                        visitor.visit(statement)
                    called_names.extend(
                        name for name in visitor.called_names if name in known_functions
                    )

                function.called_functions = list(dict.fromkeys(called_names))

        return modules

    @staticmethod
    def _resolve_module_path(module_path: Path) -> Path:
        if module_path.is_absolute():
            candidates = [module_path]
        else:
            source_root = Path(__file__).resolve().parents[1]
            candidates = [Path.cwd() / module_path, source_root / module_path]

        for candidate in candidates:
            if candidate.is_file():
                return candidate.resolve()

        dotted_path = _resolve_module_file(module_path)
        if dotted_path is not None:
            return dotted_path

        raise FileNotFoundError(f"Could not find module source file: {module_path}")


class _FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.called_names: List[str] = []

    def visit_Call(self, node: ast.Call) -> None:
        function = node.func
        if isinstance(function, ast.Name):
            self.called_names.append(function.id)
        elif isinstance(function, ast.Attribute):
            self.called_names.append(function.attr)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.called_names.append(node.attr)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return