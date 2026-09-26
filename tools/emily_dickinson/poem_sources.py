"""List ED poems by fascicle and verify complete local source coverage."""

import argparse
import json
from pathlib import Path
import re

from tools.common.source_pages import archive_pages, validate_manifest


HEADING = re.compile(r"^(\d+),(\d+),(\d+) - .+$")


def roman(number):
    result = ""
    for value, symbol in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
                          (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
                          (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while number >= value:
            result += symbol
            number -= value
    return result


def scope_headings(src, fascicle, selected=None):
    if fascicle < 1:
        raise ValueError("Fascicle must be positive")
    headings = [line for line in Path(src).read_text().splitlines()
                if (match := HEADING.fullmatch(line)) and int(match.group(1)) == fascicle]
    if not headings or len(headings) != len(set(headings)):
        raise ValueError("Fascicle has no headings or contains duplicates")
    if selected is not None:
        if not isinstance(selected, list) or not selected or len(selected) != len(set(selected)):
            raise ValueError("Selected headings must be a non-empty, unique JSON array")
        if set(selected) - set(headings):
            raise ValueError("Selected headings contain a poem outside this fascicle")
        headings = [heading for heading in headings if heading in selected]
    return headings


def require_complete_scope(headings, items):
    validate_manifest(items)
    if [item["heading"] for item in items] != headings:
        raise ValueError("Manifest must contain every selected poem, exactly once, in source order")


def compare_log(headings, log, fascicle):
    """Compare exact source identities with logged identities; never infer completion."""
    logged = [line for line in Path(log).read_text().splitlines()
              if (match := HEADING.fullmatch(line)) and int(match.group(1)) == fascicle]
    if len(logged) != len(set(logged)):
        raise ValueError("Processing log contains duplicate headings for this fascicle")
    source_set, log_set = set(headings), set(logged)
    source_only = [heading for heading in headings if heading not in log_set]
    log_only = [heading for heading in logged if heading not in source_set]
    by_title = {}
    for heading in log_only:
        by_title.setdefault(heading.split(" - ", 1)[1], []).append(heading)
    shifted = [(old, heading) for heading in source_only
               for old in by_title.get(heading.split(" - ", 1)[1], [])]
    return source_only, log_only, shifted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "status", "template", "fetch"))
    parser.add_argument("--src", type=Path, default=Path("emily_dickinson/src.txt"))
    parser.add_argument("--log", type=Path, default=Path("emily_dickinson/processing_log.md"))
    parser.add_argument("--fascicle", type=int, required=True)
    parser.add_argument("--selected", type=Path, help="Optional JSON array of approved headings")
    parser.add_argument("--manifest", type=Path, help="Completed source manifest for fetch")
    parser.add_argument("--output", type=Path, help="New template file or local archive directory")
    args = parser.parse_args()
    try:
        if args.command == "status" and args.selected:
            raise ValueError("status compares the whole fascicle; omit --selected")
        selected = json.loads(args.selected.read_text()) if args.selected else None
        headings = scope_headings(args.src, args.fascicle, selected)
        if args.command == "plan":
            print(f"Emily Dickinson::{args.fascicle:02d} Fascicle {roman(args.fascicle)}\n")
            print("| Poem |\n|---|")
            for heading in headings:
                print(f"| {heading.replace('|', '&#124;')} |")
        elif args.command == "status":
            source_only, log_only, shifted = compare_log(headings, args.log, args.fascicle)
            print(f"Source-only: {len(source_only)}; log-only: {len(log_only)}; matching titles at changed numbers: {len(shifted)}")
            for heading in source_only:
                print(f"SOURCE ONLY {heading}")
            for heading in log_only:
                print(f"LOG ONLY {heading}")
            for old, new in shifted:
                print(f"POSSIBLE RENUMBER {old} -> {new}")
        elif args.command == "template":
            if args.output is None:
                raise ValueError("--output is required for template")
            items = [{"heading": heading, "url": "", "edition": ""} for heading in headings]
            with args.output.open("x") as file:
                json.dump(items, file, ensure_ascii=False, indent=2)
                file.write("\n")
            print(f"Wrote {len(items)} poem slots to {args.output}")
        else:
            if args.manifest is None or args.output is None:
                raise ValueError("--manifest and --output are required for fetch")
            items = json.loads(args.manifest.read_text())
            require_complete_scope(headings, items)
            results = archive_pages(items, args.output)
            for result in results:
                print(f"{result['heading']}: {result['state']}; "
                      f"{'first line found' if result['match_found'] else 'IDENTITY NEEDS REVIEW'}; {result['text']}")
            print(f"{len(results)} local texts; {sum(not r['match_found'] for r in results)} identity warnings")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
