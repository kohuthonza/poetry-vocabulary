"""Prepare reviewed Wikimedia Commons file pages for the image batch helper."""

import argparse
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.parse import unquote, urlencode, urlsplit
from urllib.request import Request, urlopen


API = "https://commons.wikimedia.org/w/api.php"


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain_text(html):
    parser = _Text()
    parser.feed(html or "")
    return " ".join(unescape("".join(parser.parts)).split())


def file_title(source):
    parsed = urlsplit(source)
    if parsed.scheme != "https" or parsed.netloc != "commons.wikimedia.org":
        raise ValueError(f"Expected a Wikimedia Commons file page: {source}")
    title = unquote(parsed.path.removeprefix("/wiki/")).replace("_", " ")
    if not parsed.path.startswith("/wiki/") or not title.startswith("File:"):
        raise ValueError(f"Expected a Wikimedia Commons File: page: {source}")
    return title


def _key(title):
    return " ".join(title.replace("_", " ").split()).casefold()


def _metadata_query(titles, width):
    params = {"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
              "iiprop": "url|size|mime|extmetadata", "iiurlwidth": width, "format": "json"}
    request = Request(f"{API}?{urlencode(params)}",
                      headers={"User-Agent": "PoetryVocabulary/1.0 (educational project)"})
    for attempt in range(5):
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in {429, 503} or attempt == 4:
                raise
            time.sleep(min(10 * (attempt + 1), 60))


def prepare(items, *, width=1280, query=_metadata_query):
    """Resolve selected Commons file pages; return rows accepted by images batch."""
    if not isinstance(items, list) or not items:
        raise ValueError("Input must be a non-empty JSON array")
    if width < 1:
        raise ValueError("Width must be positive")
    titles = []
    seen_filenames = set()
    for item in items:
        if not isinstance(item, dict) or set(item) - {"filename", "source", "credit"} or not {"filename", "source"} <= set(item):
            raise ValueError("Each item needs filename and source, with optional credit")
        filename, source = item["filename"], item["source"]
        if not isinstance(filename, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*-[0-9]+\.jpg", filename):
            raise ValueError(f"Invalid image filename: {filename}")
        if filename in seen_filenames:
            raise ValueError(f"Duplicate filename: {filename}")
        seen_filenames.add(filename)
        if not isinstance(source, str):
            raise ValueError(f"{filename}: source must be a Commons file URL")
        titles.append(file_title(source))
        if "credit" in item and (not isinstance(item["credit"], str) or not item["credit"].strip()):
            raise ValueError(f"{filename}: credit must be non-empty if supplied")

    lookup = {}
    unique_titles = list(dict.fromkeys(titles))
    for start in range(0, len(unique_titles), 25):
        response = query(unique_titles[start:start + 25], width)
        for page in response.get("query", {}).get("pages", {}).values():
            info = next(iter(page.get("imageinfo", [])), None)
            if info:
                lookup[_key(page["title"])] = info

    output = []
    for item, title in zip(items, titles):
        filename = item["filename"]
        info = lookup.get(_key(title))
        if not info:
            raise ValueError(f"{filename}: no Commons image metadata for {title}")
        if info.get("mime") != "image/jpeg":
            raise ValueError(f"{filename}: Commons file is {info.get('mime')}, not JPEG")
        url = info.get("thumburl") or info.get("url")
        if not url or urlsplit(url).scheme != "https":
            raise ValueError(f"{filename}: missing HTTPS image URL")
        meta = info.get("extmetadata", {})
        artist = plain_text(meta.get("Artist", {}).get("value"))
        licence = plain_text(meta.get("LicenseShortName", {}).get("value"))
        credit = item.get("credit") or (f"{artist}; {licence}" if artist and licence else "")
        if not credit:
            raise ValueError(f"{filename}: supply reviewed credit; Commons artist/licence is incomplete")
        output.append({"filename": filename, "url": url,
                       "source": item["source"], "credit": credit})
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Reviewed filename/source JSON array")
    parser.add_argument("--output", required=True, help="New images.batch manifest path")
    parser.add_argument("--width", type=int, default=1280, help="Requested thumbnail width")
    args = parser.parse_args()
    try:
        prepared = prepare(json.loads(Path(args.manifest).read_text()), width=args.width)
        with Path(args.output).open("x") as destination:
            json.dump(prepared, destination, ensure_ascii=False, indent=2)
            destination.write("\n")
        print(f"{len(prepared)} image rows prepared: {args.output}")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
