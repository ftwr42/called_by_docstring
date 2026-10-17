import ast
from typing import Dict, List
from pathlib import Path

from models import ModuleModel, FunctionModel


class ReflectTheDir:
    """
    A class that reflects the directory structure of a given path.
    It provides a function to recursively traverse the directory and scans all available Python modules.
    Every module is then scanned for functions.
    This structure is then stored in a dictionary,
    where the keys are the module names and the values are lists of function names.
    """
    def __init__(self, path):
        self.path = Path(path)

    def reflect(self) -> List[ModuleModel]:
        """
        1. Recursively traverse the directory structure starting from the given path.
        2. For each Python module found, scan for functions defined in that module.
        :return:
        """
        return self._recursive_module_reflection()

    def _recursive_module_reflection(self) -> List[ModuleModel]:
        source_dir = self.path

        module_source_dir = Path(__file__).resolve().parents[1]
        if not source_dir.is_dir() and not source_dir.is_absolute() and source_dir.name == module_source_dir.name:
            source_dir = module_source_dir

        if not source_dir.is_dir():
            if _resolve_module_file(self.path) is None:
                raise NotADirectoryError(f"'{self.path}' is not a directory or Python module")

            module_name = self.path.with_suffix("") if self.path.suffix == ".py" else self.path
            return [ModuleModel(path=Path(f"{str(module_name).replace('/', '.')}.py"), functions=None)]

        source_dir = source_dir.resolve()
        prefix = (self.path.name if self.path.is_absolute() else self.path.as_posix()).replace("/", ".")

        module_list: List[ModuleModel] = []
        for module_path in source_dir.rglob("*.py"):
            if not module_path.is_file():
                continue

            relative_name = module_path.relative_to(source_dir).with_suffix("").as_posix().replace("/", ".")
            module_list.append(ModuleModel(path=Path(f"{prefix}.{relative_name}.py"), functions=None))

        return sorted(module_list, key=lambda module: str(module.path))

    def _scan_modules_for_functions(self, modules: List[ModuleModel]) -> List[ModuleModel]:
        search_roots = [self.path.resolve().parent]
        for module in modules:
            absolute_module_path = _resolve_module_file(module.path, search_roots)
            if absolute_module_path is None:
                continue

            with absolute_module_path.open(encoding="utf-8") as source_file:
                syntax_tree = ast.parse(source_file.read(), filename=str(absolute_module_path))

            for class_node in ast.walk(syntax_tree):
                if not isinstance(class_node, ast.ClassDef):
                    continue
                for node in class_node.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not (node.name.startswith("__") and node.name.endswith("__")):
                            function_model = FunctionModel(
                                function_name=node.name,
                                docstring=ast.get_docstring(node),
                                called_functions=None,
                            )
                            if module.functions is None:
                                module.functions = []
                            module.functions.append(function_model)

        return modules


def _resolve_module_file(module: Path, extra_roots: List[Path] | None = None) -> Path | None:
    """Resolve a dotted module name or a .py path against cwd, the project root, src and extra roots."""
    if module.suffix == ".py" and "." not in module.with_suffix("").name and len(module.parts) > 1:
        relative = module
    else:
        dotted = str(module.with_suffix("")) if module.suffix == ".py" else str(module)
        relative = Path(*dotted.split(".")).with_suffix(".py")
    if relative.is_absolute():
        return relative if relative.is_file() else None

    src_root = Path(__file__).resolve().parents[1]
    for base in (Path.cwd(), src_root.parent, src_root, *(extra_roots or [])):
        candidate = base / relative
        if candidate.is_file():
            return candidate.resolve()
    return None
