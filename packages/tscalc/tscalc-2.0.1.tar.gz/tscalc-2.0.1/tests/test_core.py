import unittest
from tscalc import ToughnessSuccessCalculator

class TestToughnessSuccessCalculator(unittest.TestCase):
    def test_initialization(self):
        calculator = ToughnessSuccessCalculator()
        self.assertIsInstance(calculator, ToughnessSuccessCalculator)

if __name__ == "__main__":
    unittest.main()
