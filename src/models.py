from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict


@dataclass
class FunctionModel:
    function_name:str
    docstring:str|None
    called_functions:List[str]|None

    def __str__(self) -> str:
        buffer = f"{self.function_name}"
        # if self.called_functions is not None:
        #     buffer += ", ".join(self.called_functions)
        return buffer


@dataclass
class ModuleModel:
    path:Path
    functions:List[FunctionModel]|None

    def __str__(self) -> str:
        return str(self.path)


def print_of_modules(modules:List[ModuleModel]) -> Dict:
    d = {}
    for module in modules:
        s = f"{str(module)}:"
        if module.functions is not None:
            for f in module.functions:
                k = f"{s}{str(f)}"
                d[k] = []
                if f.called_functions is not None:
                    for cf in f.called_functions:
                        d[k].append(cf)

        else:
            d[str(module)] = []

    return d

