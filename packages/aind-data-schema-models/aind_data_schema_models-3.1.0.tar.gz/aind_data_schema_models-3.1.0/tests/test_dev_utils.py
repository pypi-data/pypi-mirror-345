"""Dev utils tests"""

import unittest
from aind_data_schema_models._generators.dev_utils import to_class_name, to_class_name_underscored


class TestDevUtils(unittest.TestCase):
    """Tests for dev_utils module"""

    def test_to_class_name(self):
        """Test to class name method"""

        # Regular cases
        self.assertEqual(to_class_name("Smart SPIM"), "Smart_Spim")
        self.assertEqual(to_class_name("SmartSPIM"), "Smartspim")
        self.assertEqual(to_class_name("single-plane-ophys"), "Single_Plane_Ophys")

        # Edge cases
        self.assertEqual(to_class_name("a-b-c"), "A_B_C")  # Hyphenated
        self.assertEqual(to_class_name("_Already-Underscored"), "_Already_Underscored")

        # Check that non-alphanumeric characters are replaced with _
        self.assertEqual(to_class_name("123test"), "_123Test")  # Replace number with _
        self.assertEqual(to_class_name("#a"), "_A")  # Replace alphanumeric with _
        self.assertEqual(to_class_name("1Smart 2Spim"), "_1Smart_2Spim")  # Replace alphanumeric with _

        # Empty string
        self.assertEqual(to_class_name(""), "")

    def test_to_class_name_underscored(self):
        """Test to class name underscored method"""

        # Regular cases
        self.assertEqual(to_class_name_underscored("Smart SPIM"), "_Smart_Spim")
        self.assertEqual(to_class_name_underscored("SmartSPIM"), "_Smartspim")
        self.assertEqual(to_class_name_underscored("single-plane-ophys"), "_Single_Plane_Ophys")

        # Edge cases
        self.assertEqual(to_class_name_underscored("123test"), "_123Test")  # Starts with a number
        self.assertEqual(to_class_name_underscored("a-b-c"), "_A_B_C")  # Hyphenated
        self.assertEqual(to_class_name_underscored("_Already-Underscored"), "__Already_Underscored")
        self.assertEqual(to_class_name_underscored("#a"), "__A")  # Strip non-alphanumeric characters
        self.assertEqual(to_class_name_underscored("1Smart 2Spim"), "_1Smart_2Spim")  # Replace alphanumeric with _

        # Empty string
        self.assertEqual(to_class_name_underscored(""), "_")  # Should still return an underscore


if __name__ == "__main__":
    unittest.main()
