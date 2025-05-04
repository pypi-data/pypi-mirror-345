from typing import Any

class ITestStdOut:
    """
    Utility for printing debug info during tests, including caller context (file, line, method).
    """

    @staticmethod
    def print(*args: Any) -> None:
        """
        Print arguments to the console with file, line, and method of the caller.

        Parameters
        ----------
        *args : Any
            Any values to print. The first argument is ignored (typically the class or context).
        """
