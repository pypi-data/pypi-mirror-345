"""
Tests for the core functionality of Clivy.
"""

import unittest
from clivy.core import example_function, format_output

class TestCore(unittest.TestCase):
    """Test cases for core functionality."""
    
    def test_example_function(self):
        """Test the example_function."""
        result = example_function("test")
        self.assertEqual(result, "Clivy processed: test")
    
    def test_format_output(self):
        """Test the format_output function."""
        result = format_output("test", "bold")
        self.assertTrue(result.startswith("\033[1m"))
        self.assertTrue(result.endswith("\033[0m"))
        
        # Test with no style
        result = format_output("test")
        self.assertEqual(result, "test")

if __name__ == "__main__":
    unittest.main()
