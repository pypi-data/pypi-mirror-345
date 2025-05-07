import re
from os import walk
from orionis.luminate.test.contracts.test_suite import ITestSuite
from orionis.luminate.test.test_unit import UnitTest as UnitTestClass

class TestSuite(ITestSuite):
    """
    A class containing test utility methods.
    """

    @staticmethod
    def load(
        base_path: str = 'tests',
        folder_path: list | str = '*',
        pattern: str = 'test_*.py'
    ) -> UnitTestClass:
        """
        Discover and initialize a test suite from the specified folder(s).

        This method scans the provided folder(s) for test files matching the given pattern
        and initializes a test suite with the discovered files.

        Parameters
        ----------
        base_path : str, optional
            The base path for the tests. Defaults to 'tests'.
        folder_path : str or list of str, optional
            Path(s) to the folder(s) containing test files. Use '*' to scan all folders
            under the base path. Defaults to '*'.
        pattern : str, optional
            File pattern to match test files. Defaults to 'test_*.py'.

        Returns
        -------
        UnitTestClass
            An initialized test suite containing the discovered test files.

        Raises
        ------
        TypeError
            If `base_path` is not a string, `folder_path` is not a string or list, or
            `pattern` is not a string.
        """
        # Validate parameters
        if not isinstance(base_path, str):
            raise TypeError("base_path must be a string")
        if not isinstance(folder_path, (str, list)):
            raise TypeError("folder_path must be a string or a list")
        if not isinstance(pattern, str):
            raise TypeError("pattern must be a string")

        # Helper function to list folders matching the pattern
        def list_matching_folders(custom_path: str, pattern: str):
            matched_folders = []
            for root, _, files in walk(custom_path):
                for file in files:
                    if re.fullmatch(pattern.replace('*', '.*').replace('?', '.'), file):
                        relative_path = root.replace(base_path, '').replace('\\', '/').lstrip('/')
                        if relative_path not in matched_folders:
                            matched_folders.append(relative_path)
            return matched_folders

        # Discover folders
        discovered_folders = []
        if folder_path == '*':
            discovered_folders.extend(list_matching_folders(base_path, pattern))
        elif isinstance(folder_path, list):
            for custom_path in folder_path:
                discovered_folders.extend(list_matching_folders(custom_path, pattern))
        else:
            discovered_folders.extend(list_matching_folders(folder_path, pattern))

        # Initialize the test suite
        tests = UnitTestClass()

        # Add discovered folders to the test suite
        for folder in discovered_folders:
            tests.discoverTestsInFolder(
                base_path=base_path,
                folder_path=folder,
                pattern=pattern
            )

        # Return the initialized test suite
        return tests