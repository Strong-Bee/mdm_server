import unittest

from scripts.sync_ios_cves import extract_advisory_links, extract_cves


class IOSCVETests(unittest.TestCase):
    def test_extracts_cves_and_metadata(self):
        text = (
            "About the security content of iOS 17.4 and iPadOS 17.4 "
            "Released March 5, 2024 Kernel issue CVE-2024-12345 fixed. "
            "WebKit issue CVE-2024-54321 fixed."
        )
        rows = extract_cves(text, "https://support.apple.com/en-us/12345", "iOS 17.4 security content")
        self.assertEqual([row["cve"] for row in rows], ["CVE-2024-12345", "CVE-2024-54321"])
        self.assertTrue(all(row["published_date"] == "March 5, 2024" for row in rows))
        self.assertTrue(all(row["product"] == "iOS/iPadOS" for row in rows))

    def test_filters_non_apple_and_non_ios_links(self):
        html = """
        <a href="https://support.apple.com/en-us/123">About the security content of iOS 17</a>
        <a href="https://support.apple.com/en-us/456">About the security content of macOS 14</a>
        <a href="https://example.com/evil">About the security content of iPadOS 17</a>
        """
        self.assertEqual(
            extract_advisory_links(html),
            [("https://support.apple.com/en-us/123", "About the security content of iOS 17")],
        )


if __name__ == "__main__":
    unittest.main()
