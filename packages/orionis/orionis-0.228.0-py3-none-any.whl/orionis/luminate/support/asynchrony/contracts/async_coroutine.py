import asyncio
from typing import Any, Coroutine, TypeVar, Union

T = TypeVar("T")

class IAsyncIO:
    """
    Interface for executing asynchronous coroutines.
    """

    @staticmethod
    def run(coro: Coroutine[Any, Any, T]) -> Union[T, asyncio.Future]:
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
