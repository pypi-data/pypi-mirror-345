from orionis.luminate.support.patterns.singleton import SingletonMeta
from orionis.luminate.test.test_case import TestCase

class TestsAsyncCoroutine(TestCase):

    async def testSingletonMeta(self):
        """
        Test the SingletonMeta metaclass to ensure that only one instance of a class is created.
        """
        class SingletonClass(metaclass=SingletonMeta):
            def __init__(self, value):
                self.value = value

        instance1 = SingletonClass(1)
        instance2 = SingletonClass(2)

        self.assertIs(instance1, instance2)
        self.assertEqual(instance1.value, 1)