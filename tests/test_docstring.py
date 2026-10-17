import shutil
import tempfile
import unittest
from pathlib import Path

from add_docstring.add_docstring import AddDocstring
from reflect.check_for_called_functions import CheckForCalledFunctions
from reflect.reflect_the_dir import ReflectTheDir
from models import ModuleModel, FunctionModel


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self._restore_test_file_a()
        self.addCleanup(self._restore_test_file_a)

    @staticmethod
    def _restore_test_file_a():
        directory = Path(__file__).resolve().parent
        shutil.copyfile(directory / "test_file_c.txt", directory / "test_file_a.py")

    def test_print_class_file(self):
        f1 = FunctionModel(function_name="test_func_a", called_functions=None, docstring=None)
        f2 = FunctionModel(function_name="test_func_b", called_functions=None, docstring=None)
        f3 = FunctionModel(function_name="test_func_c", called_functions=None, docstring=None)

        ad = AddDocstring(path="tests.test_file_a", functions=[f1, f2, f3])
        s = ad.print_class_file()
        print(s)
        self.assertTrue(s is not None)

    def test_get_docstrings(self):
        reflection = ReflectTheDir(path='tests.test_file_a')
        modules = reflection._scan_modules_for_functions(reflection.reflect())
        check = CheckForCalledFunctions(modules=modules).check()

        f = check[0].functions
        ad = AddDocstring(path="tests.test_file_a", functions=f)
        ad._get_docstring()

        self.assertEqual(f[0].docstring, "Perform some action a.")
        self.assertEqual(f[1].docstring, "Perform another action b.")
        self.assertEqual(f[2].docstring, "Perform yet another action c.")

    def test_get_docstrings_and_annotate_called_by(self):
        reflection = ReflectTheDir(path='tests.test_file_a')
        modules = reflection._scan_modules_for_functions(reflection.reflect())
        check = CheckForCalledFunctions(modules=modules).check()

        f = check[0].functions
        ad = AddDocstring(path="tests.test_file_a", functions=f)
        ad._get_docstring()

        self.assertEqual("Perform some action a.", f[0].docstring)
        self.assertEqual("Perform another action b.", f[1].docstring)
        self.assertEqual("Perform yet another action c.", f[2].docstring)

        ad._annotate_called_by()

        self.assertEqual("Perform some action a.\ncalled_by: test_func_b, test_func_c", f[0].docstring)
        self.assertEqual("Perform another action b.\ncalled_by: test_func_a, test_func_c", f[1].docstring)
        self.assertEqual("Perform yet another action c.\ncalled_by: test_func_a, test_func_b", f[2].docstring)

    def test_write_annotation_to_file(self):
        reflection = ReflectTheDir(path='tests.test_file_a')
        modules = reflection._scan_modules_for_functions(reflection.reflect())
        check = CheckForCalledFunctions(modules=modules).check()

        f = check[0].functions
        ad = AddDocstring(path="tests.test_file_a", functions=f)
        ad._get_docstring()
        ad._annotate_called_by()
        ad._write_new_annotation_to_file()

        # read file content
        with open("test_file_a.py", "r", encoding="utf-8") as file_a, \
            open("test_file_b.txt", "r", encoding="utf-8") as file_b:
            content_a = file_a.read()
            content_b = file_b.read()

            self.assertTrue(content_a.__eq__(content_b))

    def test_remove_called_by_annotation(self):
        reflection = ReflectTheDir(path='tests.test_file_a')
        modules = reflection._scan_modules_for_functions(reflection.reflect())
        check = CheckForCalledFunctions(modules=modules).check()

        f = check[0].functions
        ad = AddDocstring(path="tests.test_file_a", functions=f)

        ad._remove_called_by_annotation()

        # read file content
        with open("test_file_a.py", "r", encoding="utf-8") as file_a, \
            open("test_file_c.txt", "r", encoding="utf-8") as file_c:
            content_a = file_a.read()
            content_c = file_c.read()

            self.assertTrue(content_a.__eq__(content_c))



if __name__ == '__main__':
    unittest.main()
