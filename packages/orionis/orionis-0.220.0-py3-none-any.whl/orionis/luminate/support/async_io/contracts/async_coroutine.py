import asyncio
from typing import Any, Coroutine, TypeVar, Union

T = TypeVar("T")

class IAsyncCoroutine:
    """
    Interface for executing asynchronous coroutines.

    Methods
    -------
    execute(coro: Coroutine[Any, Any, T]) -> Union[T, asyncio.Future]
        Executes the given coroutine.
    """

    @staticmethod
    def execute(coro: Coroutine[Any, Any, T]) -> Union[T, asyncio.Future]:
        """
        Execute the given coroutine.

        Parameters
        ----------
        coro : Coroutine[Any, Any, T]
            The coroutine to be executed.

        Returns
        -------
        Union[T, asyncio.Future]
            The result of the coroutine execution or a Future object.
        """
        pass
