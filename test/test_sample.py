import unittest
from src import calculations as calc


class TestCalculations(unittest.TestCase):

    def test_interpolate_arm(self):
        """Test fuel arm interpolation."""
        table = [[0, 1200], [10000, 1250], [20000, 1300]]

        # Test exact point
        self.assertEqual(calc.interpolate_arm(table, 10000), 1250)

        # Test interpolation
        result = calc.interpolate_arm(table, 5000)
        self.assertAlmostEqual(result, 1225, places=1)

        # Test below minimum
        self.assertEqual(calc.interpolate_arm(table, -100), 1200)

        # Test above maximum
        self.assertEqual(calc.interpolate_arm(table, 30000), 1300)

    def test_calculate_mac_percent(self):
        """Test %MAC conversion."""
        # Known values from Boeing manual
        arm = 1242.28
        mac = calc.calculate_mac_percent(arm, 1174.5, 278.5)
        self.assertAlmostEqual(mac, 24.34, places=2)

    def test_klm_index_base(self):
        """Test KLM index calculation."""
        # Boeing certified example
        dow = 170200
        arm = 1252.48
        index = calc.klm_index_base(dow, arm, 1258, 200000, 50)
        self.assertAlmostEqual(index, 45.3, places=1)

    def test_check_limits(self):
        """Test limit checking."""
        limits = {
            "MZFW_kg": 237682,
            "MTOW_kg": 351534,
            "MTW_kg": 352441,
            "MFW_kg": 167829
        }

        # Test within limits
        warnings = calc.check_limits(230000, 340000, limits)
        self.assertEqual(len(warnings), 0)

        # Test exceeding MZFW
        warnings = calc.check_limits(250000, 340000, limits)
        self.assertEqual(len(warnings), 1)
        # Check for "ZFW" in the warning message instead of "MZFW"
        self.assertIn("ZFW", warnings[0])


if __name__ == '__main__':
    unittest.main()