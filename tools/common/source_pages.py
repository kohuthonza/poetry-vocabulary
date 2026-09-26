"""Archive approved full-poem web pages as local text for a source audit."""

import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


MAX_BYTES = 5_000_000
BLOCK_TAGS = {"article", "blockquote", "br", "div", "h1", "h2", "h3", "h4", "li", "p", "pre", "section"}


class PageText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skipped = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skipped += 1
        elif not self.skipped and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skipped = max(0, self.skipped - 1)
        elif not self.skipped and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skipped:
            self.parts.append(data)


def page_text(data, content_type, charset):
    decoded = data.decode(charset or "utf-8", errors="replace")
    if content_type == "text/plain":
        return decoded
    if content_type not in {"text/html", "application/xhtml+xml"}:
        raise ValueError(f"A full-text HTML or plain-text source is required, got {content_type}")
    parser = PageText()
    parser.feed(decoded)
    lines = [" ".join(line.split()) for line in "".join(parser.parts).splitlines()]
    return "\n".join(line for line in lines if line) + "\n"


def normalized_words(value):
    return " ".join(re.findall(r"\w+", value.casefold()))


def validate_manifest(items):
    if not isinstance(items, list) or not items:
        raise ValueError("Manifest must be a non-empty JSON array")
    headings = set()
    for position, item in enumerate(items, 1):
        if not isinstance(item, dict) or not all(isinstance(item.get(key), str) and item[key].strip()
                                                 for key in ("heading", "url", "edition")):
            raise ValueError(f"Source {position} needs heading, URL and edition/transcription identity")
        if item["heading"] in headings:
            raise ValueError(f"Duplicate heading: {item['heading']}")
        headings.add(item["heading"])
        if urlsplit(item["url"]).scheme not in {"http", "https"}:
            raise ValueError(f"Source {position} URL must use HTTP or HTTPS")
        if "match" in item and not isinstance(item["match"], str):
            raise ValueError(f"Source {position} match must be text")


def atomic_bytes(path, data):
    handle, temporary = tempfile.mkstemp(prefix=".poem_", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as file:
            file.write(data)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def archive_pages(items, output):
    """Save each source page and extracted text; return compact per-poem coverage."""
    validate_manifest(items)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "sources.json"
    manifest_bytes = (json.dumps(items, ensure_ascii=False, indent=2) + "\n").encode()
    if manifest_path.exists() and manifest_path.read_bytes() != manifest_bytes:
        raise ValueError("Existing archive uses another manifest; choose a new output directory")
    if not manifest_path.exists():
        atomic_bytes(manifest_path, manifest_bytes)
    results = []
    for number, item in enumerate(items, 1):
        raw = output / f"{number:03d}.html"
        text_path = output / f"{number:03d}.txt"
        if raw.is_file() and text_path.is_file():
            content = text_path.read_text()
            state = "cached"
        else:
            request = Request(item["url"], headers={"User-Agent": "PoetryVocabulary/1.0"})
            with urlopen(request, timeout=30) as response:
                content_type = response.headers.get_content_type()
                charset = response.headers.get_content_charset()
                data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise ValueError(f"Source {number} exceeds {MAX_BYTES} bytes")
            content = page_text(data, content_type, charset)
            if len(normalized_words(content)) < 20:
                raise ValueError(f"Source {number} has too little usable text")
            atomic_bytes(raw, data)
            atomic_bytes(text_path, content.encode())
            state = "saved"
        # A match is a retrieval check, not proof that an edition's reading is correct.
        match = item.get("match") or item["heading"].split(" - ", 1)[-1]
        found = normalized_words(match) in normalized_words(content)
        results.append({"heading": item["heading"], "text": str(text_path),
                        "state": state, "match_found": found})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        items = json.loads(args.manifest.read_text())
        results = archive_pages(items, args.output)
        for result in results:
            print(f"{result['state']} {result['text']} {'match found' if result['match_found'] else 'MATCH NEEDS REVIEW'}")
        print(f"Archived {len(results)} sources; {sum(not r['match_found'] for r in results)} need identity review")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
