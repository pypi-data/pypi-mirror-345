import os
import sys
from orionis.luminate.console.output.console import Console
from orionis.luminate.test.contracts.test_std_out import ITestStdOut

class TestStdOut(ITestStdOut):
    """
    A utility class for printing debug information during testing. This class temporarily
    redirects the standard output and error streams to their original states to ensure
    proper console output, and provides contextual information about the file and line
    number where the print call was made.
    Methods
    -------
    print(*args)
        Prints the provided arguments to the console with contextual information
        about the file and line number of the caller. If no arguments are provided,
        the method does nothing.
    """

    def print(*args):
        """
        Prints the provided arguments to the console with contextual information
        about the file and line number of the caller. The output is formatted with
        muted text decorations for better readability.
        Parameters
        ----------
        *args : tuple
            The arguments to be printed. The first argument is ignored, and the
            remaining arguments are printed. If no arguments are provided, the
            method does nothing.
        Notes
        -----
        - The method temporarily redirects `sys.stdout` and `sys.stderr` to their
          original states (`sys.__stdout__` and `sys.__stderr__`) to ensure proper
          console output.
        - The contextual information includes the file path and line number of the
          caller, which is displayed in a muted text format.
        - After printing, the method restores the original `sys.stdout` and
          `sys.stderr` streams.
        """

        # Check if the first argument is a string and remove it from the args tuple
        if len(args) == 0:
            return

        # Change the output stream to the original stdout and stderr
        # to avoid any issues with the console output
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        # Get the file name and line number of the caller
        # using sys._getframe(1) to access the caller's frame
        _file = os.path.relpath(sys._getframe(1).f_code.co_filename, start=os.getcwd())
        _method = sys._getframe(1).f_code.co_name
        _line = sys._getframe(1).f_lineno

        # Print the contextual information and the provided arguments
        Console.textMuted(f"[Printout] File: {_file}, Line: {_line}, Method: {_method}")
        print(*args[1:], end='\n')
        Console.newLine()

        # Restore the original stdout and stderr streams
        sys.stdout = original_stdout
        sys.stderr = original_stderr