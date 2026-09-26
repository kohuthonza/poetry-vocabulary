# Reading the Dickinson source

Apply [the common update workflow](../../common/update_src.md) using [resources.md](resources.md). The existing `0_vocabulary.txt` remains a historical reference; the common workflow now provides the active pipeline and local Anki delivery.

## Record boundaries and fascicle routing

Each source record begins with `N,N,N - first line`. The numbers are **fascicle, sheet, poem order in Poems: As She Preserved Them**. They are not Franklin/Johnson numbers, vocabulary, or part of the first line used for text lookup. Split only at the initial ` - ` delimiter; preserve later dashes in the poem text.

Use the entire heading, including all three numbers and first-line text, as the processing-log identity, trimmed only at its outer edges. One poem is one log record, even when several poems share a destination. Do not use only the fascicle number or treat a whole fascicle as a single completion marker. A poem inserted anywhere remains detectable.

Only non-empty lines under Words are submitted vocabulary entries. Stop at Visuals or any next section/poem heading. Each Words line remains one entry even if it contains commas or semicolons. Ignore empty lines. Remove external markup only when clearly separate from selected wording. Visuals entries select concepts and do not create vocabulary notes. Moods, Sent, Tags and other metadata are not vocabulary. An empty Words section contributes no entries; unmatched Visuals require a report, not fabricated vocabulary.

Route **all poems of fascicle N**, regardless of sheet or poem number, to:

`Emily Dickinson::<NN> Fascicle <ROMAN>`

Here `<NN>` is the fascicle number padded to at least two digits and `<ROMAN>` is that same number in Roman numerals. Examples:

| Heading prefix | Destination |
|---|---|
| `1,*,*` | `Emily Dickinson::01 Fascicle I` |
| `2,*,*` | `Emily Dickinson::02 Fascicle II` |
| `3,*,*` | `Emily Dickinson::03 Fascicle III` |
| `4,*,*` | `Emily Dickinson::04 Fascicle IV` |
| `5,*,*` | `Emily Dickinson::05 Fascicle V` |

Before any fascicle work, show `Emily Dickinson::<NN> Fascicle <ROMAN>` as a heading with a one-column `Poem` table listing **every** selected `N,N,N - first line` heading in source order. Do this even for a single, already-known deck. Wait for explicit approval of that table and destination before the source-text download or typo audit. Preserve source poem order, including sheet order, and do not start a later fascicle just because its text exists when the user selected a smaller scope.

Before forming that table, run the read-only `poem_sources status` check for the whole fascicle. Review source-only and log-only headings, especially identical first lines under changed numbers after an insertion. A source-only heading can also be a deliberate log-deleted redo request; determine its scope from the user's request and live Anki, never from numbering alone. Then use `poem_sources plan` for the exact source-order proposal.

After approval, download a usable full text for **each** selected poem to a task-scoped local archive before claiming any typo audit is complete. Check every Words line against the downloaded poem in context, including plausible English words that may conceal a misreading of an unfamiliar word. Present all suspected corrections at once in the common workflow's three-column table. Keep the local poems available while writing vocabulary so definitions and examples reflect the actual poem, then remove the temporary archive after verified completion. Use [resources.md](resources.md) for edition/source checks; do not assert “no typos” from src alone or from partial search snippets. The ED source-list and coverage helper is described in [tools/README.md](../../tools/README.md).

## Retained exceptions

- Ignore Cole in Visuals: it is a painter reference, not a vocabulary image request, and does not prevent completion.
- Ghent remains vocabulary only; do not add it back to Visuals or create city images for it.

## Vocabulary and visuals

Search the whole collection, including other fascicles and poets, for existing vocabulary. Reuse a suitable note wherever its cards reside; another deck is not a reconciliation problem. Check the current poem's meaning, add an important missing meaning to the existing note if needed while preserving earlier meanings, otherwise leave it unchanged. Never move existing cards or change their decks. Fascicle routing and log mappings apply only to new cards.

Consult [reconciliation.md](../reconciliation.md) only for active unresolved conflicts; leave it completely empty when none remain. Use [processing_log.md](../processing_log.md) for poem/deck mappings and completion status. Unmatched selections are candidates for investigation, not permission to create duplicate notes or replace images.

Use the common rules for approved typo corrections, capitalization, five-example standard entries, empty-example excerpts, mandatory extraction, independent explanations and aligned Czech translations. Retain poem context for extracted entries and duplicate merges. Do not silently substitute another edition's wording or modernize historical forms.

Apply the same capitalization normalization to each processed Words line in src as to its displayed Anki English Word. Preserve required capitals such as I, Pleiad and Ghent; keep poem headings and other metadata unchanged. Verify vocabulary and normalized source before starting any image searches or downloads, following the common workflow's images-last order.

Only manually selected Visuals concepts qualify. Visuals normally use the singular form of a word contained in the poem's vocabulary. Assign each to the closest matching entry: prefer the same standalone word (including a relevant extracted entry), then the closest phrase containing it, allowing capitalization and singular/plural differences. For example, Robin matches crimson robin. Report actual missing terms or ambiguous matches; do not create vocabulary solely from Visuals.

Normalize Visuals labels to lowercase and use the established image-index subject label when a same-meaning alias is present, for example laurels → laurel. Keep existing basenames and media filenames unchanged. Normalize Moods labels to lowercase as well, including comma-separated mood labels. Preserve headings, metadata such as Sent, and required capitals in Words, such as Pleiad and Ghent. Metadata normalization alone does not request Anki processing of later fascicles.

Use the provided Visuals keyword for each new image set and basename, independently of the matched Anki identifier: robin → ed-robin links to crimson robin, and violet → ed-violet links to violets. The vocabulary identifier must not replace or expand the Visuals keyword in proposals or image naming.

Use prefix `ed-` and the local [image_sources.md](../image_sources.md). If a selected word already has an Anki Visual basename, still produce and index the current approved set normally, preserving the older basename in Anki. Reuse sets already resolved in this poet's index. An intentional basename difference is not a reconciliation problem; do not replace the old link or overwrite its files. Preserve its established basenames, same-meaning aliases and representative subjects. Prefer appropriate Amherst/Massachusetts/New England species when consistent with the term; never substitute a local species for a distinctly named one. Existing examples include Eurasian linnet, bay-laurel/victory-wreath laurel, and capuchin as a historical garment. Images are vocabulary illustrations, not identifications of the exact specimen Dickinson intended.

The shared index includes reuse across fascicles. Do not rebuild or re-download resolved sets when processing a later poem. Historical image/CSV counts are not proof that all currently selected Words, Visuals or entire fascicles have been imported.
