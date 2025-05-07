from orionis.luminate.support.asynchrony.async_io import AsyncIO
from orionis.luminate.test.test_case import TestCase

class TestsAsyncIO(TestCase):

    async def testExecuteWithActiveEventLoop(self):
        """
        Test the execution of a coroutine within an active event loop.
        This test simulates a scenario where the coroutine is executed in an environment with an active event loop,
        such as a Jupyter notebook or a Starlette application.
        """
        async def sample_coroutine():
            return "Hello, World!"

        result = await AsyncIO.run(sample_coroutine())
        self.assertEqual(result, "Hello, World!")

    def testExecuteWithoutActiveEventLoop(self):
        """
        Test the execution of a coroutine without an active event loop.
        This test simulates a scenario where the coroutine is executed in a synchronous context without an active event loop.
        """
        async def sample_coroutine():
            return "Hello, World!"

        result = AsyncIO.run(sample_coroutine())
        self.assertEqual(result, "Hello, World!")

    def testExecuteWithNonCoroutine(self):
        """
        Test the execution of a non-coroutine object.
        This test checks that a TypeError is raised when a non-coroutine object is passed to the execute method.
        """
        def sample_no_coroutine():
            return "Hello, World!"

        with self.assertRaises(TypeError):
            AsyncIO.run(sample_no_coroutine())