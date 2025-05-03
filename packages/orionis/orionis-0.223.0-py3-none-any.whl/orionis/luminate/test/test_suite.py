from orionis.luminate.test.contracts.test_suite import ITests
from orionis.luminate.test.test_unit import UnitTest as UnitTestClass

class Tests(ITests):
    """
    A class containing test utility methods.

    Methods
    -------
    folders(folders: list) -> UnitTestClass
        Validates folder configurations and initializes test suite.
    """

    @staticmethod
    def execute(folders: list, print_result:bool = True, throw_exception:bool = False):
        """
        Validate folder configurations and initialize test suite.

        Parameters
        ----------
        folders : list
            List of folder configuration dictionaries. Each dictionary must contain:
            - folder_path : str
                Path to the folder containing test files
            - base_path : str
                Base path for the tests
            - pattern : str
                File pattern to match test files

        Returns
        -------
        UnitTestClass
            Initialized test suite with added folders

        Raises
        ------
        TypeError
            If folders is not a list or contains non-dictionary items
        KeyError
            If any folder dictionary is missing required keys

        Examples
        --------
        >>> Tests.folders([
        ...     {
        ...         'folder_path': 'example',
        ...         'base_path': 'tests',
        ...         'pattern': 'test_*.py'
        ...     }
        ... ])
        """
        if not isinstance(folders, list):
            raise TypeError("folders must be a list")

        for folder in folders:
            if not isinstance(folder, dict):
                raise TypeError("each folder must be a dictionary")
            if not all(key in folder for key in ['folder_path', 'base_path', 'pattern']):
                raise KeyError("each folder must contain 'folder_path', 'base_path' and 'pattern' keys")

        tests = UnitTestClass()
        for folder in folders:
            tests.addFolder(
                base_path=folder['base_path'],
                folder_path=folder['folder_path'],
                pattern=folder['pattern']
            )
        return tests.run(print_result, throw_exception)