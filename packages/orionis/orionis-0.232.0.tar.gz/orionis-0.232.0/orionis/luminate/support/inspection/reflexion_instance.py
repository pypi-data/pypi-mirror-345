from typing import Any, Type, Dict, List, Tuple, Callable, Optional
import inspect

from orionis.luminate.support.asynchrony.async_io import AsyncIO

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
        """
        return self._instance.__class__.__name__

    def getClass(self) -> Type:
        """Get the class of the instance.

        Returns
        -------
        Type
            The class object of the instance
        """
        return self._instance.__class__

    def getModuleName(self) -> str:
        """Get the name of the module where the class is defined.

        Returns
        -------
        str
            The module name
        """
        return self._instance.__class__.__module__

    def getAttributes(self) -> Dict[str, Any]:
        """Get all attributes of the instance.

        Returns
        -------
        Dict[str, Any]
            Dictionary of attribute names and their values
        """
        return vars(self._instance)

    def getMethods(self) -> List[str]:
        """Get all method names of the instance.

        Returns
        -------
        List[str]
            List of method names
        """
        class_name = self.getClassName()
        methods = [name for name, _ in inspect.getmembers(
            self._instance,
            predicate=inspect.ismethod
        )]

        out_methods = []
        for method in methods:
            out_methods.append(method.replace(f"_{class_name}", ""))

        return out_methods

    def getProtectedMethods(self) -> List[str]:
        """Get all protected method names of the instance.

        Returns
        -------
        List[str]
            List of protected method names, excluding private methods (starting with '_')
        """
        class_name = self.getClassName()
        methods = [name for name, _ in inspect.getmembers(
            self._instance,
            predicate=inspect.ismethod
        )]

        out_methods = []
        for method in methods:
            if method.startswith("_") and not method.startswith("__") and not method.startswith(f"_{class_name}"):
                out_methods.append(method)

        return out_methods

    def getPrivateMethods(self) -> List[str]:
        """Get all private method names of the instance.

        Returns
        -------
        List[str]
            List of private method names, excluding protected methods (starting with '_')
        """
        class_name = self.getClassName()
        methods = [name for name, _ in inspect.getmembers(
            self._instance,
            predicate=inspect.ismethod
        )]

        out_methods = []
        for method in methods:
            if method.startswith(f"_{class_name}"):
                out_methods.append(method.replace(f"_{class_name}", ""))

        return out_methods

    def getAsyncMethods(self) -> List[str]:
        """
        Get all asynchronous method names of the instance that are not static methods.

        Returns
        -------
        List[str]
            List of asynchronous method names
        """
        obj = self._instance
        cls = obj if inspect.isclass(obj) else obj.__class__
        class_name = self.getClassName()
        methods = [
            name for name, func in inspect.getmembers(obj, inspect.iscoroutinefunction)
            if not isinstance(inspect.getattr_static(cls, name, None), staticmethod)
        ]

        out_methods = []
        for method in methods:
            out_methods.append(method.replace(f"_{class_name}", ""))

        return out_methods

    def getSyncMethods(self) -> List[str]:
        """
        Get all synchronous method names of the instance that are not static methods.

        Returns
        -------
        List[str]
            List of synchronous method names
        """
        obj = self._instance
        cls = obj if inspect.isclass(obj) else obj.__class__
        class_name = self.getClassName()
        methods = [
            name for name, func in inspect.getmembers(obj, predicate=inspect.ismethod)
            if not inspect.iscoroutinefunction(func) and
            not isinstance(inspect.getattr_static(cls, name, None), staticmethod)
        ]

        out_methods = []
        for method in methods:
            out_methods.append(method.replace(f"_{class_name}", ""))

        return out_methods

    def getClassMethods(self) -> List[str]:
        """Get all class method names of the instance.

        Returns
        -------
        List[str]
            List of class method names.
        """
        return [
            name for name in dir(self._instance.__class__)
            if isinstance(inspect.getattr_static(self._instance.__class__, name), classmethod)
        ]

    def getStaticMethods(self) -> List[str]:
        """Get all static method names of the instance.

        Returns
        -------
        List[str]
            List of static method names.
        """
        return [
            name for name in dir(self._instance.__class__)
            if isinstance(inspect.getattr_static(self._instance.__class__, name), staticmethod)
        ]

    def getAsyncStaticMethods(self) -> List[str]:
        """
        Get all asynchronous method names of the instance that are not static methods.

        Returns
        -------
        List[str]
            List of asynchronous method names
        """
        obj = self._instance
        cls = obj if inspect.isclass(obj) else obj.__class__
        return [
            name for name, func in inspect.getmembers(obj, inspect.iscoroutinefunction)
            if isinstance(inspect.getattr_static(cls, name, None), staticmethod)
        ]

    def getSyncStaticMethods(self) -> List[str]:
        """
        Get all synchronous static method names of the instance.

        Returns
        -------
        List[str]
            List of synchronous static method names
        """
        obj = self._instance
        cls = obj if inspect.isclass(obj) else obj.__class__
        return [
            name for name, func in inspect.getmembers(cls, inspect.isfunction)
            if not inspect.iscoroutinefunction(func) and
            isinstance(inspect.getattr_static(cls, name, None), staticmethod)
        ]

    def getPropertyNames(self) -> List[str]:
        """Get all property names of the instance.

        Returns
        -------
        List[str]
            List of property names
        """
        return [name for name, _ in inspect.getmembers(
            self._instance.__class__,
            lambda x: isinstance(x, property)
        )]

    def getProperty(self, propertyName: str) -> Any:
        """Get the value of a property.

        Parameters
        ----------
        propertyName : str
            Name of the property

        Returns
        -------
        Any
            The value of the property

        Raises
        ------
        AttributeError
            If the property doesn't exist or is not a property
        """
        attr = getattr(self._instance.__class__, propertyName, None)
        if isinstance(attr, property) and attr.fget is not None:
            return getattr(self._instance, propertyName)
        raise AttributeError(f"{propertyName} is not a property or doesn't have a getter.")

    def getPropertySignature(self, propertyName: str) -> inspect.Signature:
        """Get the signature of a property.

        Parameters
        ----------
        propertyName : str
            Name of the property

        Returns
        -------
        inspect.Signature
            The property signature

        Raises
        ------
        AttributeError
            If the property doesn't exist or is not a property
        """
        attr = getattr(self._instance.__class__, propertyName, None)
        if isinstance(attr, property) and attr.fget is not None:
            return inspect.signature(attr.fget)
        raise AttributeError(f"{propertyName} is not a property or doesn't have a getter.")

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
            The result of the method call

        Raises
        ------
        AttributeError
            If the method does not exist on the instance
        TypeError
            If the method is not callable
        """

        if methodName in self.getPrivateMethods():
            methodName = f"_{self.getClassName()}{methodName}"

        method = getattr(self._instance, methodName, None)

        if method is None:
            raise AttributeError(f"'{self.getClassName()}' object has no method '{methodName}'.")
        if not callable(method):
            raise TypeError(f"'{methodName}' is not callable on '{self.getClassName()}'.")

        if inspect.iscoroutinefunction(method):
            return AsyncIO.run(method(*args, **kwargs))

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
        """
        if methodName in self.getPrivateMethods():
            methodName = f"_{self.getClassName()}{methodName}"

        method = getattr(self._instance, methodName)
        if callable(method):
            return inspect.signature(method)

    def getDocstring(self) -> Optional[str]:
        """Get the docstring of the instance's class.

        Returns
        -------
        Optional[str]
            The class docstring, or None if not available
        """
        return self._instance.__class__.__doc__

    def getBaseClasses(self) -> Tuple[Type, ...]:
        """Get the base classes of the instance's class.

        Returns
        -------
        Tuple[Type, ...]
            Tuple of base classes
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
        """
        return isinstance(self._instance, cls)

    def getSourceCode(self) -> Optional[str]:
        """Get the source code of the instance's class.

        Returns
        -------
        Optional[str]
            The source code if available, None otherwise
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
        """
        if callable(value):
            raise AttributeError(f"Cannot set attribute '{name}' to a callable.")
        setattr(self._instance, name, value)

    def removeAttribute(self, name: str) -> None:
        """Remove an attribute from the instance.

        Parameters
        ----------
        name : str
            The attribute name to remove

        Raises
        ------
        AttributeError
            If the attribute doesn't exist or is read-only
        """
        if not hasattr(self._instance, name):
            raise AttributeError(f"'{self.getClassName()}' object has no attribute '{name}'.")
        delattr(self._instance, name)

    def setMacro(self, name: str, value: Callable) -> None:
        """Set a callable attribute value.

        Parameters
        ----------
        name : str
            The attribute name
        value : Callable
            The callable to set

        Raises
        ------
        AttributeError
            If the value is not callable
        """
        if not callable(value):
            raise AttributeError(f"The value for '{name}' must be a callable.")
        setattr(self._instance, name, value)

    def removeMacro(self, name: str) -> None:
        """Remove a callable attribute from the instance.

        Parameters
        ----------
        name : str
            The attribute name to remove

        Raises
        ------
        AttributeError
            If the attribute doesn't exist or is not callable
        """
        if not hasattr(self._instance, name) or not callable(getattr(self._instance, name)):
            raise AttributeError(f"'{self.getClassName()}' object has no callable macro '{name}'.")
        delattr(self._instance, name)