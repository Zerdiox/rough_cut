import unittest


class PackageImportTest(unittest.TestCase):
    def test_package_imports(self):
        import roughcut  # noqa: F401
