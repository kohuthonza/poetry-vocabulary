# Reading the Keats source

Apply [the common update workflow](../../common/update_src.md) using [resources.md](resources.md). The user's initial processing prompt will specify which poems in the current `src.txt` go to which decks. Do not infer a deck from the poem title, position, date or another poet's routing rule. Before source retrieval or vocabulary work, show every selected poem under its full proposed destination deck in the common workflow's numbered `# | Poem` tables and wait for explicit scope and deck approval.

## Source records

One poem block is one source record. A block begins with either a title followed by the opening verse on the next line, or the opening verse alone when there is no title. `Words:` follows these header lines. There is no Dickinson-style numeric prefix or other structural marking. Preserve titles and opening verses exactly as supplied. Parse the whole file for block boundaries, including records inserted between existing ones; blank lines separate populated blocks but are not completion markers.

Use the **opening verse** as the processing-log identity, whether or not a title precedes it. For every user-facing reference, including the deck proposal's `Poem` tables, typo decisions and progress reports, show the title when one exists and is unique. If a title repeats, show `Title (opening verse)` to distinguish its poems; for example, `To My Brother George (Many the wonders I this day have seen;)`. For an untitled poem, show its opening verse. Keep the supplied capitalization and punctuation. Do not replace the exact opening-verse identity in the log with this display label. If two opening verses are identical, resolve their identity with the user before logging them; do not use line numbers or silently collapse them. If a single header line appears to be a title rather than verse, verify the full poem and ask about the missing opening verse before processing that record. Do not invent a verse line or silently change its identity.

The unheaded `Words:`/`Visuals:`/`Moods:` groups at the end of the current file are placeholders, not poem records. Leave them untouched and out of processing proposals until a title or opening verse identifies each intended poem. Do not attach their entries to the preceding poem.

`Words:`, `Visuals:`, `Moods:` and the existing singular `Mood:` delimit sections. Every non-empty line under Words is one submitted vocabulary entry, even if it contains commas or semicolons. Every non-empty line under Visuals is a selected image keyword, not a vocabulary entry. Moods and other metadata are not vocabulary. Stop each section at the next label or poem block. An empty Words or Visuals section is valid; do not fabricate entries. Preserve labels and other metadata, including the existing `Mood:` spelling, when normalizing only approved records.

A poem title or part of it may intentionally appear in Words and remains a submitted entry. A poem may also have a prefatory quotation; Words may select a phrase from that quotation. Include titles and prefatory quotations when checking the full source, and do not flag an entry merely because it is outside the verse body.

## Vocabulary and visuals

Follow the common source-checked typo audit and wait for decisions on suspected corrections. Preserve Keats's contractions, apostrophes, historical forms and the user's submitted inflections unless a correction is approved. Normalize only the approved records' Words capitalization, Visuals labels and Moods values under the common rules; keep titles, opening verses and other metadata unchanged.

Keats routinely omits an `e` and uses an apostrophe in shortened words. This convention is understood; do not explain it anywhere in Anki note fields.

Search the whole Anki collection for each vocabulary identifier. Reuse a suitable note in any deck and enrich it in place only when an important meaning is missing. Never move an existing card; the approved deck applies to new cards only. Use the common rules for independent Anki explanations and examples, excerpts, extraction, aligned English/Czech senses and read-back verification.

Only submitted Visuals keywords select image sets. Match each to the closest vocabulary entry in the same poem, including relevant extracted entries, and report genuine gaps or ambiguity. Use prefix `jk-` and the local [image_sources.md](../image_sources.md). The selected keyword determines a new basename; the matched vocabulary entry determines only the note to receive it. Reuse resolved same-meaning sets from this poet's index. Produce and index approved new sets even when a matching note already has a different non-empty Visual basename; preserve that existing Anki value. Follow the common images-last order.

Use [processing_log.md](../processing_log.md) for opening-verse/deck mappings and status. [reconciliation.md](../reconciliation.md) contains only active unresolved conflicts and stays completely empty when none remain.
