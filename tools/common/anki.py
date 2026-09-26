"""AnkiConnect fallback; prefer MCP when it is convenient."""

import argparse
import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen


class AnkiError(RuntimeError):
    pass


class AnkiConnect:
    def __init__(self, url=None, key=None, timeout=30):
        self.url = url or os.environ.get("ANKI_CONNECT_URL", "http://localhost:8765")
        self.key = key if key is not None else os.environ.get("ANKI_CONNECT_KEY")
        self.timeout = timeout

    def call(self, action, **params):
        payload = {"action": action, "version": 6, "params": params}
        if self.key:
            payload["key"] = self.key
        request = Request(self.url, json.dumps(payload).encode(),
                          {"Content-Type": "application/json"})
        # Never automatically retry: a failed response may follow a successful write.
        with urlopen(request, timeout=self.timeout) as response:
            result = json.load(response)
        if not isinstance(result, dict) or set(result) != {"result", "error"}:
            raise AnkiError("Unexpected AnkiConnect response")
        if result["error"] is not None:
            raise AnkiError(f"{action}: {result['error']}")
        return result["result"]

    def media_dir(self):
        directory = Path(self.call("getMediaDirPath"))
        if not directory.is_absolute() or not directory.is_dir():
            raise AnkiError("Anki returned an unavailable local media directory")
        return directory

    def update_fields(self, note_id, fields, *, expected_word):
        """Update one approved note and verify once, preserving unrelated content."""
        if not fields or not all(isinstance(v, str) for v in fields.values()):
            raise ValueError("Provide a non-empty field map with string values")
        notes = self.call("notesInfo", notes=[note_id])
        if len(notes) != 1 or notes[0].get("noteId") != note_id:
            raise AnkiError("Note not found")
        before = notes[0]
        old = {k: v["value"] for k, v in before["fields"].items()}
        if old.get("English Word") != expected_word:
            raise AnkiError("English Word changed or the wrong note was selected")
        if fields.keys() - old.keys():
            raise ValueError("Unknown note fields")
        if old.get("Visual") and fields.get("Visual", old["Visual"]) != old["Visual"]:
            raise AnkiError("Preserve the existing non-empty Visual basename")
        expected = old | fields
        if expected == old:
            return {"noteId": note_id, "changed": False}
        self.call("updateNoteFields", note={"id": note_id, "fields": fields})
        after = self.call("notesInfo", notes=[note_id])[0]
        if ({k: v["value"] for k, v in after["fields"].items()} != expected
                or after["cards"] != before["cards"]
                or after["tags"] != before["tags"]):
            raise AnkiError("Read-back mismatch; inspect the note before retrying")
        return {"noteId": note_id, "changed": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    call = commands.add_parser("call", help="Call an action; read its params as JSON from stdin")
    call.add_argument("action")
    update = commands.add_parser("update-fields", help="Read approved fields as JSON from stdin")
    update.add_argument("note_id", type=int)
    update.add_argument("--expected-word", required=True)
    args = parser.parse_args()
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("stdin must contain a JSON object")
        client = AnkiConnect()
        result = (client.call(args.action, **data) if args.command == "call" else
                  client.update_fields(args.note_id, data, expected_word=args.expected_word))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, AnkiError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
