from pathlib import Path
import unittest
from scripts.validate_site import validate_site


class PublishedSiteTests(unittest.TestCase):
    def test_site_on_disk(self):
        root = Path(__file__).resolve().parents[1] / 'site'
        self.assertEqual([], validate_site(root))


if __name__ == '__main__':
    unittest.main()
