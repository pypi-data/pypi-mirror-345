from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Auth:
    """
    Represents a class that holds custom properties in a dictionary.

    Attributes
    ----------
    custom : dict
        A dictionary to store any additional custom properties.
        This field is initialized with an empty dictionary by default.
    """
    custom: Dict[str, any] = field(default_factory=dict)
