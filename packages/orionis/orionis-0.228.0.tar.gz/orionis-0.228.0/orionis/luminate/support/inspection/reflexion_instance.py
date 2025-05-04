from typing import Any, Type, Dict, List, Tuple, Callable, Optional
import inspect

class ReflexionInstance:
    """A reflection object encapsulating a class instance.

    Parameters
    ----------
    instance : Any
        The instance being reflected upon

    Attributes
    ----------
    _instance : Any
        The encapsulated instance
    """

    def __init__(self, instance: Any) -> None:
        """Initialize with the instance to reflect upon."""
        self._instance = instance

    def getClassName(self) -> str:
        """Get the name of the instance's class.

        Returns
        -------
        str
            The name of the class

        Examples
        --------
        >>> obj = SomeClass()
        >>> reflex = ReflexionInstance(obj)
        >>> reflex.getClassName()
        'SomeClass'
        """
        return self._instance.__class__.__name__

    def getClass(self) -> Type:
        """Get the class of the instance.

        Returns
        -------
        Type
            The class object of the instance

        Examples
        --------
        >>> reflex.getClass() is SomeClass
        True
        """
        return self._instance.__class__

    def getModuleName(self) -> str:
        """Get the name of the module where the class is defined.

        Returns
        -------
        str
            The module name

        Examples
        --------
        >>> reflex.getModuleName()
        'some_module'
        """
        return self._instance.__class__.__module__

    def getAttributes(self) -> Dict[str, Any]:
        """Get all attributes of the instance.

        Returns
        -------
        Dict[str, Any]
            Dictionary of attribute names and their values

        Examples
        --------
        >>> reflex.getAttributes()
        {'attr1': value1, 'attr2': value2}
        """
        return vars(self._instance)

    def getMethods(self) -> List[str]:
        """Get all method names of the instance.

        Returns
        -------
        List[str]
            List of method names

        Examples
        --------
        >>> reflex.getMethods()
        ['method1', 'method2']
        """
        return [name for name, _ in inspect.getmembers(
            self._instance,
            predicate=inspect.ismethod
        )]

    def getStaticMethods(self) -> List[str]:
        """Get all static method names of the instance.

        Returns
        -------
        List[str]
            List of static method names, excluding private methods (starting with '_')

        Examples
        --------
        >>> class MyClass:
        ...     @staticmethod
        ...     def static_method(): pass
        ...     @staticmethod
        ...     def _private_static(): pass
        ...
        >>> reflex = ReflexionInstance(MyClass())
        >>> reflex.getStaticMethods()
        ['static_method']
        """
        return [
            name for name in dir(self._instance.__class__)
            if not name.startswith('_') and
            isinstance(inspect.getattr_static(self._instance.__class__, name), staticmethod)
        ]

    def getPropertyNames(self) -> List[str]:
        """Get all property names of the instance.

        Returns
        -------
        List[str]
            List of property names

        Examples
        --------
        >>> reflex.getPropertyNames()
        ['prop1', 'prop2']
        """
        return [name for name, _ in inspect.getmembers(
            self._instance.__class__,
            lambda x: isinstance(x, property)
        )]

    def callMethod(self, methodName: str, *args: Any, **kwargs: Any) -> Any:
        """Call a method on the instance.

        Parameters
        ----------
        methodName : str
            Name of the method to call
        *args : Any
            Positional arguments for the method
        **kwargs : Any
            Keyword arguments for the method

        Returns
        -------
        Any
            The return value of the method

        Raises
        ------
        AttributeError
            If the method doesn't exist

        Examples
        --------
        >>> reflex.callMethod('calculate', 2, 3)
        5
        """
        method = getattr(self._instance, methodName)
        return method(*args, **kwargs)

    def getMethodSignature(self, methodName: str) -> inspect.Signature:
        """Get the signature of a method.

        Parameters
        ----------
        methodName : str
            Name of the method

        Returns
        -------
        inspect.Signature
            The method signature

        Raises
        ------
        AttributeError
            If the method doesn't exist

        Examples
        --------
        >>> sig = reflex.getMethodSignature('calculate')
        >>> str(sig)
        '(x, y)'
        """
        method = getattr(self._instance, methodName)
        if callable(method):
            return inspect.signature(method)

    def getPropertySignature(self, propertyName: str) -> inspect.Signature:
        """Get the signature of a property getter.

        Parameters
        ----------
        propertyName : str
            Name of the property

        Returns
        -------
        inspect.Signature
            The property's getter method signature

        Raises
        ------
        AttributeError
            If the property doesn't exist or is not a property

        Examples
        --------
        >>> sig = reflex.getPropertySignature('config')
        >>> str(sig)
        '(self)'
        """
        attr = getattr(type(self._instance), propertyName, None)
        if isinstance(attr, property) and attr.fget is not None:
            return inspect.signature(attr.fget)
        raise AttributeError(f"{propertyName} is not a property or doesn't have a getter.")

    def getDocstring(self) -> Optional[str]:
        """Get the docstring of the instance's class.

        Returns
        -------
        Optional[str]
            The class docstring, or None if not available

        Examples
        --------
        >>> reflex.getDocstring()
        'This class does something important.'
        """
        return self._instance.__class__.__doc__

    def getBaseClasses(self) -> Tuple[Type, ...]:
        """Get the base classes of the instance's class.

        Returns
        -------
        Tuple[Type, ...]
            Tuple of base classes

        Examples
        --------
        >>> reflex.getBaseClasses()
        (<class 'object'>,)
        """
        return self._instance.__class__.__bases__

    def isInstanceOf(self, cls: Type) -> bool:
        """Check if the instance is of a specific class.

        Parameters
        ----------
        cls : Type
            The class to check against

        Returns
        -------
        bool
            True if the instance is of the specified class

        Examples
        --------
        >>> reflex.isInstanceOf(SomeClass)
        True
        """
        return isinstance(self._instance, cls)

    def getSourceCode(self) -> Optional[str]:
        """Get the source code of the instance's class.

        Returns
        -------
        Optional[str]
            The source code if available, None otherwise

        Examples
        --------
        >>> print(reflex.getSourceCode())
        class SomeClass:
            def __init__(self):
                ...
        """
        try:
            return inspect.getsource(self._instance.__class__)
        except (TypeError, OSError):
            return None

    def getFileLocation(self) -> Optional[str]:
        """Get the file location where the class is defined.

        Returns
        -------
        Optional[str]
            The file path if available, None otherwise

        Examples
        --------
        >>> reflex.getFileLocation()
        '/path/to/module.py'
        """
        try:
            return inspect.getfile(self._instance.__class__)
        except (TypeError, OSError):
            return None

    def getAnnotations(self) -> Dict[str, Any]:
        """Get type annotations of the class.

        Returns
        -------
        Dict[str, Any]
            Dictionary of attribute names and their type annotations

        Examples
        --------
        >>> reflex.getAnnotations()
        {'name': str, 'value': int}
        """
        return self._instance.__class__.__annotations__

    def hasAttribute(self, name: str) -> bool:
        """Check if the instance has a specific attribute.

        Parameters
        ----------
        name : str
            The attribute name to check

        Returns
        -------
        bool
            True if the attribute exists

        Examples
        --------
        >>> reflex.hasAttribute('important_attr')
        True
        """
        return hasattr(self._instance, name)

    def getAttribute(self, name: str) -> Any:
        """Get an attribute value by name.

        Parameters
        ----------
        name : str
            The attribute name

        Returns
        -------
        Any
            The attribute value

        Raises
        ------
        AttributeError
            If the attribute doesn't exist

        Examples
        --------
        >>> reflex.getAttribute('count')
        42
        """
        return getattr(self._instance, name)

    def setAttribute(self, name: str, value: Any) -> None:
        """Set an attribute value.

        Parameters
        ----------
        name : str
            The attribute name
        value : Any
            The value to set

        Raises
        ------
        AttributeError
            If the attribute is read-only

        Examples
        --------
        >>> reflex.setAttribute('count', 100)
        """
        setattr(self._instance, name, value)

    def getCallableMembers(self) -> Dict[str, Callable]:
        """Get all callable members (methods) of the instance.

        Returns
        -------
        Dict[str, Callable]
            Dictionary of method names and their callable objects

        Examples
        --------
        >>> reflex.getCallableMembers()
        {'calculate': <bound method SomeClass.calculate>, ...}
        """
        return {
            name: member for name, member in inspect.getmembers(
                self._instance,
                callable
            ) if not name.startswith('__')
        }