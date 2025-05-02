import asyncio
from inspect import iscoroutine
from typing import Any, Coroutine, TypeVar, Union
from orionis.luminate.support.async_io.contracts.async_coroutine import IAsyncCoroutine

T = TypeVar("T")

class AsyncCoroutine(IAsyncCoroutine):
    """
    A utility class for executing coroutine objects in various asynchronous and synchronous contexts.
    This class provides a static method to execute coroutine objects, handling different scenarios
    such as running within an active event loop (e.g., in Jupyter notebooks or Starlette) or in a
    synchronous context without an active event loop.

    Methods
    -------
    execute(coro: Coroutine[Any, Any, T]) -> Union[T, asyncio.Future]
        Executes the given coroutine object, adapting to the current execution context.
    """

    @staticmethod
    def execute(coro: Coroutine[Any, Any, T]) -> Union[T, asyncio.Future]:
        """
        Executes the given coroutine object, adapting to the current execution context.
        If there is an active event loop, it uses `asyncio.ensure_future` to schedule the coroutine.
        If there is no active event loop, it uses `asyncio.run` to run the coroutine directly.
        If the coroutine is already running, it returns a `Future` object that can be awaited.

        Parameters
        ----------
        coro : Coroutine[Any, Any, T]
            The coroutine object
        """
        if not iscoroutine(coro):
            raise TypeError("Expected a coroutine object.")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)

        if loop.is_running():
            return asyncio.ensure_future(coro)
        else:
            return loop.run_until_complete(coro)
