from typing import Any
from orionis.luminate.support.environment.env import Env

def env(key: str, default = None) -> Any:
    """
    Retrieves the value of an environment variable.

    This function provides a convenient way to access environment variables
    stored in the application context. If the variable does not exist, it
    returns the specified default value.

    Parameters
    ----------
    key : str
        The name of the environment variable to retrieve.
    default : Any, optional
        The default value to return if the environment variable does not exist.
        Defaults to None.

    Returns
    -------
    Any
        The value of the environment variable, or the default value if the variable
        does not exist.
    """
    return Env.get(key, default)