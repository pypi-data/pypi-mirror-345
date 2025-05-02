import asyncio
import logging
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")

class AsyncExecutor:
    """ Utility class to run asynchronous functions synchronously. """

    @staticmethod
    def run(callback: Coroutine[Any, Any, T]) -> T:
        """
        Runs an asynchronous coroutine in a synchronous context.

        Parameters
        ----------
        callback : Coroutine[Any, Any, T]
            The asynchronous coroutine to execute.

        Returns
        -------
        T
            The result of the coroutine execution.

        Raises
        ------
        Exception
            If the coroutine execution fails.
        """
        logging.getLogger('asyncio').setLevel(logging.WARNING)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(callback)
        except Exception as e:
            raise RuntimeError(f"Error executing coroutine: {e}") from e
