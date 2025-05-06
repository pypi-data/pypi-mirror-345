import os
from typing import Any, Optional, Union
from dotenv import set_key, unset_key, dotenv_values
from orionis.luminate.support.environment.contracts.env import IEnv
from orionis.luminate.support.environment.functions import (
    _initialize,
    _parse_value,
    _serialize_value,
    _delete_file
)

class Env(IEnv):
    """
    A utility class for managing environment variables stored in a `.env` file.
    """

    @staticmethod
    def get(key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieves the value of an environment variable from the `.env` file.

        Parameters
        ----------
        path : str or Path, optional
            The path to the `.env` file. If None, a default path is used.
        key : str
            The name of the environment variable to retrieve.
        default : Any, optional
            The default value to return if the variable is not found.

        Returns
        -------
        Any
            The value of the environment variable, parsed into its appropriate type,
            or the default value if the variable is not found.
        """
        resolved_path = _initialize()
        value = dotenv_values(resolved_path).get(key) or os.getenv(key)
        return _parse_value(value) if value is not None else default

    @staticmethod
    def set(key: str, value: Union[str, int, float, bool, list, dict]) -> None:
        """
        Sets the value of an environment variable in the `.env` file.

        Parameters
        ----------
        path : str or Path, optional
            The path to the `.env` file. If None, a default path is used.
        key : str
            The name of the environment variable to set.
        value : str, int, float, bool, list, or dict
            The value to assign to the environment variable. It will be serialized
            before being stored.

        Returns
        -------
        None
        """
        resolved_path = _initialize()
        serialized_value = _serialize_value(value)
        set_key(str(resolved_path), key, serialized_value)

    @staticmethod
    def unset(key: str) -> None:
        """
        Removes an environment variable from the `.env` file.

        Parameters
        ----------
        path : str or Path, optional
            The path to the `.env` file. If None, a default path is used.
        key : str
            The name of the environment variable to remove.

        Returns
        -------
        None
        """
        resolved_path = _initialize()
        unset_key(str(resolved_path), key)

    @staticmethod
    def all() -> dict:
        """
        Retrieves all environment variables from the `.env` file.

        Parameters
        ----------
        path : str or Path, optional
            The path to the `.env` file. If None, a default path is used.

        Returns
        -------
        dict
            A dictionary containing all environment variables from the `.env` file,
            with their values parsed into their appropriate types.
        """
        resolved_path = _initialize()
        env_vars = {}
        data = dotenv_values(resolved_path)

        for key, value in data.items():
            env_vars[key] = _parse_value(value)

        return env_vars

    @staticmethod
    def initialize() -> None:
        """
        Initializes the `.env` file if it does not exist.

        Parameters
        ----------
        path : str or Path, optional
            The path to the `.env` file. If None, a default path is used.

        Returns
        -------
        None
        """
        _initialize()

    @staticmethod
    def destroy() -> None:
        """
        Deletes the `.env` file.

        Parameters
        ----------
        path : str or Path, optional
            The path to the `.env` file. If None, a default path is used.

        Returns
        -------
        None
        """
        _delete_file()