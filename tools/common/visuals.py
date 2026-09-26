"""Check and attach approved visual sets to exact Anki vocabulary notes."""

import argparse
import html
import json
from pathlib import Path
import re

from tools.common.anki import AnkiConnect, AnkiError


def displayed(value):
    return html.unescape(re.sub(r"<[^>]*>", "", value))


def validate_targets(items):
    if not isinstance(items, list) or not items:
        raise ValueError("Visual manifest must be a non-empty JSON array")
    words = set()
    for item in items:
        if not isinstance(item, dict) or set(item) - {"word", "basename", "note_id"}:
            raise ValueError("Each target needs word and basename, with optional note_id")
        word, basename = item.get("word"), item.get("basename")
        if not isinstance(word, str) or not word or not isinstance(basename, str):
            raise ValueError("Each target needs a non-empty word and basename")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", basename):
            raise ValueError(f"Invalid basename: {basename}")
        if word in words:
            raise ValueError(f"Duplicate target: {word}")
        words.add(word)
        if "note_id" in item and (not isinstance(item["note_id"], int) or item["note_id"] <= 0):
            raise ValueError(f"Invalid note_id for {word}")


def check_sets(client, basenames, index):
    rows = Path(index).read_text().splitlines()
    media = client.media_dir()
    for basename in basenames:
        for number in range(5):
            filename = f"{basename}-{number}.jpg"
            if sum(row.startswith(f"| {filename} |") for row in rows) != 1:
                raise ValueError(f"Missing or duplicate source-index row: {filename}")
            if not (media / filename).is_file():
                raise ValueError(f"Missing Anki media file: {filename}")


def resolve_targets(client, items):
    resolved = []
    for item in items:
        word = item["word"]
        if "note_id" in item:
            ids = [item["note_id"]]
        else:
            escaped = word.replace("\\", "\\\\").replace('"', '\\"')
            ids = client.call("findNotes", query=f'"English Word:{escaped}"')
        candidates = client.call("notesInfo", notes=ids)
        exact = [note for note in candidates if displayed(note["fields"]["English Word"]["value"]) == word]
        if len(exact) != 1:
            raise ValueError(f"{word}: expected one exact Anki note, found {len(exact)}")
        note = exact[0]
        current = note["fields"]["Visual"]["value"]
        resolved.append({"word": word, "id": note["noteId"], "raw_word": note["fields"]["English Word"]["value"],
                         "current": current, "basename": item["basename"],
                         "action": "attach" if not current else "already" if current == item["basename"] else "preserve"})
    return resolved


def process_visuals(client, items, index, *, apply=False):
    validate_targets(items)
    check_sets(client, {item["basename"] for item in items}, index)
    resolved = resolve_targets(client, items)
    if apply:
        for row in resolved:
            if row["action"] == "attach":
                client.update_fields(row["id"], {"Visual": row["basename"]}, expected_word=row["raw_word"])
    return resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "apply"))
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    args = parser.parse_args()
    try:
        items = json.loads(args.manifest.read_text())
        resolved = process_visuals(AnkiConnect(), items, args.index, apply=args.command == "apply")
        for row in resolved:
            print(f"{row['word']}: {row['id']} {row['action']} "
                  f"{row['current'] or '(empty)'} -> {row['basename']}")
    except (OSError, ValueError, json.JSONDecodeError, AnkiError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
