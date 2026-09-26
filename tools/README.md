# Vocabulary tools

Run these modules from the repository root with Python 3.14. Shared code belongs in `tools/common/`. Add `tools/<poet>/` only when a reusable operation genuinely depends on that poet; source interpretation and exceptions remain in the Markdown instructions. Do not retain one-off corrections, hardcoded note IDs, batch manifests or processing histories here.

`pyproject.toml` declares Python 3.14 and pins Pillow, the only runtime dependency. Set up the environment from the repository root:

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

Only the Python packages under `tools/` are installed; poet material, instructions and tests are excluded. Future poet-specific Python packages need an `__init__.py`. For development, use `python -m pip install -e .` so code edits are reflected without reinstalling. Alternatively, `uv sync` creates an environment from the same project configuration; use `uv run python` for the commands below.

## AnkiConnect fallback

Prefer the available MCP tools. For missing operations or more convenient scripting, use the shared client:

```sh
python3.14 -m tools.common.anki call deckNamesAndIds <<<'{}'
python3.14 -m tools.common.anki call findNotes <<<'{"query":"\"English Word:robin\""}'
python3.14 -m tools.common.anki update-fields NOTE_ID --expected-word 'robin' < /tmp/approved-fields.json
```

Replace `NOTE_ID` with a live note ID. The update input is a JSON object of only the approved fields, for example `{"Visual":"ed-robin"}`. The helper checks the identifier, preserves existing non-empty Visual values, updates by ID and reads back once to verify fields, card IDs and tags. It does not move cards or change scheduling. A timeout is not automatically retried; inspect live Anki before trying again.

`call` passes any requested action and JSON parameters to AnkiConnect without adding workflow decisions. Inspect returned per-item errors/nulls for batch actions: a batch may partially succeed. Both commands use `ANKI_CONNECT_URL` (default `http://localhost:8765`) and optional `ANKI_CONNECT_KEY` from the environment. No credentials belong in the repository.

Scripts can import `AnkiConnect` from `tools.common.anki` and use `call`, `update_fields` or `media_dir`.

## Approved images

After subject/source selection and approval:

```sh
python3.14 -m tools.common.images download \
  --filename ed-robin-0.jpg \
  --url 'https://example.org/approved-photo.jpg' \
  --source 'https://example.org/source-page' \
  --credit 'Photographer; licence or explicitly unknown' \
  --index emily_dickinson/image_sources.md
python3.14 -m tools.common.images preview ed-robin --output /tmp/ed-robin-preview.jpg
```

Replace example URLs and credits with verified source information. The download command queries Anki for the active media directory, stages there, converts to RGB JPEG quality 95 without resizing, corrects EXIF orientation, puts transparency on white and refuses existing filenames or index entries. It saves a source row in the existing `Filename` table; it does not append a batch log. Keep the index's subject table and overall counts current as part of the normal workflow.

If indexing fails after an image is saved, keep that image and repair its missing source row using the original command's metadata; do not redownload or overwrite it. Run image saves sequentially for one index. Existing resolved sets should be reused without running these commands again.

The preview command checks the five numbered JPEGs, rejects identical decoded images and produces a compact contact sheet for the required visual review. It does not establish correct subjects, sufficient resolution, licences or near-duplicate views; those remain review decisions. Previews use a new output path and do not alter media. No automatic Anki attachment, image search, ZIP, processing-log edit or approval step is hidden in these helpers.

## Checks

```sh
python3.14 -m unittest discover -s tools/tests
```

Tests use temporary images and a fake Anki client. They do not modify the live collection or media.
