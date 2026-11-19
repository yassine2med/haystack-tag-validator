"""Command line entry: python -m haystack_validator FILE.csv"""

import sys

from .validator import validate_file


def main(argv: list[str] | None = None) -> int:
    """Print every issue; return 0 when clean, 1 when issues exist, 2 on bad usage."""
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python -m haystack_validator FILE.csv", file=sys.stderr)
        return 2
    try:
        issues = validate_file(args[0])
    except OSError as err:
        print(f"cannot read file: {err}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    print(f"{len(issues)} issue(s) found")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
