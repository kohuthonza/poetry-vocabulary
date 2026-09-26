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

For large responses, import the client in a script and project only the fields needed for the decision. Keep raw results in memory or a temporary file, not tool output. In particular, never print full `cardsInfo` question/answer HTML or `modelTemplates`. With MCP, consume `structuredContent` when available, otherwise parse the text payload once; do not print both representations. Search across decks using scoped identifier batches and HTML-decode fields for comparison.

Save each generated vocabulary block and successful write result promptly in a task-scoped `/tmp` JSON draft so a later turn can resume. Turn-local tool memory is not durable. These temporary drafts are not repository tracking files or approval records; remove them after verified completion. Retrieve HTML/JSON/PDF evidence into temporary files and extract bounded metadata or relevant text before returning output. Do not print raw image tags or `srcset` attributes.

## Poem source archive for the typo audit

For Dickinson, generate the mandatory deck/poem proposal from source headings, then wait for the user's scope and deck approval:

```sh
python3.14 -m tools.emily_dickinson.poem_sources status --fascicle 5
python3.14 -m tools.emily_dickinson.poem_sources plan --fascicle 5
python3.14 -m tools.emily_dickinson.poem_sources template --fascicle 5 --output /tmp/ed5-sources.json
```

Run `status` against the full fascicle before preparing the proposal. It compares exact src and processing-log headings, including likely renumbering when a title matches at a different number. Source-only headings may be genuinely new poems or intentionally log-deleted redo requests; review them against the log and live Anki. The command is read-only and never decides completion.

Fill the template only after approval. Each JSON array item needs the exact `heading`, a verified full-poem `url`, and the actual `edition` or transcription identity; an optional `match` supplies a first-line variant for the retrieval check. For an approved subset, pass `--selected /tmp/ed5-selected.json` to both commands; that file is a JSON array of exact approved headings. The downloader refuses a manifest missing any selected poem or changing their source order:

```sh
python3.14 -m tools.emily_dickinson.poem_sources fetch --fascicle 5 \
  --manifest /tmp/ed5-sources.json --output /tmp/ed5-poems
```

Each poem gets a raw `.html` page and extracted `.txt` file; `sources.json` in the temporary archive records URLs and edition labels. Completed files are reused on a resume. A first-line match only checks retrieval identity: inspect the complete local poem and its edition manually, and use the raw page when extraction obscures verse layout or typography. Then audit **all** Words and relevant Visuals before making the comprehensive typo table. Missing or unsuitable texts remain unresolved coverage, not a “no typos” finding. The generic downloader is `python3.14 -m tools.common.source_pages --manifest ... --output ...` for other poets. Keep the archive through vocabulary work and delete it after verified completion; it is not a permanent Words/Visuals database.

When a comparative Franklin anthology page contains several poems, save each approved source page once and split it locally. Supply `/tmp/ed6-pages.json` as an array of `{"path":"/tmp/f0101-0150.html","url":"https://example.org/page","edition":"Identified comparative transcription"}` objects. The path must name an existing full HTML page. After scope approval, run:

```sh
python3.14 -m tools.emily_dickinson.franklin_sources --fascicle 6 \
  --pages /tmp/ed6-pages.json --output /tmp/ed6-poems
```

Pass `--selected /tmp/ed6-selected.json` for an approved subset. If a first line differs, investigate the poem identity and pass `--overrides /tmp/ed6-matches.json` with an exact heading-to-comparative-first-line mapping; this locates a text and does not approve a source correction. The splitter refuses missing or ambiguous matches and archives each poem as `NNN.txt`, with source URL, edition, Franklin number and original page path in `sources.json`. Its parser handles the table layout used for fascicle 5; review the page layout if it reports a parsing error. Read each complete poem and compare consequential variants with the user's reading edition. A Franklin text remains comparative evidence and cannot establish a correction by itself. Keep the saved pages and archive through vocabulary work, then remove the temporary files after completion.

## Approved images

Only after approved vocabulary has been written to Anki and normalized src has been verified, select sources for the approved visual subjects. Then download:

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

For many approved images, use a temporary JSON array of `{"filename":"ed-robin-0.jpg","url":"...","source":"...","credit":"..."}` entries. Then run:

```sh
python3.14 -m tools.common.images batch --manifest /tmp/approved-images.json \
  --index emily_dickinson/image_sources.md
```

The batch command processes entries sequentially and skips only complete media/index pairs with matching provenance. It stops on a mismatch so the existing file or source row can be repaired without an unsafe redownload. Continue to review each set's contact sheet and update the index subject table/counts; the manifest is temporary.

After all approved sets are resolved, a temporary JSON array of `{"word":"robin","basename":"ed-robin"}` entries can drive exact-note attachment. Add `note_id` when already known. Check first, then apply:

```sh
python3.14 -m tools.common.visuals check --manifest /tmp/approved-visuals.json \
  --index emily_dickinson/image_sources.md
python3.14 -m tools.common.visuals apply --manifest /tmp/approved-visuals.json \
  --index emily_dickinson/image_sources.md
```

This verifies five indexed media files per set, resolves one exact English Word note per target across the collection, fills only empty Visual fields, and preserves every non-empty basename. It does not choose visual subjects or authorize attachments; use it only after the user's visual approval and vocabulary/image gates.

## Checks

```sh
python3.14 -m unittest discover -s tools/tests
```

Tests use temporary images and a fake Anki client. They do not modify the live collection or media.
