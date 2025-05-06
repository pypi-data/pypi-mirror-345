class BaseFakeClass:
    pass

class FakeClass(BaseFakeClass):
    """This is a test class for ReflexionInstance.

    Attributes
    ----------
    public_attr : int
        An example public attribute
    _private_attr : str
        An example "private" attribute
    """

    class_attr: str = "class_value"

    def __init__(self) -> None:
        self.public_attr = 42
        self._private_attr = "secret"
        self.dynamic_attr = None

    def instance_method(self, x: int, y: int) -> int:
        """Adds two numbers.

        Parameters
        ----------
        x : int
            First number
        y : int
            Second number

        Returns
        -------
        int
            The sum of x and y
        """
        return x + y

    @property
    def computed_property(self) -> str:
        """A computed property."""
        return f"Value: {self.public_attr}"

    @classmethod
    def class_method(cls) -> str:
        """A class method."""
        return f"Class attr: {cls.class_attr}"

    @staticmethod
    def static_method(text: str) -> str:
        """A static method."""
        return text.upper()

    def __private_method(self) -> str:
        """A 'private' method."""
        return "This is private"

    def _protected_method(self) -> str:
        """A 'protected' method."""
        return "This is protected"