"""Split locally saved Franklin anthology pages into comparative poem texts."""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from tools.common.source_pages import MAX_BYTES, atomic_bytes, normalized_words
from tools.emily_dickinson.poem_sources import scope_headings


MARKER = re.compile(r"<p\b[^>]*>\s*(?:/\s*)?F(\d+)\b", re.IGNORECASE)
FIRST_CELL = re.compile(r"<table\b[^>]*>.*?<td\b[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL)
CHARSET = re.compile(rb"charset\s*=\s*['\"]?([\w-]+)", re.IGNORECASE)


class VerseText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"br", "p", "div"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"p", "div"}:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)

    def text(self):
        lines = [" ".join(line.split()) for line in "".join(self.parts).splitlines()]
        return "\n".join(line for line in lines if line) + "\n"


def extract_poems(raw):
    """Return Franklin number and verse from the first cell after each F marker."""
    if len(raw) > MAX_BYTES:
        raise ValueError("Anthology page exceeds source size limit")
    charset = CHARSET.search(raw[:4096])
    encoding = charset.group(1).decode("ascii") if charset else "utf-8"
    page = raw.decode(encoding, errors="replace")
    markers = list(MARKER.finditer(page))
    if not markers:
        raise ValueError("No Franklin poem markers found; page layout needs review")
    poems = []
    for position, marker in enumerate(markers):
        stop = markers[position + 1].start() if position + 1 < len(markers) else len(page)
        cell = FIRST_CELL.search(page, marker.end(), stop)
        if cell is None:
            raise ValueError(f"F{marker.group(1)} has no poem table")
        parser = VerseText()
        parser.feed(cell.group(1))
        lines = parser.text().splitlines()
        if len(lines) < 2:
            raise ValueError(f"F{marker.group(1)} has too little verse text")
        poems.append((int(marker.group(1)), "\n".join(lines) + "\n"))
    return poems


def split_pages(headings, pages, output, overrides=None):
    """Require one exact first-line match per heading before writing any archive file."""
    if not isinstance(pages, list) or not pages:
        raise ValueError("Pages must be a non-empty JSON array")
    overrides = overrides or {}
    if not isinstance(overrides, dict) or set(overrides) - set(headings):
        raise ValueError("Overrides must map selected headings to alternate first lines")
    if any(not isinstance(value, str) or not value.strip() for value in overrides.values()):
        raise ValueError("Each override needs a non-empty first line")
    candidates = []
    seen_urls = set()
    for position, page in enumerate(pages, 1):
        if not isinstance(page, dict) or not all(isinstance(page.get(key), str) and page[key].strip()
                                                 for key in ("path", "url", "edition")):
            raise ValueError(f"Page {position} needs path, URL and edition")
        if urlsplit(page["url"]).scheme not in {"http", "https"} or page["url"] in seen_urls:
            raise ValueError(f"Page {position} needs a unique HTTP(S) URL")
        seen_urls.add(page["url"])
        raw = Path(page["path"]).read_bytes()
        for number, verse in extract_poems(raw):
            candidates.append({"franklin": number, "verse": verse, "url": page["url"],
                               "edition": page["edition"], "local_page": str(Path(page["path"]).resolve())})
    rows = []
    used = set()
    for position, heading in enumerate(headings, 1):
        match = overrides.get(heading, heading.split(" - ", 1)[1])
        matches = [candidate for candidate in candidates
                   if normalized_words(candidate["verse"].splitlines()[0]) == normalized_words(match)]
        if len(matches) != 1:
            raise ValueError(f"{heading}: found {len(matches)} exact first-line matches; review source or override")
        candidate = matches[0]
        identity = (candidate["url"], candidate["franklin"])
        if identity in used:
            raise ValueError(f"{heading}: source poem is already assigned to another heading")
        used.add(identity)
        rows.append({"heading": heading, "url": candidate["url"], "edition": candidate["edition"],
                     "franklin": candidate["franklin"], "match": match,
                     "local_page": candidate["local_page"], "text": f"{position:03d}.txt",
                     "verse": candidate["verse"]})
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = [{key: value for key, value in row.items() if key != "verse"} for row in rows]
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    source_file = output / "sources.json"
    if source_file.exists() and source_file.read_bytes() != manifest_bytes:
        raise ValueError("Existing archive uses another source mapping; choose a new output directory")
    for row in rows:
        text_file = output / row["text"]
        if text_file.exists() and text_file.read_text() != row["verse"]:
            raise ValueError(f"Existing poem text differs: {text_file}")
    for row in rows:
        text_file = output / row["text"]
        if not text_file.exists():
            atomic_bytes(text_file, row["verse"].encode())
    if not source_file.exists():
        atomic_bytes(source_file, manifest_bytes)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fascicle", type=int, required=True)
    parser.add_argument("--src", type=Path, default=Path("emily_dickinson/src.txt"))
    parser.add_argument("--selected", type=Path, help="JSON array of approved headings")
    parser.add_argument("--pages", type=Path, required=True, help="JSON array of saved page path, URL, edition")
    parser.add_argument("--overrides", type=Path, help="JSON heading-to-first-line map for reviewed variants")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        headings = scope_headings(args.src, args.fascicle,
                                  json.loads(args.selected.read_text()) if args.selected else None)
        pages = json.loads(args.pages.read_text())
        overrides = json.loads(args.overrides.read_text()) if args.overrides else None
        rows = split_pages(headings, pages, args.output, overrides)
        for row in rows:
            print(f"{row['heading']}: F{row['franklin']} -> {args.output / row['text']}")
        print(f"Archived {len(rows)} comparative poem texts; inspect each full poem and edition")
    except (OSError, ValueError, UnicodeError, LookupError, json.JSONDecodeError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
