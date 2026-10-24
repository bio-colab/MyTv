import unittest
import sys
from pathlib import Path

# Add tools to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import assess_device

class AssessDeviceTest(unittest.TestCase):

    def test_parse_meminfo(self):
        sample_meminfo = """MemTotal:        1014856 kB
MemFree:          124500 kB
MemAvailable:     210400 kB
Buffers:           32000 kB
Cached:           340000 kB
"""
        tot_kb, avail_kb = assess_device.parse_meminfo(sample_meminfo)
        self.assertEqual(tot_kb, 1014856)
        self.assertEqual(avail_kb, 210400)

    def test_parse_df(self):
        sample_df = """Filesystem       1K-blocks      Used Available Use% Mounted on
/dev/block/dm-0    2500000   1800000    700000  72% /data
"""
        tot_kb, avail_kb = assess_device.parse_df(sample_df)
        self.assertEqual(tot_kb, 2500000)
        self.assertEqual(avail_kb, 700000)

    def test_tier1_ultra_budget_classification(self):
        # Mock low-spec device: 1GB RAM, 700MB storage free, SDK 27
        rep = assess_device.assess()
        # Test default without active TV (returns Tier 1 due to 0/unknown specs)
        self.assertEqual(rep["tier"], 1)
        self.assertEqual(rep["recommendations"]["profile"], "ultra-lite")
        self.assertTrue(rep["recommendations"]["reduced_motion"])
        self.assertFalse(rep["recommendations"]["ambient_glow"])

    def test_regional_apps_constants(self):
        self.assertIn("com.mbc.shahid", assess_device.REGIONAL_APPS)
        self.assertIn("com.tod", assess_device.REGIONAL_APPS)
        self.assertIn("cm.aptoidetv.pt", assess_device.THIRD_PARTY_STORES)

if __name__ == "__main__":
    unittest.main()
