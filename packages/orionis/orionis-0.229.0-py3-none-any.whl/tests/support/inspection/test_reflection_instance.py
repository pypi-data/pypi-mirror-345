from orionis.luminate.support.inspection.reflection import Reflection
from orionis.luminate.support.inspection.reflexion_instance import ReflexionInstance
from orionis.luminate.test.test_case import TestCase
from tests.support.inspection.fakes.fake_reflection_instance import BaseFakeClass, FakeClass
import asyncio

class TestReflectionInstance(TestCase):
    """
    Unit tests for the Reflection class.
    """

    async def testReflectionInstanceExceptionValueError(self):
        """Ensure Reflection.instance raises ValueError for invalid types."""
        with self.assertRaises(ValueError):
            Reflection.instance(str)

    async def testReflectionInstance(self):
        """Verify Reflection.instance returns an instance of ReflexionInstance."""
        self.assertIsInstance(Reflection.instance(FakeClass()), ReflexionInstance)

    async def testReflectionInstanceGetClassName(self):
        """Check that getClassName returns the correct class name."""
        reflex = Reflection.instance(FakeClass())
        self.assertEqual(reflex.getClassName(), "FakeClass")

    async def testReflectionInstanceGetClass(self):
        """Ensure getClass returns the correct class."""
        reflex = Reflection.instance(FakeClass())
        self.assertEqual(reflex.getClass(), FakeClass)

    async def testReflectionInstanceGetModuleName(self):
        """Verify getModuleName returns the correct module name."""
        reflex = Reflection.instance(FakeClass())
        self.assertEqual(reflex.getModuleName(), "tests.support.inspection.fakes.fake_reflection_instance")

    async def testReflectionInstanceGetAttributes(self):
        """Check that getAttributes returns all attributes of the class."""
        reflex = Reflection.instance(FakeClass())
        attributes = reflex.getAttributes()
        self.assertTrue("public_attr" in attributes)
        self.assertTrue("_private_attr" in attributes)
        self.assertTrue("dynamic_attr" in attributes)

    async def testReflectionInstanceGetMethods(self):
        """Ensure getMethods returns all methods of the class."""
        reflex = Reflection.instance(FakeClass())
        methods = reflex.getMethods()
        self.assertTrue("instance_method" in methods)
        self.assertTrue("class_method" in methods)

    async def testReflectionInstanceGetStaticMethods(self):
        """Verify getStaticMethods returns all static methods of the class."""
        reflex = Reflection.instance(FakeClass())
        methods = reflex.getStaticMethods()
        self.assertTrue("static_method" in methods)

    async def testReflectionInstanceGetPropertyNames(self):
        """Check that getPropertyNames returns all property names."""
        reflex = Reflection.instance(FakeClass())
        properties = reflex.getPropertyNames()
        self.assertTrue("computed_property" in properties)

    async def testReflectionInstanceCallMethod(self):
        """Ensure callMethod correctly invokes a method with arguments."""
        reflex = Reflection.instance(FakeClass())
        result = reflex.callMethod("instance_method", 1, 2)
        self.assertEqual(result, 3)

    async def testReflectionInstanceGetMethodSignature(self):
        """Verify getMethodSignature returns the correct method signature."""
        reflex = Reflection.instance(FakeClass())
        signature = reflex.getMethodSignature("instance_method")
        self.assertEqual(str(signature), "(x: int, y: int) -> int")

    async def testReflectionInstanceGetDocstring(self):
        """Check that getDocstring returns the correct class docstring."""
        reflex = Reflection.instance(FakeClass())
        docstring = reflex.getDocstring()
        self.assertIn("This is a test class for ReflexionInstance", docstring)

    async def testReflectionInstanceGetBaseClasses(self):
        """Ensure getBaseClasses returns the correct base classes."""
        reflex = Reflection.instance(FakeClass())
        base_classes = reflex.getBaseClasses()
        self.assertIn(BaseFakeClass, base_classes)

    async def testReflectionInstanceIsInstanceOf(self):
        """Verify isInstanceOf checks inheritance correctly."""
        reflex = Reflection.instance(FakeClass())
        self.assertTrue(reflex.isInstanceOf(BaseFakeClass))

    async def testReflectionInstanceGetSourceCode(self):
        """Check that getSourceCode returns the class source code."""
        reflex = Reflection.instance(FakeClass())
        source_code = reflex.getSourceCode()
        self.assertIn("class FakeClass(BaseFakeClass):", source_code)

    async def testReflectionInstanceGetFileLocation(self):
        """Ensure getFileLocation returns the correct file path."""
        reflex = Reflection.instance(FakeClass())
        file_location = reflex.getFileLocation()
        self.assertIn("fake_reflection_instance.py", file_location)

    async def testReflectionInstanceGetAnnotations(self):
        """Verify getAnnotations returns the correct class annotations."""
        reflex = Reflection.instance(FakeClass())
        annotations = reflex.getAnnotations()
        self.assertEqual("{'class_attr': <class 'str'>}", str(annotations))

    async def testReflectionInstanceHasAttribute(self):
        """Check that hasAttribute correctly identifies attributes."""
        reflex = Reflection.instance(FakeClass())
        self.assertTrue(reflex.hasAttribute("public_attr"))
        self.assertFalse(reflex.hasAttribute("non_existent_attr"))

    async def testReflectionInstanceGetAttribute(self):
        """Ensure getAttribute retrieves the correct attribute value."""
        reflex = Reflection.instance(FakeClass())
        attr_value = reflex.getAttribute("public_attr")
        self.assertEqual(attr_value, 42)

    async def testReflectionInstanceGetCallableMembers(self):
        """Verify getCallableMembers returns all callable members."""
        reflex = Reflection.instance(FakeClass())
        callable_members = reflex.getCallableMembers()
        self.assertIn("instance_method", callable_members)
        self.assertIn("class_method", callable_members)
        self.assertIn("static_method", callable_members)

    async def testReflectionInstanceSetAttribute(self):
        """Check that setAttribute correctly sets a new attribute."""
        async def myMacro(cls: FakeClass, num):
            """Simulate an async function with an async sleep."""
            await asyncio.sleep(0.1)
            return cls.instance_method(10, 12) + num

        reflex = Reflection.instance(FakeClass())
        reflex.setAttribute("myMacro", myMacro)

        self.assertTrue(reflex.hasAttribute("myMacro"))

        result = await reflex.callMethod("myMacro", reflex._instance, 3)
        self.assertEqual(result, 25)

    def testReflectionInstanceGetPropertySignature(self):
        """Ensure getPropertySignature returns the correct property signature."""
        signature = Reflection.instance(FakeClass()).getPropertySignature('computed_property')
        self.assertEqual(str(signature), '(self) -> str')