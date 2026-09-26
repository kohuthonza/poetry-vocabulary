import copy
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from tools.common.anki import AnkiConnect, AnkiError
from tools.common.images import contact_sheet, convert_jpeg, download_image


class FakeAnki(AnkiConnect):
    def __init__(self):
        self.note = {"noteId": 1, "cards": [2, 3], "tags": ["keep"], "fields": {
            "English Word": {"value": "robin"}, "Visual": {"value": ""},
            "English Explanation": {"value": "bird"}}}
        self.actions = []

    def call(self, action, **params):
        self.actions.append(action)
        if action == "notesInfo":
            return [copy.deepcopy(self.note)]
        if action == "updateNoteFields":
            for name, value in params["note"]["fields"].items():
                self.note["fields"][name]["value"] = value
            return None
        raise AssertionError(action)


class AnkiTests(unittest.TestCase):
    def test_update_preserves_other_fields_and_verifies_once(self):
        client = FakeAnki()
        client.update_fields(1, {"Visual": "ed-robin"}, expected_word="robin")
        self.assertEqual(client.note["fields"]["English Explanation"]["value"], "bird")
        self.assertEqual(client.actions, ["notesInfo", "updateNoteFields", "notesInfo"])

    def test_wrong_identifier_and_existing_visual_do_not_write(self):
        client = FakeAnki()
        with self.assertRaises(AnkiError):
            client.update_fields(1, {"Visual": "ed-robin"}, expected_word="violet")
        client.note["fields"]["Visual"]["value"] = "older-robin"
        with self.assertRaises(AnkiError):
            client.update_fields(1, {"Visual": "ed-robin"}, expected_word="robin")
        self.assertNotIn("updateNoteFields", client.actions)

    def test_server_error_is_not_retried(self):
        with patch("tools.common.anki.urlopen", return_value=BytesIO(
                b'{"result":null,"error":"blocked"}')) as request:
            with self.assertRaises(AnkiError):
                AnkiConnect().call("updateNoteFields", note={})
            self.assertEqual(request.call_count, 1)


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.client = type("Client", (), {"media_dir": lambda _: self.root})()

    def test_conversion_transparency_dimensions_and_collision(self):
        source, dest = self.root / "source.png", self.root / "test-0.jpg"
        Image.new("RGBA", (43, 29), (255, 0, 0, 0)).save(source)
        convert_jpeg(source, dest)
        with Image.open(dest) as image:
            self.assertEqual((image.mode, image.size), ("RGB", (43, 29)))
            self.assertEqual(image.getpixel((0, 0)), (255, 255, 255))
        previous = dest.read_bytes()
        with self.assertRaises(FileExistsError):
            convert_jpeg(source, dest)
        self.assertEqual(dest.read_bytes(), previous)

    def test_exif_orientation(self):
        source = self.root / "source.jpg"
        exif = Image.Exif()
        exif[274] = 6
        Image.new("RGB", (43, 29), "red").save(source, exif=exif)
        _, original, converted = convert_jpeg(source, self.root / "test-0.jpg")
        self.assertEqual((original, converted), ((43, 29), (29, 43)))

    def test_download_indexes_inside_table_and_refuses_retry(self):
        index = self.root / "image_sources.md"
        index.write_text("| Filename | Pixels | Format | Source | URL | Credit |\n"
                         "|---|---|---|---|---|---|\n\nOther material\n")
        data = BytesIO()
        Image.new("RGB", (43, 29), "red").save(data, format="PNG")
        args = dict(filename="test-0.jpg", url="https://example.org/image",
                    source="https://example.org/source", credit="Name | licence unknown", index=index)
        with patch("tools.common.images.urlopen", return_value=BytesIO(data.getvalue())):
            download_image(self.client, **args)
        text = index.read_text()
        self.assertLess(text.index("| test-0.jpg |"), text.index("Other material"))
        self.assertIn("Name &#124; licence unknown", text)
        with self.assertRaises(FileExistsError):
            download_image(self.client, **args)
        self.assertFalse(list(self.root.glob("_poetry_*")))

    def test_preview_rejects_duplicates(self):
        for number in range(5):
            Image.new("RGB", (43, 29), "red").save(self.root / f"test-{number}.jpg")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            contact_sheet(self.client, "test", self.root / "preview.jpg")
        self.assertFalse((self.root / "preview.jpg").exists())


if __name__ == "__main__":
    unittest.main()
