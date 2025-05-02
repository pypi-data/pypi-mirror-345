from orionis.luminate.support.async_io.async_coroutine import AsyncCoroutine
from orionis.luminate.test.test_case import TestCase
from tests.support.adapters.fakes.fake_dict import fake_dict

class TestsAsyncCoroutine(TestCase):

    async def testExecuteWithActiveEventLoop(self):
        """
        Test the execution of a coroutine within an active event loop.
        This test simulates a scenario where the coroutine is executed in an environment with an active event loop,
        such as a Jupyter notebook or a Starlette application.
        """
        async def sample_coroutine():
            return "Hello, World!"

        result = await AsyncCoroutine.execute(sample_coroutine())
        self.assertEqual(result, "Hello, World!")

    async def testExecuteWithoutActiveEventLoop(self):
        """
        Test the execution of a coroutine without an active event loop.
        This test simulates a scenario where the coroutine is executed in a synchronous context without an active event loop.
        """
        async def sample_coroutine():
            return "Hello, World!"
        result = await AsyncCoroutine.execute(sample_coroutine())
        self.assertEqual(result, "Hello, World!")

    async def testExecuteWithNonCoroutine(self):
        """
        Test the execution of a non-coroutine object.
        This test checks that a TypeError is raised when a non-coroutine object is passed to the execute method.
        """
        with self.assertRaises(TypeError) as context:
            AsyncCoroutine.execute("not a coroutine")