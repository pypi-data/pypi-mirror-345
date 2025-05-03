from orionis.luminate.support.adapters.dot_dict import DotDict
from orionis.luminate.test.test_case import TestCase
from tests.support.adapters.fakes.fake_dict import fake_dict

class TestsDotDict(TestCase):

    async def testAccessByDot(self):
        """
        Test the ability to access dictionary values using dot notation.
        """
        # Create a DotDict instance from the fake_dict
        dot_dict = DotDict(fake_dict)

        # Access the 'type' attribute using dot notation
        self.assertEqual(dot_dict.type, "framework")

        # Access the 'name' attribute using dot notation
        self.assertEqual(dot_dict.name, "Orionis Framework")

        # Access a nested attribute using dot notation
        self.assertEqual(dot_dict.features.authentication, True)