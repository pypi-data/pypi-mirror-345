import io
import re
import time
import traceback
import unittest
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple
from orionis.luminate.console.output.console import Console
from orionis.luminate.test.test_exception import OrionisTestFailureException
from orionis.luminate.test.test_result import TestResult
from orionis.luminate.test.test_status import TestStatus

class UnitTest:
    """
    An advanced testing framework for discovering, running, and analyzing unit tests.

    Features include:
    - Detailed test discovery and filtering
    - Comprehensive result reporting
    - Performance timing
    - Customizable output formatting
    - Failure analysis

    Attributes
    ----------
    loader : unittest.TestLoader
        Test loader instance for discovering tests
    suite : unittest.TestSuite
        Test suite holding discovered tests
    test_results : List[TestResult]
        Detailed results of executed tests
    start_time : float
        Timestamp when test execution began
    """

    def __init__(self) -> None:
        """Initialize the testing framework."""
        self.loader = unittest.TestLoader()
        self.suite = unittest.TestSuite()
        self.test_results: List[TestResult] = []
        self.start_time: float = 0.0

    def addFolder(
            self,
            folder_path: str,
            base_path: str = "tests",
            pattern: str = "test_*.py",
            test_name_pattern: Optional[str] = None
        ) -> 'UnitTest':
        """
        Discover and add tests from a specified folder to the test suite.

        Parameters
        ----------
        folder_path : str
            Path to the folder containing test files
        pattern : str, optional
            Pattern to match test files (default 'test_*.py')
        test_name_pattern : Optional[str], optional
            Regex pattern to filter test names

        Raises
        ------
        ValueError
            If the folder is invalid or no tests are found
        """
        try:
            tests = self.loader.discover(
                start_dir=f"{base_path}/{folder_path}",
                pattern=pattern,
                top_level_dir=None
            )

            if test_name_pattern:
                tests = self._filter_tests_by_name(tests, test_name_pattern)

            if not list(tests):
                raise ValueError(f"No tests found in '{base_path}/{folder_path}' matching pattern '{pattern}'")

            self.suite.addTests(tests)

            return self

        except ImportError as e:
            raise ValueError(f"Error importing tests from '{base_path}/{folder_path}': {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error discovering tests: {str(e)}")

    def _filter_tests_by_name(self, suite: unittest.TestSuite, pattern: str) -> unittest.TestSuite:
        """Filter tests based on a name pattern."""
        filtered_suite = unittest.TestSuite()
        regex = re.compile(pattern)

        for test in self._flatten_test_suite(suite):
            if regex.search(test.id()):
                filtered_suite.addTest(test)

        return filtered_suite

    def _flatten_test_suite(self, suite: unittest.TestSuite) -> List[unittest.TestCase]:
        """Flatten a test suite into a list of test cases."""
        tests = []
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                tests.extend(self._flatten_test_suite(item))
            else:
                tests.append(item)
        return tests

    def _extract_error_info(self, traceback_str: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract file path and clean traceback from error output.

        Parameters
        ----------
        traceback_str : str
            The full traceback string

        Returns
        -------
        Tuple[Optional[str], Optional[str]]
            (file_path, clean_traceback)
        """
        file_match = re.search(r'File "([^"]+)"', traceback_str)
        file_path = file_match.group(1) if file_match else None

        # Clean up traceback by removing framework internals
        tb_lines = traceback_str.split('\n')
        clean_tb = '\n'.join(line for line in tb_lines if not any(s in line for s in ['unittest/', 'lib/python']))

        return file_path, clean_tb

    def run(self, print_result:bool = True, throw_exception:bool = False) -> Dict[str, Any]:
        """
        Execute all tests in the test suite with comprehensive reporting.

        Returns
        -------
        Dict[str, Any]
            Detailed summary of test results including:
            - total_tests
            - passed
            - failed
            - errors
            - skipped
            - total_time
            - test_details

        Raises
        ------
        OrionisTestFailureException
            If any tests fail or error occurs
        """
        self.start_time = time.time()
        if print_result:
            Console.newLine()
            Console.info("🚀 Starting Test Execution...")
            Console.newLine()

        # Setup output capture
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()

        # Execute tests
        with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
            runner = unittest.TextTestRunner(
                stream=output_buffer,
                verbosity=2,
                resultclass=self._create_custom_result_class()
            )
            result = runner.run(self.suite)

        # Process results
        execution_time = time.time() - self.start_time
        summary = self._generate_summary(result, execution_time)

        # Print captured output
        if print_result:
            self._display_results(summary, result)

        # if there are any errors or failures, raise an exception
        if not result.wasSuccessful():
            if throw_exception:
                raise OrionisTestFailureException(
                    f"{summary['failed'] + summary['errors']} test(s) failed"
                )

        # Return summary of results
        return summary

    def _create_custom_result_class(self) -> type:
        """Create a custom TestResult class to capture detailed information."""

        this = self
        class OrionisTestResult(unittest.TextTestResult):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.test_results = []

            def addSuccess(self, test):
                super().addSuccess(test)
                self.test_results.append(
                    TestResult(
                        name=str(test),
                        status=TestStatus.PASSED,
                        execution_time=0.0
                    )
                )

            def addFailure(self, test, err):
                super().addFailure(test, err)
                tb_str = ''.join(traceback.format_exception(*err))
                file_path, clean_tb = this._extract_error_info(tb_str)
                self.test_results.append(
                    TestResult(
                        name=str(test),
                        status=TestStatus.FAILED,
                        execution_time=0.0,
                        error_message=str(err[1]),
                        traceback=clean_tb,
                        file_path=file_path
                    )
                )

            def addError(self, test, err):
                super().addError(test, err)
                tb_str = ''.join(traceback.format_exception(*err))
                file_path, clean_tb = this._extract_error_info(tb_str)
                self.test_results.append(
                    TestResult(
                        name=str(test),
                        status=TestStatus.ERRORED,
                        execution_time=0.0,
                        error_message=str(err[1]),
                        traceback=clean_tb,
                        file_path=file_path
                    )
                )

            def addSkip(self, test, reason):
                super().addSkip(test, reason)
                self.test_results.append(
                    TestResult(
                        name=str(test),
                        status=TestStatus.SKIPPED,
                        execution_time=0.0,
                        error_message=reason
                    )
                )

        return OrionisTestResult

    def _generate_summary(self, result: unittest.TestResult, execution_time: float) -> Dict[str, Any]:
        """Generate a comprehensive test summary."""

        test_details = []
        for test_result in result.test_results:
            rst:dict = asdict(test_result)
            test_details.append({
                'name': rst.get('name'),
                'status': rst.get('status').name,
                'execution_time': float(rst.get('execution_time', 0)),
                'error_message': rst.get('error_message', None),
                'traceback': rst.get('traceback', None),
                'file_path': rst.get('file_path', None)
            })

        return {
            "total_tests": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "total_time": f"{execution_time:.3f} seconds",
            "success_rate": f"{((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%",
            "test_details": test_details
        }

    def _display_results(self, summary: Dict[str, Any], result: unittest.TestResult) -> None:
        """Display test results in a formatted manner."""
        # Summary table
        Console.table(
            headers=["Total", "Passed", "Failed", "Errors", "Skipped", "Duration", "Success Rate"],
            rows=[[
                summary["total_tests"],
                summary["passed"],
                summary["failed"],
                summary["errors"],
                summary["skipped"],
                summary["total_time"],
                summary["success_rate"]
            ]]
        )
        Console.newLine()

        # Detailed failure/error reporting
        if result.failures or result.errors:
            Console.textSuccessBold("Test Failures and Errors")
            for test, traceback_str in result.failures + result.errors:
                file_path, clean_tb = self._extract_error_info(traceback_str)
                title = f"❌ {test.id()}" + (f" ({file_path})" if file_path else "")
                Console.fail(title)
                Console.write(clean_tb)
                Console.newLine()

        # Performance highlights
        if len(self.test_results) > 10:
            slow_tests = sorted(
                [r for r in self.test_results if r.status == TestStatus.PASSED],
                key=lambda x: x.execution_time,
                reverse=True
            )[:3]
            if slow_tests:
                Console.textSuccessBold("⏱️ Slowest Passing Tests")
                for test in slow_tests:
                    Console.warning(f"{test.name}: {test.execution_time:.3f}s")

        # Final status
        if result.wasSuccessful():
            Console.success("✅ All tests passed successfully!")
        else:
            Console.error(
                f"❌ {summary['failed'] + summary['errors']} test(s) failed "
                f"(Success Rate: {summary['success_rate']})"
            )
        Console.newLine()