"""Save approved images to active Anki media and make compact previews."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageOps

from tools.common.anki import AnkiConnect, AnkiError


def image_info(path):
    with Image.open(path) as image:
        image.load()
        if image.format != "JPEG" or image.mode != "RGB":
            raise ValueError(f"Expected an RGB JPEG: {path.name}")
        digest = hashlib.sha256(str(image.size).encode() + image.tobytes()).hexdigest()
        return image.size, digest


def convert_jpeg(source, destination):
    """Convert without resizing and publish atomically without overwriting."""
    destination = Path(destination)
    with Image.open(source) as original:
        source_format, original_size = original.format, original.size
        if getattr(original, "n_frames", 1) != 1:
            raise ValueError("Choose a still image, not an animation or multipage file")
        image = ImageOps.exif_transpose(original)
        if "A" in image.getbands() or "transparency" in image.info:
            rgba = image.convert("RGBA")
            image = Image.new("RGB", rgba.size, "white")
            image.paste(rgba, mask=rgba.getchannel("A"))
        else:
            image = image.convert("RGB")
        handle, temporary = tempfile.mkstemp(prefix="_poetry_jpeg_", dir=destination.parent)
        try:
            with os.fdopen(handle, "wb") as output:
                image.save(output, format="JPEG", quality=95)
            size, _ = image_info(Path(temporary))
            os.link(temporary, destination)  # Fails if the destination already exists.
        finally:
            Path(temporary).unlink(missing_ok=True)
    return source_format, original_size, size


def web_url(value):
    if urlsplit(value).scheme not in {"http", "https"}:
        raise ValueError("Image and source URLs must use HTTP or HTTPS")
    return value


def cell(value):
    return str(value).replace("|", "&#124;").replace("\n", " ").replace("\r", " ")


def link(label, url):
    return f"[{label}](<{cell(url).replace('>', '%3E').replace('<', '%3C')}>)"


def source_table_end(text):
    lines = text.splitlines(keepends=True)
    for start, line in enumerate(lines):
        if line.startswith("| Filename |"):
            end = start + 1
            while end < len(lines) and lines[end].startswith("|"):
                end += 1
            return lines, end
    raise ValueError("The index needs an existing six-column '| Filename |' source table")


def download_image(client, *, filename, url, source, credit, index):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*-[0-9]+\.jpg", filename):
        raise ValueError("Use basename-N.jpg without directories")
    web_url(url)
    web_url(source)
    if not credit.strip():
        raise ValueError("Provide source credits and known licence, or state unknown")
    index = Path(index)
    text = index.read_text()  # Require the existing cumulative index.
    source_table_end(text)  # Validate before downloading.
    directory = client.media_dir()
    destination = directory / filename
    indexed = any(line.split("|")[1].strip() == filename
                  for line in text.splitlines() if line.startswith("|") and "|" in line[1:])
    if destination.exists() or indexed:
        raise FileExistsError(f"{filename} already exists in media or index; reuse or inspect it")
    handle, temporary = tempfile.mkstemp(prefix="_poetry_download_", dir=directory)
    try:
        request = Request(url, headers={"User-Agent": "PoetryVocabulary/1.0"})
        with os.fdopen(handle, "wb") as output, urlopen(request, timeout=30) as response:
            shutil.copyfileobj(response, output)
        source_format, original_size, size = convert_jpeg(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
    orientation = "; EXIF orientation corrected" if size != original_size else ""
    row = (f"| {filename} | {size[0]} × {size[1]} | {source_format} | "
           f"{link('source', source)} | {link('image', url)} | {cell(credit)}{orientation} |\n")
    # If indexing fails, retain the finished image for recovery; never overwrite it on retry.
    lines, end = source_table_end(index.read_text())
    if lines[end - 1] and not lines[end - 1].endswith("\n"):
        lines[end - 1] += "\n"
    lines.insert(end, row)
    handle, temporary = tempfile.mkstemp(prefix=".image_sources_", dir=index.parent)
    try:
        with os.fdopen(handle, "w") as output:
            output.write("".join(lines))
        os.replace(temporary, index)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return destination


def download_batch(client, *, manifest, index):
    """Save a reviewed image manifest sequentially; resume complete file/index pairs."""
    items = json.loads(Path(manifest).read_text())
    if not isinstance(items, list) or not items:
        raise ValueError("Image manifest must be a non-empty JSON array")
    names = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {"filename", "url", "source", "credit"}:
            raise ValueError("Each image needs filename, URL, source and credit")
        filename = item["filename"]
        if not isinstance(filename, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*-[0-9]+\.jpg", filename):
            raise ValueError(f"Invalid image filename: {filename}")
        if filename in names:
            raise ValueError(f"Duplicate image filename: {filename}")
        names.add(filename)
        for key in ("url", "source"):
            if not isinstance(item[key], str):
                raise ValueError(f"{filename}: {key} must be a URL")
            web_url(item[key])
        if not isinstance(item["credit"], str) or not item["credit"].strip():
            raise ValueError(f"{filename}: credit is required")
    directory = client.media_dir()
    outcomes = []
    for item in items:
        filename = item["filename"]
        text = Path(index).read_text()
        row = next((line for line in text.splitlines()
                    if line.startswith(f"| {filename} |")), None)
        exists = (directory / filename).is_file()
        if bool(row) != exists:
            raise ValueError(f"{filename}: media/index mismatch; repair before resuming")
        if row:
            if (link("source", item["source"]) not in row or
                    link("image", item["url"]) not in row or cell(item["credit"]) not in row):
                raise ValueError(f"{filename}: saved provenance differs from manifest")
            outcomes.append((filename, "reused"))
            continue
        download_image(client, index=index, **item)
        outcomes.append((filename, "saved"))
    return outcomes


def contact_sheet(client, basename, output):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", basename):
        raise ValueError("Invalid basename")
    directory = client.media_dir()
    sheet = Image.new("RGB", (1300, 290), "white")
    draw = ImageDraw.Draw(sheet)
    hashes = set()
    for number in range(5):
        path = directory / f"{basename}-{number}.jpg"
        size, digest = image_info(path)
        if digest in hashes:
            raise ValueError(f"Duplicate image in set: {path.name}")
        hashes.add(digest)
        with Image.open(path) as image:
            image.thumbnail((250, 250))
            sheet.paste(image, (number * 260 + (250 - image.width) // 2, 30))
        draw.text((number * 260 + 5, 5), f"{number}: {size[0]} x {size[1]}", fill="black")
    with Path(output).open("xb") as target:
        sheet.save(target, format="JPEG", quality=90)
    return Path(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    download = commands.add_parser("download", help="Save one approved image and append its source row")
    for flag in ("filename", "url", "source", "credit", "index"):
        download.add_argument(f"--{flag}", required=True)
    preview = commands.add_parser("preview", help="Validate five JPEGs and create one contact sheet")
    preview.add_argument("basename")
    preview.add_argument("--output", required=True, help="New preview path, normally under /tmp")
    batch = commands.add_parser("batch", help="Save a reviewed JSON image manifest, resuming complete files")
    batch.add_argument("--manifest", required=True)
    batch.add_argument("--index", required=True)
    args = vars(parser.parse_args())
    command = args.pop("command")
    try:
        client = AnkiConnect()
        if command == "download":
            print(download_image(client, **args))
        elif command == "preview":
            print(contact_sheet(client, **args))
        else:
            result = download_batch(client, **args)
            for filename, state in result:
                print(f"{filename}: {state}")
            print(f"{sum(state == 'saved' for _, state in result)} saved, "
                  f"{sum(state == 'reused' for _, state in result)} reused")
    except (OSError, ValueError, json.JSONDecodeError, AnkiError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
