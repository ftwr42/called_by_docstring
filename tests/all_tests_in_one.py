import unittest

from add_docstring.add_docstring import AddDocstring
from models import print_of_modules
from reflect.check_for_called_functions import CheckForCalledFunctions
from reflect.reflect_the_dir import ReflectTheDir


class MyTestCase(unittest.TestCase):

    def test_paths_1(self):
        modules = ReflectTheDir(path='tests.test_file').reflect()
        d = print_of_modules(modules)

        test_d = {
            'tests.test_file.py': [],
        }

        self.assertEqual(d, test_d)  # add assertion here


    def test_paths_2(self):
        modules = ReflectTheDir(path='src.main').reflect()
        d = print_of_modules(modules)

        test_d = {
            'src.main.py': [],
        }

        self.assertEqual(d, test_d)  # add assertion here

    def test_paths_3(self):
        modules = ReflectTheDir(path='src').reflect()
        d = print_of_modules(modules)

        test_d = {
            'src.add_docstring.add_docstring.py': [],
            'src.main.py': [],
            'src.models.py': [],
            'src.reflect.check_for_called_functions.py': [],
            'src.reflect.reflect_the_dir.py': [],
        }

        self.assertEqual(d, test_d)  # add assertion here


    def test_recursive_module_reflection(self):
        reflect = ReflectTheDir(path='src')
        modules = reflect._recursive_module_reflection()
        dict_of_modules = {}
        for module in modules:
            dict_of_modules[str(module.path)] = []
        test_dir = {
            'src.add_docstring.add_docstring.py': [],
            'src.main.py': [],
            'src.models.py': [],
            'src.reflect.check_for_called_functions.py': [],
            'src.reflect.reflect_the_dir.py': [],
        }
        self.assertEqual(dict_of_modules, test_dir)  # add assertion here

    def test_scan_modules_for_functions(self):
        reflection = ReflectTheDir(path='src')
        modules = reflection._recursive_module_reflection()
        modules_with_functions = reflection._scan_modules_for_functions(modules=modules)

        d = {}
        for module in modules_with_functions:
            s=f"{str(module)}:"
            if module.functions is not None:
                for f in module.functions:
                    d[f"{s}{str(f)}"] = []
            else:
                d[s] = []

        test_dir = {
            'src.add_docstring.add_docstring.py:_get_docstring': [],
            'src.add_docstring.add_docstring.py:add': [],
            'src.main.py:': [],
            'src.models.py:': [],
            'src.reflect.check_for_called_functions.py:_resolve_module_path': [],
            'src.reflect.check_for_called_functions.py:check': [],
            'src.reflect.check_for_called_functions.py:visit_AsyncFunctionDef': [],
            'src.reflect.check_for_called_functions.py:visit_Call': [],
            'src.reflect.check_for_called_functions.py:visit_ClassDef': [],
            'src.reflect.check_for_called_functions.py:visit_FunctionDef': [],
            'src.reflect.reflect_the_dir.py:_recursive_module_reflection': [],
            'src.reflect.reflect_the_dir.py:_scan_modules_for_functions': [],
            'src.reflect.reflect_the_dir.py:reflect': []
        }
        self.assertEqual(d, test_dir)

    def test_reflect(self):
        modules = ReflectTheDir(path='src').reflect()

        d = {}
        for module in modules:
            s=f"{str(module)}:"
            if module.functions is not None:
                for f in module.functions:
                    d[f"{s}{str(f)}"] = []
            else:
                d[s] = []

        test_dir = {
            'src.add_docstring.add_docstring.py:': [],
            'src.main.py:': [],
            'src.models.py:': [],
            'src.reflect.check_for_called_functions.py:': [],
            'src.reflect.reflect_the_dir.py:': [],
        }
        self.assertEqual(test_dir, d)

    def test_finding_functions(self):
        reflection = ReflectTheDir(path='src')
        modules = reflection._scan_modules_for_functions(reflection.reflect())
        check = CheckForCalledFunctions(modules=modules).check()

        d = {}
        for module in check:
            s = f"{str(module)}:"
            if module.functions is not None:
                for f in module.functions:
                    k = f"{s}{str(f)}"
                    d[k] = []
                    if f.called_functions is not None:
                        for cf in f.called_functions:
                            d[k].append(cf)

            else:
                d[s] = []

        test_dir = {
            'src.add_docstring.add_docstring.py:_get_docstring': [],
            'src.add_docstring.add_docstring.py:add': ['_get_docstring'],
            'src.main.py:': [],
            'src.models.py:': [],

            'src.reflect.check_for_called_functions.py:_resolve_module_path': [],
            'src.reflect.check_for_called_functions.py:check': ["_resolve_module_path", ],
            'src.reflect.check_for_called_functions.py:visit_AsyncFunctionDef': [],
            'src.reflect.check_for_called_functions.py:visit_Call': [],
            'src.reflect.check_for_called_functions.py:visit_ClassDef': [],
            'src.reflect.check_for_called_functions.py:visit_FunctionDef': [],

            'src.reflect.reflect_the_dir.py:_recursive_module_reflection': [],
            'src.reflect.reflect_the_dir.py:_scan_modules_for_functions': [],
            'src.reflect.reflect_the_dir.py:reflect': ["_recursive_module_reflection"]
        }
        self.assertEqual(d, test_dir)


if __name__ == '__main__':
    unittest.main()
