# Reading the Wordsworth source

Apply [the common update workflow](../../common/update_src.md) using [resources.md](resources.md). The old `0_vocabulary.txt`, `1_normalization.txt` and `2_visualization.txt` are historical references, not three separate steps that must still be run.

## Source records and destination decks

One book block is one source record. Its first line, such as `Prelude 1805 - Book I`, is the log identity. The second line is that book's opening verse, used for context, not a vocabulary entry. There is no fascicle or other special grouping rule.

The following labels delimit sections: `Words:`, `Visuals:`, `Moods:`. Each non-empty Words line is one submitted vocabulary entry. Each non-empty Visuals line selects a visual concept. Moods and any other metadata are not vocabulary. Stop a section at the next label or book heading. Maintain one line per heading, opening verse, label or entry, with no empty lines inside a book and exactly one blank line between books.

For `Prelude 1805 - Book <ROMAN>`, convert the Roman book number to its two-digit Arabic sorting prefix and use:

`William Wordsworth::Prelude 1805 - <NN> Book <ROMAN>`

For example, Book I goes to `William Wordsworth::Prelude 1805 - 01 Book I`, Book IX to `William Wordsworth::Prelude 1805 - 09 Book IX`, and Book XIII to `William Wordsworth::Prelude 1805 - 13 Book XIII`. The live names were confirmed through MCP on 2026-09-25. The separate `Wordsworth` deck is not this parent. Do not create a new `Prelude` parent from historical names. For a different work or an unrecognized heading, propose a new routing rule rather than guessing.

Keep book order and Words order. Extra standalone vocabulary extracted into Anki is expected and must not automatically be inserted into src. Search the entire collection for repeated terms, including other books, the separate Wordsworth deck and other poets. Reuse suitable notes wherever they reside; another deck is not a reconciliation problem. Check the current passage's meaning, add an important missing meaning to the existing note if needed, otherwise leave it unchanged. Never move existing cards or change their decks. The log's destination applies to new cards only, not every shared note used by the book.

## Vocabulary and existing decisions

Use the common classification, extraction, example, semantic-alignment and capitalization rules. The historical rule based on whether a CSV already had an original example is inapplicable to new src entries.

Consult [reconciliation.md](../reconciliation.md) for prior source-to-Anki decisions and outstanding issues. Look up current note IDs in live Anki when needed. Keep `oars` in Book I Words; `oats` remains a separate cereal visual and existing note. Retain previously approved splits/expansions and `faltering at length`. Suspected errors and edition differences were explicitly retained for now. The current review in reconciliation.md is limited to highly probable typing errors; valid historical forms and wording differences are excluded. Do not treat the old generated Anki explanations as proof of a typo. A correction requires the user's decision, not silent normalization. Do not import historical counts or “next book” statements from old prompts as current progress.

## Visuals

Use prefix `ww-` and the local [image_sources.md](../image_sources.md). If a selected word already has an Anki Visual basename, still produce and index the current approved set normally, preserving the older basename in Anki. Reuse sets already resolved in this poet's index. An intentional basename difference is not a reconciliation problem; do not replace the old link or overwrite its files. The current manually selected Visuals lists replace the old instruction to scan every CSV row for visual candidates. Do not automatically expand them. Previously approved subjects, including shared sets, remain eligible subject to matching the correct meaning.

If the user explicitly asks for additional candidate suggestions, the historical preferences are animals/plants and unfamiliar concrete buildings/places; exclude abstract/figurative subjects, landscape terms, ordinary objects and familiar geographic names. Existing exceptions include tether, domestic peat-fire, and knave in the playing-card sense. These preferences do not revoke already selected/indexed visuals.

Prefer relevant Cumbrian/British specimens for those passages, and the appropriate locality for passages elsewhere; correct identification comes first. `grunsel` includes a clearly yellow-flowered common groundsel image; do not create a separate yellow-grunsel set. `knave` illustrates the jack, `peat-fire` domestic peat fuel, and `tether` the visible restraint. Keep indexed homonym choices explicit: Book X pine images illustrate the tree, although the passage uses the verb. Do not automatically attach a wrong-sense set to a new note. Existing oats imagery must never be attached to oars.

Known unresolved imported links: primrose and brood have indexed sets but had empty Visual fields at reconciliation; `faltering at length` lacked an exact note. Plan their reconciliation when those records are selected. Do not redownload their existing sets or silently declare these exceptions fixed.
