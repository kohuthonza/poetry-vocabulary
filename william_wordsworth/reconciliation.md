# Wordsworth source reconciliation

Prelude has been imported. The pending checks below concern individual records and do not reopen the book imports.

## Structure and scope

All 13 books in `src.txt` use `Prelude 1805 - Book <ROMAN>`, the book's opening line, then `Words:`, `Visuals:`, and `Moods:`.

Opening lines were checked against the [1805 text linked in the vocabulary prompt](https://viscomi.sites.oasis.unc.edu/viscomi/coursepack/wordsworth/Prelude1805.pdf), printed pages 1, 20, 34, 53, 67, 85, 105, 126, 150, 176, 205, 217, and 228. Opening small capitals were rendered in ordinary capitalization; footnote markers were omitted.

The original 1,488 selected Words entries became 1,490 after two approved splits. Selection order and repeated occurrences within and between books were retained. Extra vocabulary extracted into Anki was not automatically added to Words. Moods remain empty because none were supplied.

The comparison read 2,173 notes across the 13 Prelude decks through Anki MCP, plus 42 notes from targeted searches for shared source/visual terms across the collection. These are note counts, not card counts. Some words are stored outside their source book's deck; their existing identifiers were used where the match was clear. This is normal reuse, not a reconciliation problem. Existing cards retain their decks; a new poem calls only for checking contextual meaning and enriching the existing note if an important meaning is missing.

Of the 1,488 original entries, 1,469 changed: 1,356 by capitalization alone and 113 by wording, spelling, punctuation, spacing, or an approved split/expansion. Required capitals such as `I`, `Cam`, `Windermere`, and `Comates` were preserved. Historical forms were retained where present in Anki; normalized lemmas were copied where the existing mapping was clear.

The entry-by-entry conversion audit was checked before removal: all original selections had matched Anki note IDs except the explicitly retained `faltering at length` fragment in Book XI. The decisions and outstanding issues are preserved below. For future updates, inspect live Anki matches and use the book-level processing log and Git source baseline.

## User decisions applied

| Book | Original selection | Result |
|---|---|---|
| 1 | Oats | `oars` in Words; oats stays in Visuals with its cereal images. Both notes already exist in Anki. |
| 1 | Woodcocks ran along the open turf, trod the turf | Split into `woodcocks ran along the open turf` and `trod the turf`, matching the two Anki excerpts. |
| 1 | Springes, snares | Split into `springe` and `snare`. |
| 11 | Faltering at length | Retained as `faltering at length`. There is no matching Anki excerpt; standalone `falter` does not replace the selected fragment. |
| 12 | Gigantic wicker thrills | Expanded to `the voice of those in the gigantic wicker thrills throughout the region`, matching Anki. |
| 13 | We breast the ascent | Expanded to `thus did we breast the ascent`, matching Anki. |

### Retained readings

| Book | Retained source/Anki wording | Reason for exclusion |
|---|---|---|
| VI | langour | The Century Dictionary records it as an old form of languor ([entry reproduced by Wordnik](https://www.wordnik.com/words/langour)). Do not classify it as an obvious nonword or force modernization. |
| VII | dythyrambic fervour | Scholarship quotes `Dythyrambic` from Wordsworth's manuscript MS. A, 143r ([EURAMERICA article](https://www.ea.sinica.edu.tw/eu_file/140359190914.pdf)). The current spelling is not sufficient evidence of a typing error; the user's exact Oxford printing has not been checked here. |
| VI | toil abstruse | Valid English; singular/plural disagreement with the PDF's `toils` is outside this review. |
| VI | returning from the great spousal newly solemnized | Valid English; singular/plural disagreement with the PDF's `spousals` is outside this review. |
| X | voices of the hawkers in the crowd bawling | `Bawling` and the PDF's `brawling` are both valid English; leave this wording difference alone. |

Any existing Anki explanation that calls a retained historical form a misspelling is prior generated content, not independent evidence of an error. Retained historical forms should not be labelled typos solely because another edition differs.

Other mappings: Book 2 `Interveniant` now matches `intervenient`; Book 5 `Scepter shape` matches `spectre shape`, supported by the passage; Book 9 `Thrince` matches the existing `thrice` note. The supplied PDF prints `Trice` in Book 9's opening passage, so this follows Anki's identifier and meaning rather than reproducing that PDF spelling. This reconciliation is not a complete proofread or correction of Anki itself.

## Visuals and local media

For future reconciliation, an existing non-empty Anki Visual basename may intentionally differ from this poet's current indexed set. Preserve that earlier basename while producing and indexing the current approved images normally. This difference alone is not a missing link or reconciliation issue. Empty fields or actual missing files remain separate findings; this policy does not claim they have been repaired.

Visuals follow `image_sources.md`'s per-book log and subject table: 44 book-level selections covering 38 unique sets. Keywords follow its English terms, with `Cloister` lowercased. Book 12 has no recorded visuals. Shared sets remain selected in every book recorded by the index, even when the note resides elsewhere in Anki.

The MCP media listing contains all 190 expected filenames: numbers 0–4 for each of the 38 basenames. This verifies presence by filename; image bytes and visual quality were not rechecked or downloaded.

Live note links agree with 36 of the 38 indexed basenames. Two discrepancies remain for the later Anki update:

| Term | Indexed basename | Live note ID | Finding |
|---|---|---|---|
| primrose | ww-primrose | 1789127271940 | Visual field is empty although all five files exist. Keep primrose in source Visuals for Books 1 and 7. |
| brood | ww-brood | 1789322261481 | Visual field is empty although all five files exist. Keep brood in source Visuals for Book 5. |

Book 10's `pine` visual deliberately illustrates the tree sense, while the passage uses the verb meaning to long sorrowfully. The existing index documents this distinction, which was preserved.

## Local workflow

See [local_anki.md](../common/local_anki.md) for the persistent MCP installation, automatic stdio startup, current scope, and local media policy. Future image additions belong in the active Anki profile's local media collection through the supported interface. Historical cloud destinations and manual ZIP/import steps are not the destination for this new workflow.

The source reconciliation did not modify historical prompt templates, Anki records or image files. The active generation workflow is now consolidated in [the common update instruction](../common/update_src.md); the remaining issues below are pending or deliberately retained.

Keep only pending questions here and remove them when resolved. Keep completed book/deck mappings in [processing_log.md](processing_log.md). Do not record a history of individual fixes.
