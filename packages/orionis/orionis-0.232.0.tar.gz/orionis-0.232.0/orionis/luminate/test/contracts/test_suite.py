from abc import ABC, abstractmethod

class ITestSuite(ABC):
    """
    Provides utility methods to configure and execute unit tests from specified folders.
    """

    @staticmethod
    @abstractmethod
    def load(
        base_path: str = 'tests',
        folder_path: list | str = '*',
        pattern: str = 'test_*.py'
    ):
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
        pass
