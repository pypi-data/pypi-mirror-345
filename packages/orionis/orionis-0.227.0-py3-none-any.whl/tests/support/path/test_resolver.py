from orionis.luminate.support.paths.resolver import Resolver
from orionis.luminate.test.test_case import TestCase

class TestsResolver(TestCase):

    async def testFileNotFound(self):
        """
        Test the Resolver class for a non-existent file path.
        """
        file_path = "non_existent_file.txt"
        with self.assertRaises(FileNotFoundError):
            Resolver().relativePath(file_path)

    async def testValidFilePath(self):
        """
        Test the Resolver class for a valid file path.
        """
        path = Resolver().relativePath('orionis/luminate/test/test_suite.py').toString()
        self.assertTrue(path.endswith('test_suite.py'))

    async def testOtherBasePath(self):
        """
        Test the Resolver class for a different base path.
        """
        path = Resolver('orionis/luminate/test').relativePath('test_suite.py').toString()
        self.assertTrue(path.endswith('test_suite.py'))

    async def testEqualOutputString(self):
        """
        Test the Resolver class for a string representation of the resolved path.
        """
        path = Resolver().relativePath('orionis/luminate/test/test_suite.py')
        self.assertEqual(path.toString(), str(path))