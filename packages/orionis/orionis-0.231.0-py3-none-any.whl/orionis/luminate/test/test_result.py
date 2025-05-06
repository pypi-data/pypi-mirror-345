from dataclasses import dataclass
from typing import Optional
from orionis.luminate.test.test_status import TestStatus

@dataclass
class TestResult:
    """
    Data class containing detailed information about a test result.

    Attributes
    ----------
    name : str
        The name of the test.
    status : TestStatus
        The status of the test, indicating whether it passed, failed, or was skipped.
    execution_time : float
        The time taken to execute the test, in seconds.
    error_message : str, optional
        The error message if the test failed, by default None.
    traceback : str, optional
        The traceback information if the test failed, by default None.
    file_path : str, optional
        The file path where the test is located, by default None.
    """
    name: str
    status: TestStatus
    execution_time: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    file_path: Optional[str] = None