import unittest
from orionis.luminate.test.test_std_out import TestStdOut

class TestCase(unittest.IsolatedAsyncioTestCase, TestStdOut):
    """
    TestCase is a base class for unit tests that provides support for asynchronous
    testing using `unittest.IsolatedAsyncioTestCase` and additional functionality
    from `TestStdOut`."""
    async def asyncSetUp(self):
        """
        Asynchronous setup method called before each test.
        It ensures that the parent class's asyncSetUp method is invoked to initialize
        any required resources.
        """
        await super().asyncSetUp()

    async def asyncTearDown(self):
        """
        Asynchronous teardown method called after each test.
        It ensures that the parent class's asyncTearDown method is invoked to clean up
        any resources used during the test.
        """
        await super().asyncTearDown()

# Another asynchronous test case class
class AsyncTestCase(unittest.IsolatedAsyncioTestCase, TestStdOut):
    """
    AsyncTestCase is a test case class designed for asynchronous unit testing.
    It inherits from `unittest.IsolatedAsyncioTestCase` to provide support for
    async test methods and `TestStdOut` for additional functionality.
    Methods
    -------
    asyncSetUp()
        Asynchronous setup method called before each test. It ensures that the
        parent class's asyncSetUp method is invoked to initialize any required
        resources.
    asyncTearDown()
        Asynchronous teardown method called after each test. It ensures that the
        parent class's asyncTearDown method is invoked to clean up any resources
        used during the test.
    """
    async def asyncSetUp(self):
        """
        Asynchronous setup method called before each test.
        It ensures that the parent class's asyncSetUp method is invoked to initialize
        """
        await super().asyncSetUp()

    async def asyncTearDown(self):
        """
        Asynchronous teardown method called after each test.
        It ensures that the parent class's asyncTearDown method is invoked to clean up
        """
        await super().asyncTearDown()

class SyncTestCase(unittest.TestCase, TestStdOut):
    """
    SyncTestCase is a test case class designed for synchronous unit testing.
    It inherits from `unittest.TestCase` to provide support for standard test methods
    and `TestStdOut` for additional functionality.
    """
    pass