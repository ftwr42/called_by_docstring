import ast
import re

from typing import List

from pathlib import Path

from models import ModuleModel, FunctionModel
from reflect.reflect_the_dir import _resolve_module_file


class AddDocstring:
    """
    T = function with call_functions
    Checks if each function with T has a docstring with the field :called_by: and replaces it with
        :called_by:
            - a_function
            - b_function
            - c_function

    when it has no docstring one naive will be created like
        \"\"\"

        \"\"\"

    this. Then if it has a docstring and a :called_by: entry this will be deleted and newly added specific on
    data for this function.
    :return:
    """
    def __init__(self, path:str, functions:List[FunctionModel]):
        self.file_path = path
        self.functions = functions

    def _source_files(self) -> List[Path]:
        directory = Path(self.file_path)
        if not directory.is_dir():
            directory = Path(__file__).resolve().parents[2] / self.file_path
        if directory.is_dir():
            return sorted(directory.rglob("*.py"))

        module_file = _resolve_module_file(Path(self.file_path))
        if module_file is None:
            raise FileNotFoundError(f"Could not find module source file: {self.file_path}")
        return [module_file]

    def _get_docstring(self) -> None:
        """Assign the docstring found in the source files to each function of self.functions."""
        docstrings = {}
        for source_file in self._source_files():
            tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=str(source_file))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    docstrings.setdefault(node.name, ast.get_docstring(node))

        for function in self.functions or []:
            function.docstring = docstrings.get(function.function_name)

    def _annotate_called_by(self) -> None:
        for function in self.functions or []:
            docstring = function.docstring
            if docstring is not None and function.called_functions:
                lines = self._without_called_by(docstring)
                lines.append(":called_by:")
                lines.extend(f"{name}," for name in function.called_functions)
                docstring = "\n".join(lines[-1])
            function.docstring = docstring

    @staticmethod
    def _without_called_by(docstring: str) -> List[str]:
        """Return the docstring lines without an already existing :called_by: section."""
        lines: List[str] = []
        in_section = False
        for line in docstring.splitlines():
            if line.strip().startswith(":called_by:"):
                in_section = True
            elif in_section and line.strip().startswith("-"):
                continue
            else:
                in_section = False
                lines.append(line)
        return lines

    def _annotate_called_by(self) -> None:
        """Append a `called_by:` line to the docstring of every function that is called by other functions."""
        callers: dict = {}
        for function in self.functions or []:
            for called in function.called_functions or []:
                if called != function.function_name:
                    callers.setdefault(called, []).append(function.function_name)

        for function in self.functions or []:
            names = callers.get(function.function_name)
            if function.docstring is None or not names:
                continue
            lines = [line for line in function.docstring.splitlines() if not line.startswith("called_by:")]
            lines.append(f"called_by: {', '.join(names)}")
            function.docstring = "\n".join(lines)

    def _write_new_annotation_to_file(self) -> None:
        """Replace the docstrings in the source files, only if they differ from the original."""
        wanted = {f.function_name: f.docstring for f in self.functions or [] if f.docstring is not None}
        handled = set()
        for source_file in self._source_files():
            source = source_file.read_text(encoding="utf-8")
            lines = source.splitlines(keepends=True)
            tree = ast.parse(source, filename=str(source_file))

            replacements = []
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name not in wanted or node.name in handled:
                    continue
                handled.add(node.name)
                first = node.body[0]
                has_docstring = (
                    isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)
                )
                if has_docstring and ast.get_docstring(node) == wanted[node.name]:
                    continue
                replacements.append((node, first, has_docstring))

            for node, first, has_docstring in sorted(replacements, key=lambda r: r[1].lineno, reverse=True):
                indent = " " * first.col_offset
                text = wanted[node.name].replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
                new_lines = [f'{indent}"""\n']
                new_lines.extend(f"{indent}{line}\n" if line else "\n" for line in text.splitlines())
                new_lines.append(f'{indent}"""\n')
                start = first.lineno - 1
                end = first.end_lineno if has_docstring else start
                lines[start:end] = new_lines

            if replacements:
                source_file.write_text("".join(lines), encoding="utf-8")

    def _remove_called_by_annotation(self) -> None:
        """Remove the `called_by:` lines from the docstrings in the source files and in self.functions."""
        for source_file in self._source_files():
            source = source_file.read_text(encoding="utf-8")
            cleaned = re.sub(r"^[ \t]*called_by:.*(?:\r?\n|$)", "", source, flags=re.MULTILINE)
            if cleaned != source:
                source_file.write_text(cleaned, encoding="utf-8")

        for function in self.functions or []:
            if function.docstring is not None:
                function.docstring = "\n".join(
                    line for line in function.docstring.splitlines() if not line.startswith("called_by:")
                )

    def print_class_file(self) -> str:
        module_file = _resolve_module_file(Path(self.file_path))
        if module_file is None:
            raise FileNotFoundError(f"Could not find module source file: {self.file_path}")
        return module_file.read_text(encoding="utf-8")

    # def add(self):
    #     for module in self.modules:
    #          module.docstring = self._get_docstring()
            # for function in module.functions or []:
            #     if function.called_functions:
            #         if function.docstring is None:
            #             function.docstring = '\"\"\"\n\n\"\"\"'
            #         # Remove existing :called_by: section if present
            #         lines = function.docstring.splitlines()
            #         new_lines = []
            #         in_called_by_section = False
            #         for line in lines:
            #             if line.strip().startswith(':called_by:'):
            #                 in_called_by_section = True
            #                 continue
            #             if in_called_by_section and line.strip().startswith('-'):
            #                 continue
            #             in_called_by_section = False
            #             new_lines.append(line)
            #         # Add the new :called_by: section
            #         new_lines.append(':called_by:')
            #         for called_function in function.called_functions:
            #             new_lines.append(f'    - {called_function}')
            #         function.docstring = '\n'.join(new_lines)
