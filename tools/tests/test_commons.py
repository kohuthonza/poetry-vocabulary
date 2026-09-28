import unittest

from tools.common.commons import prepare


class CommonsManifestTests(unittest.TestCase):
    def test_reviewed_file_pages_become_download_rows(self):
        rows = [{"filename": "jk-robin-0.jpg",
                 "source": "https://commons.wikimedia.org/wiki/File:Robin_on_branch.jpg"}]

        def query(titles, width):
            self.assertEqual(titles, ["File:Robin on branch.jpg"])
            self.assertEqual(width, 1280)
            return {"query": {"pages": {"123": {"title": titles[0], "imageinfo": [{
                "mime": "image/jpeg", "url": "https://upload.wikimedia.org/original.jpg",
                "thumburl": "https://upload.wikimedia.org/1280px.jpg",
                "extmetadata": {"Artist": {"value": "<a>Photographer</a>"},
                                "LicenseShortName": {"value": "CC BY-SA 4.0"}},
            }]}}}}

        self.assertEqual(prepare(rows, query=query), [{
            "filename": "jk-robin-0.jpg", "url": "https://upload.wikimedia.org/1280px.jpg",
            "source": rows[0]["source"], "credit": "Photographer; CC BY-SA 4.0",
        }])

    def test_incomplete_credit_requires_reviewed_input(self):
        rows = [{"filename": "jk-robin-0.jpg",
                 "source": "https://commons.wikimedia.org/wiki/File:Robin.jpg"}]
        response = {"query": {"pages": {"123": {"title": "File:Robin.jpg", "imageinfo": [{
            "mime": "image/jpeg", "url": "https://upload.wikimedia.org/robin.jpg",
            "extmetadata": {"Artist": {"value": "Unknown"}},
        }]}}}}
        with self.assertRaisesRegex(ValueError, "supply reviewed credit"):
            prepare(rows, query=lambda _titles, _width: response)
        rows[0]["credit"] = "Photographer unknown; licence verified on source page"
        self.assertEqual(prepare(rows, query=lambda _titles, _width: response)[0]["credit"],
                         rows[0]["credit"])


if __name__ == "__main__":
    unittest.main()
