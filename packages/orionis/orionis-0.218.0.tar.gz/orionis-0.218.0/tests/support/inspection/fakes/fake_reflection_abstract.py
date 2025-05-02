from abc import ABC, abstractmethod
from typing import Callable
from functools import wraps

def decorator_example(func: Callable) -> Callable:
    """Example decorator for testing purposes.

    Parameters
    ----------
    func : Callable
        The function to be decorated

    Returns
    -------
    Callable
        The wrapped function

    Notes
    -----
    This is a simple identity decorator used for testing decorator detection.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def another_decorator(func: Callable) -> Callable:
    """Another example decorator for testing multiple decorators.

    Parameters
    ----------
    func : Callable
        The function to be decorated

    Returns
    -------
    Callable
        The wrapped function with added prefix

    Examples
    --------
    >>> @another_decorator
    ... def test(): return "hello"
    >>> test()
    'Decorated: hello'
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"Decorated: {func(*args, **kwargs)}"
    return wrapper


class FakeAbstractClass(ABC):
    """A fake abstract class for testing reflection capabilities.

    This class contains all elements needed to test ReflexionAbstract functionality:
    - Abstract methods
    - Concrete methods
    - Static methods
    - Class methods
    - Properties
    - Decorated methods
    - Type annotations
    - Protected/private methods

    Attributes
    ----------
    class_attr : str
        A class-level attribute with type annotation
    _value : float
        Protected attribute used by computed_property setter
    """

    class_attr: str = "class_value"

    @abstractmethod
    def abstract_method(self, x: int, y: int) -> int:
        """Required abstract method.

        Parameters
        ----------
        x : int
            First integer parameter
        y : int
            Second integer parameter

        Returns
        -------
        int
            The result of some operation

        Notes
        -----
        This method must be implemented by concrete subclasses.
        """
        pass

    @abstractmethod
    def another_abstract(self, text: str) -> str:
        """Another required abstract method.

        Parameters
        ----------
        text : str
            Input string to process

        Returns
        -------
        str
            Processed string result
        """
        pass

    def concrete_method(self, value: float) -> str:
        """Concrete implemented method.

        Parameters
        ----------
        value : float
            Numeric value to format

        Returns
        -------
        str
            Formatted string representation
        """
        return f"Value: {value}"

    @staticmethod
    def static_helper(flag: bool) -> str:
        """Static helper method.

        Parameters
        ----------
        flag : bool
            Boolean flag to determine output

        Returns
        -------
        str
            "Enabled" if flag is True, "Disabled" otherwise
        """
        return "Enabled" if flag else "Disabled"

    @classmethod
    def create_instance(cls) -> 'FakeAbstractClass':
        """Class method factory.

        Returns
        -------
        FakeAbstractClass
            New instance of the class

        Notes
        -----
        This cannot actually instantiate the abstract class, but serves
        as an example of a class method.
        """
        return cls()

    @property
    def computed_property(self) -> float:
        """Computed property example.

        Returns
        -------
        float
            The value of pi approximation
        """
        return 3.1416

    @computed_property.setter
    def computed_property(self, value: float):
        """Setter for computed property.

        Parameters
        ----------
        value : float
            New value to set
        """
        self._value = value

    @decorator_example
    @another_decorator
    def decorated_method(self) -> str:
        """Method with multiple decorators.

        Returns
        -------
        str
            Always returns "decorated" with decorator transformations

        Notes
        -----
        Used to test decorator inspection functionality.
        """
        return "decorated"

    def _protected_method(self) -> str:
        """Protected method (should be filtered in results).

        Returns
        -------
        str
            Constant string "protected"
        """
        return "protected"

    def __private_method(self) -> str:
        """Private method (should be filtered in results).

        Returns
        -------
        str
            Constant string "private"
        """
        return "private"