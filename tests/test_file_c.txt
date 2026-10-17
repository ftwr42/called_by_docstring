class TestClass:
    def __init__(self):
        """
        Initialize the TestClass instance.
        """
        pass

    def test_func_a(self):
        """
        Perform some action a.
        """
        _, _ = self.test_func_b, self.test_func_c()

    def test_func_b(self):
        """
        Perform another action b.
        """
        _, _ = self.test_func_a(), self.test_func_c()

    def test_func_c(self):
        """
        Perform yet another action c.
        """
        _, _ = self.test_func_a(), self.test_func_b()