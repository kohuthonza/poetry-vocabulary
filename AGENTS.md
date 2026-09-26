# Vocabulary workflow

For requests to update a poet's `src.txt` into Anki, follow `common/update_src.md` and `common/local_anki.md`, then that poet's `prompts/read_src.md`, `prompts/resources.md`, `processing_log.md` and `reconciliation.md` when present.

For a small approved correction, edit the existing Anki note and src directly, read back once, and stop. Do not create fix histories, Git checkpoints, or processing-log entries for individual corrections. Correcting an imported record does not reopen its book/poem. Reconciliation files contain only active unresolved conflicts and must be completely empty when none remain. Move lasting guidance into common or poet-specific instructions, not a reconciliation history.

For new source processing, plan source records and destination decks for user confirmation before typo review; resolve typo decisions before the visual proposal; obtain visual confirmation before collecting new images and writing the approved update. Preserve approvals already given for the current scope.

Keep processing logs limited to a title, status sections, deck mappings and poem/book headings. Do not add instructions, narrative summaries, dates, counts, approval notes or fix histories. General guidance belongs in common instructions; retain only necessary poet-specific exceptions in that poet's instructions to prevent repeated false issues. Use Git diffs for changes inside records. Do not create a separate Words/Visuals tracking database. Deleting a logged heading requests a redo that reconciles existing Anki notes.

Search the whole Anki collection for existing vocabulary. A matching note in another deck is normal reuse, not a reconciliation issue. Check its meaning against the current poem; if an important meaning is missing, enrich that note in place while preserving earlier meanings, otherwise leave it unchanged. Never move existing cards or change their decks during source processing or reconciliation; destination mappings apply to new cards only.

Assign each selected visual to the closest vocabulary entry from the same source record, allowing capitalization, singular/plural differences and a selected word/subphrase within a longer entry. Prefer a matching standalone entry when available. Report genuinely absent terms or ambiguous matches; do not fabricate vocabulary. Ignore Dickinson's Cole painter annotations.

The user's Visuals keyword defines the image subject and new basename. The matched vocabulary entry only determines which Anki note gets the link. Do not replace the keyword with that entry's longer wording or plural form; for example robin → ed-robin attaches to crimson robin, and violet → ed-violet attaches to violets. Preserve established basenames when reusing resolved sets.

Previously visualized notes still participate in the current approved image workflow: produce the images and record them in the current poet's `image_sources.md` normally, while preserving any existing non-empty Anki Visual basename. A different existing basename is not a reconciliation problem. Reuse sets already resolved in the current image index; do not overwrite old media.

Use Anki MCP with full read/write access; do not impose a read-only restriction. Prefer MCP, with direct AnkiConnect authorized whenever an operation is unavailable through MCP or direct access is more convenient. No additional permission is needed just to choose the interface. Downloads belong in the active local Anki media directory, not the historical cloud destinations. Do not create ZIPs or batch logs; retain the cumulative image source/credit rows and inspect local media for existing files.

Existing numbered prompts are historical references and must remain until the user removes them. No active JK prompts have been defined; do not infer them from another poet or create them unless requested.
