from orionis.luminate.support.environment.env import Env
from orionis.luminate.test.test_case import TestCase

class TestsEnvironment(TestCase):

    async def testGetEnvVariable(self):
        """
        Test retrieving an environment variable from the `.env` file.
        """

        # Mock the environment setup
        Env.set('TEST_KEY', 'TEST_VALUE')

        # Test the get method
        result = Env.get('TEST_KEY')
        self.assertEqual(result, "TEST_VALUE")

        # Test with a non-existent key
        result = Env.get('NON_EXISTENT_KEY', True)
        self.assertEqual(result, True)

    async def testSetEnvVariable(self):
        """
        Test setting an environment variable in the `.env` file.
        """

        # Set the environment variable
        Env.set('TEST_KEY', 'NEW_VALUE')

        # Verify the value was set correctly
        result = Env.get('TEST_KEY')
        self.assertEqual(result, 'NEW_VALUE')

    async def testUnsetEnvVariable(self):
        """
        Test removing an environment variable from the `.env` file.
        """

        # Set and then unset the environment variable
        Env.set('TEST_KEY', "TEST_VALUE")
        Env.unset('TEST_KEY')

        # Verify the variable was removed
        result = Env.get('TEST_KEY')
        self.assertIsNone(result)

    async def test_get_all_env_variables(self):
        """
        Test retrieving all environment variables from the `.env` file.
        """

        # Mock the environment setup
        Env.set('KEY1', 'value1')
        Env.set('KEY2', 'value2')

        # Retrieve all environment variables
        result = Env.all()

        # Verify the result
        self.assertEqual(result.get('KEY1'), 'value1')
        self.assertEqual(result.get('KEY2'), 'value2')

        Env.unset('KEY1')
        Env.unset('KEY2')