import unittest

from battery import percentage_from_voltage


class PercentageFromVoltageTest(unittest.TestCase):
    def test_maps_empty_and_full_voltage_to_percentage(self):
        self.assertEqual(percentage_from_voltage(2.8), 0)
        self.assertEqual(percentage_from_voltage(4.2), 100)

    def test_clamps_readings_outside_the_battery_range(self):
        self.assertEqual(percentage_from_voltage(2.5), 0)
        self.assertEqual(percentage_from_voltage(5.0), 100)

    def test_rounds_to_a_whole_percentage(self):
        self.assertEqual(percentage_from_voltage(3.5), 50)


if __name__ == "__main__":
    unittest.main()
