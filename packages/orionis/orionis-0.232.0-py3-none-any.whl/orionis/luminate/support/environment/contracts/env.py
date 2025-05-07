from abc import ABC, abstractmethod
from typing import Any, Optional, Union

class IEnv(ABC):
    """
    Interface for a utility class to manage environment variables in a `.env` file.
    """

    @staticmethod
    @abstractmethod
    def get(key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve the value of an environment variable.

        Parameters
        ----------
        key : str
            Name of the environment variable.
        default : Any, optional
            Default value if variable is not found.

        Returns
        -------
        Any
            Parsed value or default.
        """
        pass

    @staticmethod
    @abstractmethod
    def set(key: str, value: Union[str, int, float, bool, list, dict]) -> None:
        """
        Set the value of an environment variable.

        Parameters
        ----------
        key : str
            Name of the environment variable.
        value : str, int, float, bool, list, or dict
            Value to assign, will be serialized.
        """
        pass

    @staticmethod
    @abstractmethod
    def unset(key: str) -> None:
        """
        Remove an environment variable.

        Parameters
        ----------
        key : str
            Name of the environment variable.
        """
        pass

    @staticmethod
    @abstractmethod
    def all() -> dict:
        """
        Retrieve all environment variables as a dictionary.

        Returns
        -------
        dict
            Dictionary of parsed environment variables.
        """
        pass
