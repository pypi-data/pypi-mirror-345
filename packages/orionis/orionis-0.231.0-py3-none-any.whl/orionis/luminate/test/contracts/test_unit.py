from typing import Any, Dict, Optional

class IUnitTest:
    """
    Advanced unit testing utility for discovering, executing, and reporting test results
    with support for folder-based discovery, regex filtering, and customizable output.

    Attributes
    ----------
    loader : unittest.TestLoader
        Internal loader for test discovery.
    suite : unittest.TestSuite
        The aggregated test suite to be executed.
    test_results : List[TestResult]
        List of captured results per test, including status and errors.
    start_time : float
        Timestamp when the test execution started.
    """

    def discoverTestsInFolder(
        self,
        folder_path: str,
        base_path: str = "tests",
        pattern: str = "test_*.py",
        test_name_pattern: Optional[str] = None
    ):
        """
        Discover and add test cases from a given folder to the test suite.

        Parameters
        ----------
        folder_path : str
            Relative path to the folder containing test files.
        base_path : str, default="tests"
            Base path used to resolve full path to test modules.
        pattern : str, default="test_*.py"
            Glob pattern to match test filenames.
        test_name_pattern : Optional[str], optional
            Regex pattern to filter discovered test method names.

        Returns
        -------
        UnitTest
            Self instance for chaining.

        Raises
        ------
        ValueError
            If folder is invalid or no tests are found.
        """
        pass

    def run(self, print_result:bool = True, throw_exception:bool = False) -> Dict[str, Any]:
        """
        Run all added tests and return a summary of the results.

        Parameters
        ----------
        print_result : bool, default=True
            Whether to print a formatted report to the console.
        throw_exception : bool, default=False
            Raise an exception if there are failures or errors.

        Returns
        -------
        Dict[str, Any]
            Summary including:
            - total_tests : int
            - passed : int
            - failed : int
            - errors : int
            - skipped : int
            - total_time : str (e.g., '1.234 seconds')
            - success_rate : str (e.g., '87.5%')
            - test_details : List[Dict[str, Any]]

        Raises
        ------
        OrionisTestFailureException
            If any test fails or errors occur and `throw_exception=True`.
        """
        pass