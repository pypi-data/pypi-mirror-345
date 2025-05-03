class ITests:
    """
    Provides utility methods to configure and execute unit tests from specified folders.
    """

    @staticmethod
    def execute(folders: list, print_result:bool = True, throw_exception:bool = False):
        """
        Configure and run unit tests from a list of folder definitions.

        Parameters
        ----------
        folders : list of dict
            Each dict must include:
            - 'folder_path' (str): Path to the folder with test files.
            - 'base_path' (str): Base path for resolving test imports.
            - 'pattern' (str): Glob pattern for test file names.

        print_result : bool, default=True
            Whether to print test results to the console.

        throw_exception : bool, default=False
            Whether to raise exceptions on test failures.

        Returns
        -------
        UnitTestClass
            The initialized and executed test suite.

        Raises
        ------
        TypeError
            If `folders` is not a list of dictionaries.
        KeyError
            If any dictionary lacks required keys: 'folder_path', 'base_path', or 'pattern'.
        """
        pass
