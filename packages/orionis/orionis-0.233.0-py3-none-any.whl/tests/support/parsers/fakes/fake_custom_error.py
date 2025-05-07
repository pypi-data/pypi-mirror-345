class CustomError(Exception):
    """
    A custom exception class for handling errors with an optional error code.

    Parameters
    ----------
    message : str
        The error message describing the exception.
    code : int, optional
        An optional error code associated with the exception (default is None).

    Attributes
    ----------
    code : int or None
        The error code associated with the exception, if provided.

    Examples
    --------
    >>> try:
    ...     raise CustomError("An error occurred", code=404)
    ... except CustomError as e:
    ...     print(f"Error: {e}, Code: {e.code}")
    Error: An error occurred, Code: 404
    """
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code