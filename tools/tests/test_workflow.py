import copy
from email.message import Message
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from tools.common.images import download_batch
from tools.common.source_pages import archive_pages
from tools.common.visuals import process_visuals
from tools.emily_dickinson.franklin_sources import split_pages
from tools.emily_dickinson.poem_sources import compare_log, require_complete_scope, scope_headings


class Response(BytesIO):
    def __init__(self, data, content_type="text/html"):
        super().__init__(data)
        self.headers = Message()
        self.headers["Content-Type"] = content_type


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_ed_manifest_must_cover_every_selected_poem(self):
        src = self.root / "src.txt"
        src.write_text("4,1,1 - First poem\nWords:\nword\n4,1,2 - Second poem\nWords:\nword\n")
        headings = scope_headings(src, 4)
        self.assertEqual(len(headings), 2)
        with self.assertRaisesRegex(ValueError, "every selected poem"):
            require_complete_scope(headings, [{"heading": headings[0], "url": "https://example.org/1",
                                               "edition": "Named edition"}])

    def test_archive_downloads_full_text_and_resumes_without_network(self):
        items = [{"heading": "4,1,1 - First poem", "url": "https://example.org/poem",
                  "edition": "Named edition"}]
        html = b"<html><script>irrelevant</script><article><p>First poem</p><p>A quiet bloom.</p></article></html>"
        output = self.root / "archive"
        with patch("tools.common.source_pages.urlopen", return_value=Response(html)) as get:
            result = archive_pages(items, output)
            self.assertEqual(get.call_count, 1)
        self.assertTrue(result[0]["match_found"])
        self.assertIn("A quiet bloom.", (output / "001.txt").read_text())
        self.assertNotIn("irrelevant", (output / "001.txt").read_text())
        with patch("tools.common.source_pages.urlopen", side_effect=AssertionError("network retry")):
            self.assertEqual(archive_pages(items, output)[0]["state"], "cached")

    def test_log_check_flags_shifted_heading_without_changing_status(self):
        headings = ["5,4,1 - First poem", "5,4,2 - Missing poem", "5,4,3 - Later poem"]
        log = self.root / "log.md"
        log.write_text("## Processed\n5,4,1 - First poem\n5,4,2 - Later poem\n")
        source_only, log_only, shifted = compare_log(headings, log, 5)
        self.assertEqual(source_only, headings[1:])
        self.assertEqual(log_only, ["5,4,2 - Later poem"])
        self.assertEqual(shifted, [("5,4,2 - Later poem", "5,4,3 - Later poem")])

    def test_anthology_split_requires_reviewed_first_line_override(self):
        page = self.root / "anthology.html"
        page.write_bytes(b'<meta charset="utf-8"><P>F101<P><TABLE><TR><TD>First poem<BR>\nA quiet bloom.<BR>\nLast line.</TD></TR></TABLE>'
                         b'<P> / F102<P><TABLE><TR><TD>Later poem<BR>\nAcross the meadow.<BR>\nLast line.</TD></TR></TABLE>')
        pages = [{"path": str(page), "url": "https://example.org/anthology", "edition": "Comparative edition"}]
        headings = ["5,4,1 - First poem", "5,4,2 - Other heading"]
        output = self.root / "poems"
        with self.assertRaisesRegex(ValueError, "0 exact first-line matches"):
            split_pages(headings, pages, output)
        self.assertFalse((output / "sources.json").exists())
        rows = split_pages(headings, pages, output, {headings[1]: "Later poem"})
        self.assertEqual([row["franklin"] for row in rows], [101, 102])
        self.assertEqual((output / "002.txt").read_text().splitlines()[1], "Across the meadow.")
        self.assertEqual(rows, split_pages(headings, pages, output, {headings[1]: "Later poem"}))


class BatchImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.client = type("Client", (), {"media_dir": lambda _: self.root})()
        self.index = self.root / "image_sources.md"
        self.index.write_text("| Filename | Pixels | Format | Source | URL | Credit |\n"
                              "|---|---|---|---|---|---|\n")
        data = BytesIO()
        Image.new("RGB", (40, 30), "green").save(data, format="PNG")
        self.image = data.getvalue()
        self.manifest = self.root / "images.json"
        self.items = [{"filename": "ed-test-0.jpg", "url": "https://example.org/image.png",
                       "source": "https://example.org/poem", "credit": "Photographer; CC BY"}]
        self.manifest.write_text(json.dumps(self.items))

    def test_batch_resumes_and_rejects_media_index_mismatch(self):
        with patch("tools.common.images.urlopen", return_value=BytesIO(self.image)) as get:
            self.assertEqual(download_batch(self.client, manifest=self.manifest, index=self.index),
                             [("ed-test-0.jpg", "saved")])
            self.assertEqual(get.call_count, 1)
        with patch("tools.common.images.urlopen", side_effect=AssertionError("network retry")):
            self.assertEqual(download_batch(self.client, manifest=self.manifest, index=self.index),
                             [("ed-test-0.jpg", "reused")])
        (self.root / "ed-test-0.jpg").unlink()
        with self.assertRaisesRegex(ValueError, "media/index mismatch"):
            download_batch(self.client, manifest=self.manifest, index=self.index)


class FakeVisualClient:
    def __init__(self, media):
        self.media = media
        self.notes = {
            1: {"noteId": 1, "fields": {"English Word": {"value": "robin"}, "Visual": {"value": ""}}},
            2: {"noteId": 2, "fields": {"English Word": {"value": "daisies"}, "Visual": {"value": "ed-old-daisy"}}},
        }
        self.updates = []

    def media_dir(self):
        return self.media

    def call(self, action, **params):
        if action == "findNotes":
            return [1] if "robin" in params["query"] else [2]
        if action == "notesInfo":
            return [copy.deepcopy(self.notes[id_]) for id_ in params["notes"]]
        raise AssertionError(action)

    def update_fields(self, note_id, fields, *, expected_word):
        self.assert_word(note_id, expected_word)
        self.updates.append(note_id)
        self.notes[note_id]["fields"]["Visual"]["value"] = fields["Visual"]

    def assert_word(self, note_id, expected_word):
        if self.notes[note_id]["fields"]["English Word"]["value"] != expected_word:
            raise AssertionError("wrong word")


class VisualTests(unittest.TestCase):
    def test_attach_only_empty_visual_and_preserve_old_basename(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index = root / "index.md"
            names = [f"{base}-{i}.jpg" for base in ("ed-robin", "ed-daisy") for i in range(5)]
            index.write_text("\n".join(f"| {name} | x |" for name in names))
            for name in names:
                (root / name).touch()
            client = FakeVisualClient(root)
            items = [{"word": "robin", "basename": "ed-robin"},
                     {"word": "daisies", "basename": "ed-daisy"}]
            checked = process_visuals(client, items, index)
            self.assertEqual([row["action"] for row in checked], ["attach", "preserve"])
            process_visuals(client, items, index, apply=True)
            self.assertEqual(client.updates, [1])
            self.assertEqual(client.notes[2]["fields"]["Visual"]["value"], "ed-old-daisy")


if __name__ == "__main__":
    unittest.main()
