import tempfile
import unittest
from pathlib import Path
from met_pipeline import atomic_write, eligible


class DataContractTests(unittest.TestCase):
    def test_restricted_image_is_excluded(self):
        self.assertFalse(eligible({"isPublicDomain": False, "primaryImage": "image.jpg"}))

    def test_missing_image_is_excluded(self):
        self.assertFalse(eligible({"isPublicDomain": True, "primaryImage": ""}))

    def test_public_image_is_included(self):
        self.assertTrue(eligible({"isPublicDomain": True, "primaryImageSmall": "image.jpg"}))

    def test_unspecified_rights_are_excluded(self):
        self.assertFalse(eligible({"primaryImage": "image.jpg"}))

    def test_atomic_file_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "record.json"
            atomic_write(target, b"old")
            atomic_write(target, b"new")
            self.assertEqual(target.read_bytes(), b"new")
            self.assertFalse(target.with_suffix(".json.part").exists())


if __name__ == "__main__":
    unittest.main()
