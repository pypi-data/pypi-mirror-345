from orionis.luminate.support.environment.helper import env
from orionis.luminate.test.test_case import TestCase

class TestsEnvironmentHelper(TestCase):

    async def testGetEnvHelper(self):
        """"
        Test retrieving an environment variable using the env helper.
        """
        result = env('FRAMEWORK')
        self.assertEqual(result, 'https://github.com/orionis-framework/framework')