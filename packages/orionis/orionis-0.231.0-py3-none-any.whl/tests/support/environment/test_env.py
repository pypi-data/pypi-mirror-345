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

        # Delete File .env
        Env.destroy()

    async def testSetEnvVariable(self):
        """
        Test setting an environment variable in the `.env` file.
        """

        # Set the environment variable
        Env.set('TEST_KEY', 'NEW_VALUE')

        # Verify the value was set correctly
        result = Env.get('TEST_KEY')
        self.assertEqual(result, 'NEW_VALUE')

        # Delete File .env
        Env.destroy()

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

        # Delete File .env
        Env.destroy()

    async def testGetEnvHelper(self):
        """"
        Test retrieving an environment variable using the env helper.
        """

        # Mock the environment setup
        Env.set('FRAMEWORK', 'https://github.com/orionis-framework/framework')

        # Import the env helper and retrieve the variable
        from orionis.luminate.support.environment.helper import env as get_env
        result = get_env('FRAMEWORK')

        # Verify the result
        self.assertEqual(result, 'https://github.com/orionis-framework/framework')

        # Delete File .env
        Env.destroy()

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

        # Delete File .env
        Env.destroy()