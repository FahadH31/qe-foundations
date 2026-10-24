import unittest

from qe_foundations.utils.numbers import clamp, percent
from qe_foundations.utils.strings import is_valid_email, slugify


class TestUtils(unittest.TestCase):

    def test_clamp(self):
        self.assertEqual(clamp(5, 1, 10), 5)
        self.assertEqual(clamp(0, 1, 10), 1)
        self.assertEqual(clamp(15, 1, 10), 10)

    def test_percent(self):
        self.assertEqual(percent(50, 100), 50.0)
        self.assertEqual(percent(1, 4), 25.0)
        self.assertEqual(percent(10, 0), 0.0)

    def test_slugify(self):
        self.assertEqual(slugify("  Login Page: Happy Path "), "login-page-happy-path")

    def test_is_valid_email(self):
        self.assertTrue(is_valid_email("user@example.com"))
        self.assertFalse(is_valid_email("invalid-email"))

    def test_bad_input_clamp_raises(self):
        with self.assertRaises(TypeError):
            clamp("invalid", 1, 10)


if __name__ == "__main__":
    unittest.main()
