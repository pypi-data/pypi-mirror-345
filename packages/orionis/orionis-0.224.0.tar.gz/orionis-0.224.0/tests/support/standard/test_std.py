from orionis.luminate.support.standard.std import StdClass
from orionis.luminate.test.test_case import TestCase

class TestStdClass(TestCase):

    async def testInitializationAndAccess(self):
        obj = StdClass(
            first_name='Raul',
            last_name='Uñate',
            age=31
        )
        self.assertEqual(obj.first_name, 'Raul')
        self.assertEqual(obj.age, 31)

    async def testToDictReturnsCorrectData(self):
        obj = StdClass(a=1, b=2)
        expected = {'a': 1, 'b': 2}
        self.assertEqual(obj.toDict(), expected)

    async def testUpdateAttributes(self):
        obj = StdClass()
        obj.update(foo='bar', number=42)
        self.assertEqual(obj.foo, 'bar')
        self.assertEqual(obj.number, 42)

    async def testUpdateReservedAttributeRaisesError(self):
        obj = StdClass()
        with self.assertRaises(ValueError):
            obj.update(__init__='bad')

    async def testUpdateConflictingAttributeRaisesError(self):
        obj = StdClass()
        with self.assertRaises(ValueError):
            obj.update(toDict='oops')

    async def testRemoveExistingAttributes(self):
        obj = StdClass(x=1, y=2)
        obj.remove('x')
        self.assertFalse(hasattr(obj, 'x'))
        self.assertTrue(hasattr(obj, 'y'))

    async def testRemoveNonExistingAttributeRaisesError(self):
        obj = StdClass()
        with self.assertRaises(AttributeError):
            obj.remove('not_there')

    async def testFromDictCreatesEquivalentInstance(self):
        data = {'a': 10, 'b': 20}
        obj = StdClass.from_dict(data)
        self.assertEqual(obj.toDict(), data)

    async def testReprAndStr(self):
        obj = StdClass(x=5)
        self.assertIn("StdClass", repr(obj))
        self.assertIn("'x': 5", str(obj))

    async def testEquality(self):
        a = StdClass(x=1, y=2)
        b = StdClass(x=1, y=2)
        c = StdClass(x=3)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)