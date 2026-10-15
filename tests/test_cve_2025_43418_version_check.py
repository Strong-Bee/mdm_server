import unittest

from scripts.check_cve_2025_43418 import assess_version, parse_version


class CVE202543418VersionCheckTests(unittest.TestCase):
    def test_parse_versions(self):
        self.assertEqual(parse_version("18.7.2"), (18, 7, 2))
        self.assertEqual(parse_version(" 26.1 "), (26, 1, 0))
        self.assertIsNone(parse_version("18.x"))
        self.assertIsNone(parse_version(""))

    def test_ios_18_fixed_threshold(self):
        self.assertEqual(assess_version("18.7.1").status, "UPDATE_REQUIRED")
        self.assertEqual(assess_version("18.7.2").status, "PATCH_LEVEL_MEETS_ADVISORY")
        self.assertEqual(assess_version("18.7.3").status, "PATCH_LEVEL_MEETS_ADVISORY")

    def test_ios_26_fixed_threshold(self):
        self.assertEqual(assess_version("26.0").status, "UPDATE_REQUIRED")
        self.assertEqual(assess_version("26.1").status, "PATCH_LEVEL_MEETS_ADVISORY")
        self.assertEqual(assess_version("26.2").status, "PATCH_LEVEL_MEETS_ADVISORY")

    def test_unknown_branches_are_not_assumed_safe(self):
        self.assertEqual(assess_version("17.7.10").status, "MANUAL_REVIEW_REQUIRED")
        self.assertEqual(assess_version("27.0").status, "MANUAL_REVIEW_REQUIRED")
        self.assertEqual(assess_version("not-a-version").status, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
