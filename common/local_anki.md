# Local Anki access

Use this guide with [update_src.md](update_src.md). Anki Desktop must be running with the intended profile open because AnkiConnect runs inside it.

## Interfaces and startup

Use **Codex → Anki MCP → AnkiConnect → Anki Desktop** with full read/write access. Prefer MCP; the user explicitly authorizes **direct AnkiConnect whenever an operation is unavailable through MCP or direct access is more convenient**. MCP is a convenience, not a restriction; do not ask again for this general permission or impose a read-only mode. Environment network/filesystem approvals still apply. Do not manipulate the live collection database directly or silently switch to desktop automation.

The persistent installation is `@ankimcp/anki-mcp-server@0.25.1`, under `/home/ikohut/.local/lib/node_modules`, with executable `/home/ikohut/.local/bin/ankimcp`. It does not depend on an npx cache. Existing configuration:

```toml
[mcp_servers.anki]
command = "/home/ikohut/.local/bin/ankimcp"
args = ["--stdio"]

[mcp_servers.anki.env]
ANKI_CONNECT_URL = "http://localhost:8765"
```

Start Anki, then the CLI, which normally launches MCP over stdio. Check registration with `codex mcp list`. An active session may not expose newly registered tools; a local stdio MCP client can launch the stable executable without reinstalling it. Discover only needed tools and argument schemas.

MCP is configured for both reads and writes. After changing startup arguments, restart the MCP connection or start a new CLI session to load them. An already-running server retains its previous arguments; if necessary, launch the installed executable over stdio with the configuration above. Interface access does not change the content decisions and approvals in the vocabulary workflow.

The original install command was `npm install --global --prefix /home/ikohut/.local @ankimcp/anki-mcp-server@0.25.1`. Keep it pinned unless an upgrade is requested. A persistent third-party install is not a security audit.

## Direct AnkiConnect

Use the Python 3.14 helper in `tools/common/anki.py` for routine requests and verified field updates; commands and environment settings are in [tools/README.md](../tools/README.md). Prefer reusing it to writing another temporary API wrapper. It does not replace MCP or change the approved task scope.

POST JSON to `http://localhost:8765`, e.g. `{"action":"deckNamesAndIds","version":6}`. Inspect both `result` and `error`. Use `apiReflect` to discover available actions, and installed add-on code/documentation for parameters; MCP tools need not share AnkiConnect names or argument shapes. Keep access on localhost. No key was required by the verified local connection on 2026-09-25. If authentication is subsequently required, use existing local configuration or request the missing credential without logging secrets or disabling authentication.

The installed API lacked a deck-renaming action when checked. `changeDeck` moves cards; `saveDeckConfig` changes options, not deck names. Do not replace renaming with recreate/move/delete operations implicitly. An unavailable operation may require a focused extension, prepared separately and explained before installation/restart.

## Matching and writing

1. Read live decks, relevant notes/cards and model field names. Inspect templates only when the image convention needs verification; extract the relevant renderer expression locally, never print entire templates. MCP `listDecks`, `findNotes`, `notesInfo` and media listing tools are useful. Check actual card destinations; deck existence/counts alone do not prove source completion. Consume either structured MCP results or parsed text, never both; project needed fields before exposing output. For cards, return IDs, decks and relevant scheduling metadata, not rendered question/answer HTML.
2. Find existing identifiers across the entire collection, without restricting discovery to the target deck or poet. Search batches of relevant identifiers, not a wildcard dump of the collection. Use established note IDs and exact identifiers plus context; loose search results are candidates, not automatic matches. Compare HTML-decoded displayed English Word values; quoted words/apostrophes may be stored as entities, so investigate an apparent miss with a narrowly targeted candidate search before adding a note. An existing note in another deck is normal reuse and satisfies coverage if it fits the current poem. Check for an important missing meaning; enrich the existing note only if needed, otherwise leave it unchanged. Preserve earlier meanings and extra Anki vocabulary absent from src.
3. Prepare and validate the approved content. Confirm supported actions and parameters before using `modelFieldNames`, `modelTemplates`, `canAddNotes`, `addNotes`, `updateNoteFields`, `cardsInfo` or `createDeck`. New decks must appear in the approved destination plan. New notes need the intended deck, live model name and actual field map.
4. Re-read before edits to avoid overwriting manual changes. Update notes by ID to preserve history/scheduling; add only genuinely missing notes. Preserve unrelated tags/fields. Never move existing cards or change their decks during source processing or reconciliation; target decks apply only to genuinely new cards. Do not create duplicates for a new poem or treat a different deck as an error. Do not delete duplicates, alter models/templates or reset scheduling implicitly.
5. Inspect every write result: multi/batch operations are not an all-or-nothing transaction. Save successful IDs/results to the temporary working draft. After a timeout, query before retrying. Complete vocabulary writes and verify normalized src against displayed identifiers before starting image retrieval. Leave Visual empty for unresolved new sets; preserve existing non-empty fields. After images are resolved, fill only eligible empty Visual fields and verify those attachments. Verify existing cards retain their original decks and only new cards use the planned destination; mark records processed only when their approved work is complete.

The observed model is **`5 field vocabulary`**, despite containing ten fields. Reconfirm the schema before writes:

| Content | Observed field |
|---|---|
| Identifier | `English Word` |
| Example 1 | `English Example` |
| Examples 2–5 | `English Example 2`, `English Example 3`, `English Example 4`, `English Example 5` |
| Classes | `Word Class` |
| Definitions | `English Explanation` |
| Czech meanings | `Czech Translations` |
| Stable image basename | `Visual` |

Observed Visual values are basenames such as `ed-gentian`, not cloud paths or image HTML. Inspect the live template before assuming it supports that convention or image numbers beyond 0–4. Escape HTML-sensitive vocabulary content appropriately while preserving displayed wording. Preserve every existing non-empty Visual basename when reusing or enriching a note; omit Visual from unrelated field updates. Still produce and index the current approved images normally even if that note retains an earlier basename. Only populate Visual for a new note or an existing empty field with the approved resolved set. Do not create another note or overwrite old media to display the new set. An intentional difference between the current indexed set and the retained Anki basename is not a reconciliation error.

## Local media

Resolve the active profile's directory using `getMediaDirPath` or a supported MCP equivalent. On 2026-09-25 it returned `/home/ikohut/.local/share/Anki2/kohut.jan/collection.media`; verify again for future runs instead of hardcoding a profile.

Download new images into that directory and save final JPEGs there using approved filesystem access or supported media operations such as `storeMediaFile`. Inspect the API's collision/overwrite options and returned filename; never overwrite resolved files or silently accept an unintended filename. Do not delete unrelated media. The common workflow specifies staging cleanup, naming, conversion, compact previews, reuse and durable saving.

Keep the cumulative `image_sources.md` in the poet's repository directory and update it as images are saved. Media presence does not prove a note links to it; verify Visual fields too. A current set can be complete and indexed without replacing the older basename retained by an existing note. Historical cloud destinations/manual copying are superseded. Do not create ZIPs or batch logs. The local media files and cumulative source index establish image progress; no CSV import is required.
